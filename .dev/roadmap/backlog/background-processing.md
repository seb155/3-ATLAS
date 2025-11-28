# Background Processing

**Version:** v0.4.0  
**Goal:** Async processing for large imports and long-running operations

---

## Overview

SYNAPSE uses **Celery + Redis** for background job processing:

**Use Cases:**
- Large CSV imports (1K-5K rows)
- Package generation (500+ pages)
- Batch rule execution (1000+ assets)
- Scheduled backups
- Scheduled reports

**Benefits:**
- ✅ Non-blocking - API responds immediately
- ✅ Progress tracking - Real-time updates via WebSocket
- ✅ Retry logic - Auto-retry failed jobs
- ✅ Scheduled jobs - Cron-like scheduling
- ✅ Priority queues - Urgent jobs first

---

## Architecture

```
┌─────────────┐                 ┌─────────────┐                 ┌─────────────┐
│  Frontend   │                 │   Backend   │                 │   Celery    │
│    (React)  │                 │  (FastAPI)  │                 │   Worker    │
└──────┬──────┘                 └──────┬──────┘                 └──────┬──────┘
       │                                │                                │
       │ 1. Upload CSV (3000 rows)      │                                │
       │───────────────────────────────▶│                                │
       │                                │                                │
       │ 2. Returns job_id immediately  │                                │
       │◀───────────────────────────────│                                │
       │                                │                                │
       │                                │ 3. Queue job (Redis)           │
       │                                │───────────────────────────────▶│
       │                                │                                │
       │                                │                                │ 4. Process
       │                                │                                │    async
       │                                │                                │
       │ 5. WebSocket: Progress 25%     │◀───────────────────────────────│
       │◀───────────────────────────────│                                │
       │                                │                                │
       │ 6. WebSocket: Progress 50%     │◀───────────────────────────────│
       │◀───────────────────────────────│                                │
       │                                │                                │
       │ 7. WebSocket: Complete         │◀───────────────────────────────│
       │◀───────────────────────────────│                                │
       │                                │                                │
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Task Queue | **Celery** | Python async task framework |
| Broker | **Redis** | Message queue |
| Result Backend | **Redis** | Store task results |
| Scheduler | **Celery Beat** | Cron-like scheduling |
| Monitoring | **Flower** (optional) | Web UI for Celery |

---

## Docker Setup

```yaml
# workspace/docker-compose.yml

services:
  redis:
    image: redis:7-alpine
    container_name: forge-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - forge-network

  celery-worker:
    build: ./apps/synapse/backend
    container_name: synapse-celery-worker
    command: celery -A app.celery_app worker --loglevel=info
    volumes:
      - ./apps/synapse/backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@forge-postgres:5432/synapse
      - REDIS_URL=redis://forge-redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - forge-network

  celery-beat:
    build: ./apps/synapse/backend
    container_name: synapse-celery-beat
    command: celery -A app.celery_app beat --loglevel=info
    volumes:
      - ./apps/synapse/backend:/app
    environment:
      - DATABASE_URL=postgresql://user:pass@forge-postgres:5432/synapse
      - REDIS_URL=redis://forge-redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - forge-network

  flower:
    build: ./apps/synapse/backend
    container_name: synapse-flower
    command: celery -A app.celery_app flower
    ports:
      - "5555:5555"
    environment:
      - REDIS_URL=redis://forge-redis:6379/0
    depends_on:
      - redis
      - celery-worker
    networks:
      - forge-network

volumes:
  redis_data:
```

---

## Backend Implementation

### Celery App Setup

```python
# apps/synapse/backend/app/celery_app.py

from celery import Celery
from celery.schedules import crontab
import os

celery_app = Celery(
    "synapse",
    broker=os.getenv("REDIS_URL", "redis://forge-redis:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://forge-redis:6379/0"),
    include=["app.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/New_York",
    enable_utc=True,
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    result_expires=3600,  # 1 hour
)

# Scheduled tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "daily-backup": {
        "task": "app.tasks.backup_database",
        "schedule": crontab(hour=2, minute=0),  # 2:00 AM daily
    },
    "weekly-report": {
        "task": "app.tasks.generate_weekly_report",
        "schedule": crontab(day_of_week=1, hour=8, minute=0),  # Monday 8:00 AM
    },
}
```

### Task Definition

```python
# apps/synapse/backend/app/tasks.py

from celery import Task
from app.celery_app import celery_app
from app.services.websocket_logger import WebSocketLogger
import time

class ProgressTask(Task):
    """Base task with progress tracking"""
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress via WebSocket"""
        percent = int((current / total) * 100)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": current,
                "total": total,
                "percent": percent,
                "message": message
            }
        )
        
        # Broadcast via WebSocket
        WebSocketLogger.log(
            level="INFO",
            message=f"[{self.request.id}] {message} ({percent}%)",
            source="CELERY",
            action_type="PROGRESS",
            context={
                "task_id": self.request.id,
                "percent": percent,
                "current": current,
                "total": total
            }
        )

@celery_app.task(base=ProgressTask, bind=True)
def import_csv_assets(self, project_id: str, file_path: str):
    """
    Import assets from CSV file
    
    Args:
        self: Task instance (injected by bind=True)
        project_id: Project UUID
        file_path: Path to CSV file
    """
    import pandas as pd
    from app.models import Asset
    from app.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # 1. Load CSV
        self.update_progress(0, 100, "Loading CSV file...")
        df = pd.read_csv(file_path)
        total_rows = len(df)
        
        # 2. Validate rows
        self.update_progress(25, 100, f"Validating {total_rows} rows...")
        errors = []
        for idx, row in df.iterrows():
            if not row.get("tag"):
                errors.append(f"Row {idx}: Missing tag")
        
        if errors:
            raise ValueError(f"Validation failed: {errors}")
        
        # 3. Create assets
        created_count = 0
        for idx, row in df.iterrows():
            asset = Asset(
                project_id=project_id,
                tag=row["tag"],
                type=row["type"],
                properties=row.to_dict()
            )
            db.add(asset)
            created_count += 1
            
            # Update progress every 10 assets
            if created_count % 10 == 0:
                percent = 25 + int((created_count / total_rows) * 50)
                self.update_progress(
                    percent, 
                    100,
                    f"Created {created_count}/{total_rows} assets..."
                )
        
        db.commit()
        
        # 4. Run rules
        self.update_progress(75, 100, "Applying rules...")
        # ... rule execution logic
        
        # 5. Complete
        self.update_progress(100, 100, f"Import complete: {created_count} assets created")
        
        return {
            "status": "SUCCESS",
            "created_count": created_count,
            "total_rows": total_rows
        }
        
    except Exception as e:
        self.update_progress(0, 100, f"Error: {str(e)}")
        raise
    finally:
        db.close()

@celery_app.task(base=ProgressTask, bind=True)
def generate_package(self, project_id: str, package_type: str, options: dict):
    """Generate engineering package (Excel/PDF)"""
    from app.services.package_generator import PackageGenerator
    
    try:
        self.update_progress(0, 100, "Fetching data...")
        generator = PackageGenerator(project_id, package_type)
        
        self.update_progress(25, 100, "Generating Excel...")
        excel_file = generator.generate_excel(options)
        
        if "pdf" in options.get("formats", []):
            self.update_progress(75, 100, "Generating PDF...")
            pdf_file = generator.generate_pdf(options)
        
        self.update_progress(100, 100, "Package generation complete")
        
        return {
            "status": "SUCCESS",
            "files": [excel_file, pdf_file] if pdf_file else [excel_file]
        }
    except Exception as e:
        self.update_progress(0, 100, f"Error: {str(e)}")
        raise

@celery_app.task
def backup_database():
    """Scheduled database backup (runs daily at 2 AM)"""
    import subprocess
    import datetime
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/backups/synapse_{timestamp}.sql"
    
    subprocess.run([
        "pg_dump",
        "-h", "forge-postgres",
        "-U", "user",
        "-d", "synapse",
        "-f", backup_file
    ])
    
    WebSocketLogger.log(
        level="INFO",
        message=f"Database backup complete: {backup_file}",
        source="CELERY",
        action_type="BACKUP"
    )
    
    return {"backup_file": backup_file}

@celery_app.task
def generate_weekly_report():
    """Scheduled weekly report (runs Monday 8 AM)"""
    # ... report generation logic
    pass
```

---

## API Integration

```python
# apps/synapse/backend/app/routers/ingestion.py

from fastapi import APIRouter, UploadFile, BackgroundTasks
from app.tasks import import_csv_assets

router = APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])

@router.post("/upload-csv")
async def upload_csv(
    project_id: UUID,
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    """Upload CSV and queue import job"""
    
    # Save uploaded file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Queue Celery task
    task = import_csv_assets.delay(str(project_id), file_path)
    
    return {
        "job_id": task.id,
        "status": "QUEUED",
        "message": "Import queued, check status via WebSocket"
    }

@router.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    """Get task status"""
    from celery.result import AsyncResult
    
    task = AsyncResult(job_id, app=celery_app)
    
    if task.state == "PENDING":
        return {"status": "PENDING", "percent": 0}
    elif task.state == "PROGRESS":
        return {
            "status": "PROGRESS",
            "percent": task.info.get("percent", 0),
            "message": task.info.get("message", "")
        }
    elif task.state == "SUCCESS":
        return {
            "status": "SUCCESS",
            "result": task.result
        }
    elif task.state == "FAILURE":
        return {
            "status": "FAILURE",
            "error": str(task.info)
        }
    else:
        return {"status": task.state}
```

---

## Frontend Integration

```typescript
// apps/synapse/frontend/src/services/jobService.ts

export interface JobStatus {
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  percent?: number;
  message?: string;
  result?: any;
  error?: string;
}

export class JobService {
  static async uploadCSV(
    projectId: string, 
    file: File
  ): Promise<{job_id: string}> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_id', projectId);
    
    const response = await fetch('/api/v1/ingestion/upload-csv', {
      method: 'POST',
      body: formData
    });
    
    return response.json();
  }
  
  static async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`/api/v1/ingestion/job-status/${jobId}`);
    return response.json();
  }
}

// apps/synapse/frontend/src/components/CSVUpload.tsx

import React, { useState } from 'react';
import { JobService } from '../services/jobService';
import { useWebSocket } from '../hooks/useWebSocket';

export function CSVUpload() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  
  const { lastLog } = useWebSocket();
  
  // Listen for progress updates via WebSocket
  React.useEffect(() => {
    if (lastLog?.context?.task_id === jobId) {
      setProgress(lastLog.context.percent);
      setMessage(lastLog.message);
    }
  }, [lastLog, jobId]);
  
  const handleUpload = async (file: File) => {
    const { job_id } = await JobService.uploadCSV(projectId, file);
    setJobId(job_id);
    setMessage('Import queued...');
  };
  
  return (
    <div>
      <input type="file" onChange={(e) => handleUpload(e.target.files[0])} />
      
      {jobId && (
        <div className="progress-bar">
          <div style={{width: `${progress}%`}} />
          <span>{message} ({progress}%)</span>
        </div>
      )}
    </div>
  );
}
```

---

## Job Queue UI (Admin)

```
┌─ Job Queue ─────────────────────────────────────────────────┐
│                                                              │
│  Filter: [All ▼] [Last 24h ▼]                               │
│                                                              │
│  RUNNING (2)                                                 │
│  ├─ import_csv_assets                                        │
│  │  Job ID: abc-123                                          │
│  │  Progress: ████████░░ 75% (2,250/3,000 rows)             │
│  │  Started: 2 minutes ago                                   │
│  │  [View Logs] [Cancel]                                     │
│  │                                                           │
│  └─ generate_package                                         │
│     Job ID: def-456                                          │
│     Progress: ████░░░░░░ 40% (Generating Excel...)          │
│     Started: 30 seconds ago                                  │
│     [View Logs] [Cancel]                                     │
│                                                              │
│  QUEUED (1)                                                  │
│  └─ backup_database                                          │
│     Scheduled for: 2025-11-25 02:00                          │
│                                                              │
│  COMPLETED (5)                                               │
│  └─ import_csv_assets - Success (3,000 rows) - 5 min ago    │
│                                                              │
│  FAILED (1)                                                  │
│  └─ generate_package - Error: File not found - 1 hour ago   │
│     [Retry] [View Error]                                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Verification Plan

```bash
# Start services
docker-compose up redis celery-worker celery-beat

# Test import
curl -X POST http://localhost:8001/api/v1/ingestion/upload-csv \
  -F "file=@test_data.csv" \
  -F "project_id=proj-001"

# Check job status
curl http://localhost:8001/api/v1/ingestion/job-status/abc-123

# Monitor with Flower
http://localhost:5555
```

---

**Updated:** 2025-11-24
