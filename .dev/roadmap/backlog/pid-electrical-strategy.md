# P&ID & Electrical Drawings - Updated Strategy

**Updated:** 2025-11-22  
**Focus:** Minimize AI dependency, DWG native, Professional output

---

## 🎯 Updated Requirements

1. ✅ **No AI dependency for core features** (YOLO v8 + OpenCV)
2. ✅ **DWG output** (not just PDF)
3. ✅ **Professional quality** (Plant 3D / AutoCAD Electrical level)
4. ✅ **Leverage existing licenses** (Plant 3D, AutoCAD Electrical)
5. ✅ **Opensource alternatives** when possible
6. ✅ **Self-hosted** (Proxmox + Docker)

---

## 📥 P&ID Ingestion: YOLO v8 + OpenCV (Opensource)

### Technology Stack

**Symbol Detection:**
- **YOLO v8** (Ultralytics, AGPL-3.0)
- Train on P&ID symbols (pumps, motors, valves, instruments)
- 80-90% accuracy with good training data

**Text Extraction (OCR):**
- **EasyOCR** (Apache 2.0) - Better than Tesseract for technical drawings
- Extract tag numbers, specs

**Line Detection:**
- **OpenCV** (Apache 2.0)
- Hough Line Transform for pipe/signal lines
- Contour detection for connections

**Deployment:**
- Docker container with GPU support (NVIDIA CUDA)
- Self-hosted on Proxmox
- No external API dependencies

### Implementation

```python
# backend/app/services/pid_ingestion.py
from ultralytics import YOLO
import cv2
import easyocr
import numpy as np

class PIDIngestionService:
    def __init__(self):
        # Load trained YOLO model
        self.model = YOLO('models/pid_symbols_v8.pt')
        self.ocr_reader = easyocr.Reader(['en'])
    
    def ingest_pid_pdf(self, pdf_path: str) -> List[Asset]:
        # Convert PDF to images
        images = convert_pdf_to_images(pdf_path, dpi=300)
        
        all_assets = []
        
        for page_num, image in enumerate(images):
            # Step 1: Detect symbols with YOLO
            results = self.model.predict(image, conf=0.7)
            
            # Step 2: Extract text with OCR
            ocr_results = self.ocr_reader.readtext(image)
            
            # Step 3: Match OCR text to symbols (proximity)
            assets = self._match_symbols_to_text(results, ocr_results)
            
            # Step 4: Detect connections (lines)
            connections = self._detect_connections(image, assets)
            
            # Step 5: Create database objects
            for asset_data in assets:
                asset = create_asset_from_pid(asset_data)
                all_assets.append(asset)
            
            for conn in connections:
                create_cable(conn['from'], conn['to'])
        
        return all_assets
    
    def _detect_connections(self, image, assets):
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect lines (Hough Transform)
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 
                                minLineLength=50, maxLineGap=10)
        
        connections = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # Find equipment at endpoints
            from_asset = self._find_asset_at_point((x1, y1), assets)
            to_asset = self._find_asset_at_point((x2, y2), assets)
            
            if from_asset and to_asset:
                connections.append({
                    'from': from_asset,
                    'to': to_asset,
                    'type': self._infer_connection_type(line)
                })
        
        return connections
```

### Training YOLO Model

**Required:**
- Training dataset: ~500-1000 labeled P&ID images
- Labels: PUMP, MOTOR, VALVE, INSTRUMENT, TANK, etc.
- Tool: LabelImg or Roboflow

**Training time:** 2-4 hours on GPU  
**Inference:** <1 second per page

**Alternative:** Pre-trained model (if available) + fine-tuning

---

## 📤 P&ID Generation: DWG Native Output

### Option 1: Plant 3D Automation (Recommended - You Have License)

**Advantages:**
- ✅ Professional quality output
- ✅ Native DWG format
- ✅ Industry standard symbols
- ✅ You already own license

**Technology:**
- **Plant 3D API** (.NET/Python.NET)
- **pyautocad** (Python library for AutoCAD)
- **COM automation**

**Deployment Challenge:**
- Plant 3D requires Windows
- Docker on Linux won't work
- **Solution:** Windows VM in Proxmox OR Windows Docker container

**Implementation:**

```python
# backend/app/services/plant3d_generator.py
import win32com.client
from typing import List

class Plant3DGenerator:
    def __init__(self):
        # Connect to AutoCAD Plant 3D
        self.acad = win32com.client.Dispatch("AutoCAD.Application")
        self.doc = self.acad.Documents.Add()
    
    def generate_pid(self, assets: List[Asset], output_path: str):
        # Set up drawing
        modelspace = self.doc.ModelSpace
        
        # Place equipment symbols
        for asset in assets:
            # Get Plant 3D block for asset type
            block_name = self._get_plant3d_block(asset.type)
            
            # Insert block
            insertion_point = self._calculate_position(asset)
            block_ref = modelspace.InsertBlock(
                insertion_point,
                block_name,
                1.0, 1.0, 1.0,  # Scale
                0  # Rotation
            )
            
            # Set attributes (tag, description, etc.)
            for attrib in block_ref.GetAttributes():
                if attrib.TagString == "TAG":
                    attrib.TextString = asset.tag
                elif attrib.TagString == "DESC":
                    attrib.TextString = asset.description
            
            # Update attributes
            block_ref.Update()
        
        # Draw connections (pipes/signals)
        for cable in get_cables(assets):
            from_point = self._get_connection_point(cable.from_asset)
            to_point = self._get_connection_point(cable.to_asset)
            
            # Draw line
            modelspace.AddLine(from_point, to_point)
        
        # Save as DWG
        self.doc.SaveAs(output_path)
        self.doc.Close()
    
    def _get_plant3d_block(self, asset_type: str) -> str:
        # Map SYNAPSE types to Plant 3D block names
        mapping = {
            "PUMP": "P3D_PUMP_CENTRIFUGAL",
            "MOTOR": "P3D_MOTOR",
            "VALVE": "P3D_VALVE_GATE",
            "TANK": "P3D_TANK_VERTICAL",
            # ... more mappings
        }
        return mapping.get(asset_type, "P3D_GENERIC")
```

**Docker Deployment (Windows Container):**

```dockerfile
# Dockerfile.plant3d (Windows container)
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Install Plant 3D (requires license server accessible)
# This assumes Plant 3D is already installed on base image
# Or use silent install

# Install Python
RUN choco install python -y

# Copy application
COPY backend /app

# Install dependencies
RUN pip install pywin32 pyautocad

CMD ["python", "main.py"]
```

**Proxmox Setup:**
- Create Windows VM
- Install Plant 3D
- Run Docker Windows containers OR
- Direct Python service (FastAPI on Windows)

---

### Option 2: ezdxf (Opensource DWG Generator)

**If you want fully opensource alternative:**

**Technology:**
- **ezdxf** (MIT license)
- Generate DXF/DWG programmatically
- No AutoCAD required

**Quality:** 
- ✅ Valid DWG format
- ✅ Opens in AutoCAD
- ⚠️ Custom symbols (not Plant 3D library)
- ⚠️ Manual symbol creation required

**Implementation:**

```python
# backend/app/services/ezdxf_generator.py
import ezdxf
from ezdxf.enums import TextEntityAlignment

class EzdxfGenerator:
    def __init__(self, symbol_library_path: str):
        self.symbol_library = self._load_symbol_library(symbol_library_path)
    
    def generate_pid(self, assets: List[Asset], output_path: str):
        # Create new DXF document
        doc = ezdxf.new('R2018')  # AutoCAD 2018 format
        msp = doc.modelspace()
        
        # Define layers
        doc.layers.add(name='EQUIPMENT', color=7)  # White
        doc.layers.add(name='PIPING', color=3)     # Green
        doc.layers.add(name='TEXT', color=1)       # Red
        
        # Place equipment
        for asset in assets:
            x, y = self._calculate_position(asset)
            
            # Insert block (symbol)
            block_name = f"SYMBOL_{asset.type}"
            if block_name in self.symbol_library:
                msp.add_blockref(
                    block_name,
                    insert=(x, y),
                    dxfattribs={'layer': 'EQUIPMENT'}
                )
            
            # Add tag text
            msp.add_text(
                asset.tag,
                dxfattribs={
                    'layer': 'TEXT',
                    'height': 2.5,
                    'style': 'Arial'
                }
            ).set_placement((x, y - 5), align=TextEntityAlignment.CENTER)
        
        # Draw connections
        for cable in get_cables(assets):
            from_point = self._get_point(cable.from_asset)
            to_point = self._get_point(cable.to_asset)
            
            msp.add_line(
                from_point,
                to_point,
                dxfattribs={'layer': 'PIPING', 'lineweight': 35}
            )
        
        # Save as DWG
        doc.saveas(output_path)
    
    def _load_symbol_library(self, path: str):
        # Load DXF blocks from library file
        symbol_doc = ezdxf.readfile(path)
        return {block.name: block for block in symbol_doc.blocks}
```

**Symbol Library Creation:**
1. Create DXF file with all symbols as blocks
2. Use libre tools (QCAD, LibreCAD) or AutoCAD
3. Store as `symbols/pid_library.dxf`

---

### SVG vs DWG Quality Comparison

| Aspect | SVG | DWG (Plant 3D) | DWG (ezdxf) |
|--------|-----|----------------|-------------|
| **Native CAD** | ❌ No | ✅ Yes | ✅ Yes |
| **Editable in AutoCAD** | ❌ No | ✅ Yes | ✅ Yes |
| **Industry Standard** | ❌ No | ✅ Yes | ✅ Yes |
| **Symbol Quality** | ⚠️ Custom | ✅ Professional | ⚠️ Custom |
| **Line types** | ⚠️ Limited | ✅ All types | ✅ All types |
| **Scale** | ❌ No | ✅ Engineering scale | ✅ Engineering scale |
| **Layers** | ❌ No | ✅ Yes | ✅ Yes |
| **Attributes** | ❌ No | ✅ Yes | ✅ Yes |
| **Print quality** | ⚠️ Good | ✅ Excellent | ✅ Excellent |

**Verdict:** DWG (Plant 3D or ezdxf) >> SVG for professional engineering

**SVG to DWG conversion:** Not recommended (loss of CAD data)

---

## ⚡ Electrical Diagrams: AutoCAD Electrical Automation

### Option 1: AutoCAD Electrical Automation (You Have License)

**Similar to Plant 3D approach:**

```python
# backend/app/services/acad_electrical_generator.py
import win32com.client

class AutoCADElectricalGenerator:
    def __init__(self):
        self.acad = win32com.client.Dispatch("AutoCAD.Application")
    
    def generate_single_line(self, motors: List[Asset], output_path: str):
        doc = self.acad.Documents.Add("acad_electrical.dwt")
        msp = doc.ModelSpace
        
        y_offset = 0
        
        for motor in motors:
            # Insert motor symbol
            motor_block = msp.InsertBlock(
                (10, y_offset),
                "ACE_MOTOR_3PHASE",  # AutoCAD Electrical block
                1, 1, 1, 0
            )
            
            # Set attributes
            for attr in motor_block.GetAttributes():
                if attr.TagString == "TAG":
                    attr.TextString = motor.tag
                elif attr.TagString == "HP":
                    attr.TextString = str(motor.hp)
            
            # Insert VFD if exists
            vfd = get_vfd_for_motor(motor)
            if vfd:
                vfd_block = msp.InsertBlock(
                    (30, y_offset),
                    "ACE_VFD",
                    1, 1, 1, 0
                )
                # Connect with wire
                msp.AddLine((20, y_offset), (30, y_offset))
            
            y_offset -= 15  # Next row
        
        doc.SaveAs(output_path)
```

---

### Option 2: QElectroTech (Opensource Alternative)

**Technology:**
- **QElectroTech** (GPL-2.0)
- Professional electrical diagrams
- Export DXF/PDF
- Cross-platform (Linux/Windows)

**Quality:**
- ⚠️ Good but not AutoCAD Electrical level
- ✅ Industry-acceptable for most projects
- ✅ Extensive symbol library

**Can run in Docker:**

```dockerfile
# Dockerfile.qelectrotech
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    qelectrotech \
    xvfb \
    python3-pip

# Headless display for automation
ENV DISPLAY=:99

COPY backend /app
WORKDIR /app

CMD ["python3", "qet_service.py"]
```

**Implementation:**

```python
# backend/app/services/qet_generator.py
import subprocess

class QElectroTechGenerator:
    def generate_diagram(self, assets: List[Asset], output_path: str):
        # Generate QET project file (XML)
        qet_xml = self._generate_qet_xml(assets)
        
        # Write to temp file
        with open('/tmp/diagram.qet', 'w') as f:
            f.write(qet_xml)
        
        # Call QET CLI to render
        subprocess.run([
            'qelectrotech',
            '--headless',
            '--export-dxf', output_path,
            '/tmp/diagram.qet'
        ])
```

---

## 🐋 Docker Deployment Architecture (Proxmox)

### Recommended Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  # PostgreSQL database
  db:
    image: postgres:16
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - synapse_network
  
  # Redis cache
  redis:
    image: redis:7-alpine
    networks:
      - synapse_network
  
  # Backend (FastAPI)
  backend:
    build: ./backend
    depends_on:
      - db
      - redis
      - yolo_service
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/synapse
      - REDIS_URL=redis://redis:6379
      - YOLO_SERVICE_URL=http://yolo_service:8001
    networks:
      - synapse_network
  
  # YOLO P&ID Ingestion Service (GPU)
  yolo_service:
    build: ./services/yolo_pid
    runtime: nvidia  # GPU support
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    volumes:
      - ./models:/models
    networks:
      - synapse_network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  # Frontend
  frontend:
    build: .
    ports:
      - "3000:80"
    networks:
      - synapse_network
  
  # Adminer (DB viewer)
  adminer:
    image: adminer
    ports:
      - "8080:8080"
    networks:
      - synapse_network

volumes:
  postgres_data:

networks:
  synapse_network:
    driver: bridge
```

### For Plant 3D / AutoCAD Electrical

**Option A: Windows VM in Proxmox**
- Create Windows Server VM
- Install Plant 3D / AutoCAD Electrical
- Install Python + FastAPI service
- Expose API endpoint to Linux containers
- Call from main backend via HTTP

**Option B: Windows Container (if supported)**
- Use Windows Server Core container
- More complex but isolated

**Recommendation:** Windows VM (simpler licensing, easier setup)

---

## 📊 Final Technology Decision Matrix

| Feature | Opensource | Commercial (You Own) | Recommended |
|---------|------------|----------------------|-------------|
| **P&ID Ingestion** | YOLO v8 + OpenCV | - | ✅ YOLO v8 |
| **P&ID Generation** | ezdxf | Plant 3D API | ⭐ Plant 3D (quality) |
| **P&ID Alt** | ezdxf | - | ✅ ezdxf (backup) |
| **Electrical Gen** | QElectroTech | AutoCAD Elec API | ⭐ AutoCAD Elec |
| **Electrical Alt** | QElectroTech | - | ✅ QElectroTech |
| **Deployment** | Docker + Linux | Windows VM | ✅ Hybrid |

---

## 🎯 Recommended Architecture

```
PROXMOX SERVER
├─ Linux VM (Docker Compose)
│  ├─ PostgreSQL
│  ├─ Redis
│  ├─ Backend (FastAPI)
│  ├─ Frontend (React)
│  └─ YOLO Service (GPU)
│
└─ Windows VM (CAD Services)
   ├─ Plant 3D Service (Python + FastAPI)
   ├─ AutoCAD Electrical Service
   └─ Expose APIs to Linux containers
```

**Communication:**
- Linux containers → HTTP requests → Windows VM
- Windows VM generates DWG → Saves to shared volume
- Linux containers serve DWG to users

---

## ✅ Summary

**Ingestion:** YOLO v8 + OpenCV (100% opensource, no AI cloud)  
**Generation:** Plant 3D + AutoCAD Elec (you own licenses, best quality)  
**Backup:** ezdxf + QElectroTech (opensource alternatives)  
**Format:** Native DWG (not SVG)  
**Deployment:** Proxmox (Linux + Windows VMs)  

**Best of both worlds: Leverage your licenses + Opensource fallbacks**
