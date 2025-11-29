"""
Job Engine

Queue-based job management for async task execution.
"""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import uuid
import logging

logger = logging.getLogger(__name__)


class JobPriority(int, Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 100


class JobStatus(str, Enum):
    """Job execution status."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


@dataclass
class Job:
    """Represents a job in the queue."""
    id: str
    task_id: str
    session_id: str
    priority: JobPriority
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retries: int = 0
    max_retries: int = 3
    timeout: int = 300  # seconds
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobEngine:
    """
    Manages job queue and execution.

    Features:
    - Priority-based queue
    - Retry logic
    - Timeout handling
    - Concurrent execution limits
    """

    def __init__(
        self,
        max_concurrent: int = 3,
        redis_url: Optional[str] = None
    ):
        self.max_concurrent = max_concurrent
        self.redis_url = redis_url
        self.jobs: Dict[str, Job] = {}
        self.queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.running: set = set()
        self._executor_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the job executor."""
        logger.info("Starting job engine")
        self._executor_task = asyncio.create_task(self._executor_loop())

    async def stop(self):
        """Stop the job executor."""
        logger.info("Stopping job engine")
        if self._executor_task:
            self._executor_task.cancel()
            try:
                await self._executor_task
            except asyncio.CancelledError:
                pass

    async def submit(
        self,
        task_id: str,
        session_id: str,
        executor: Callable,
        priority: JobPriority = JobPriority.NORMAL,
        **kwargs
    ) -> Job:
        """Submit a new job to the queue."""
        job = Job(
            id=str(uuid.uuid4()),
            task_id=task_id,
            session_id=session_id,
            priority=priority,
            status=JobStatus.QUEUED,
            created_at=datetime.utcnow(),
            metadata={"executor": executor, "kwargs": kwargs}
        )

        self.jobs[job.id] = job

        # Priority queue: lower number = higher priority (so we negate)
        await self.queue.put((-priority.value, job.id))

        logger.info(f"Job {job.id} submitted with priority {priority.name}")
        return job

    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    async def cancel(self, job_id: str) -> bool:
        """Cancel a job."""
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in [JobStatus.PENDING, JobStatus.QUEUED]:
            job.status = JobStatus.CANCELLED
            logger.info(f"Job {job_id} cancelled")
            return True

        return False

    async def _executor_loop(self):
        """Main executor loop processing jobs from queue."""
        while True:
            try:
                # Wait for a job if we're at capacity
                while len(self.running) >= self.max_concurrent:
                    await asyncio.sleep(0.1)

                # Get next job
                _, job_id = await self.queue.get()
                job = self.jobs.get(job_id)

                if not job or job.status == JobStatus.CANCELLED:
                    continue

                # Execute job
                self.running.add(job_id)
                asyncio.create_task(self._execute_job(job))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in executor loop: {e}")
                await asyncio.sleep(1)

    async def _execute_job(self, job: Job):
        """Execute a single job."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()

        try:
            executor = job.metadata["executor"]
            kwargs = job.metadata["kwargs"]

            # Execute with timeout
            result = await asyncio.wait_for(
                executor(**kwargs),
                timeout=job.timeout
            )

            job.status = JobStatus.COMPLETED
            job.result = result
            job.completed_at = datetime.utcnow()

            logger.info(f"Job {job.id} completed successfully")

        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error = f"Job timed out after {job.timeout}s"
            logger.error(f"Job {job.id} timed out")

        except Exception as e:
            if job.retries < job.max_retries:
                job.retries += 1
                job.status = JobStatus.RETRYING
                logger.warning(f"Job {job.id} failed, retry {job.retries}/{job.max_retries}")
                # Re-queue
                await self.queue.put((-job.priority.value, job.id))
            else:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.completed_at = datetime.utcnow()
                logger.error(f"Job {job.id} failed permanently: {e}")

        finally:
            self.running.discard(job.id)
