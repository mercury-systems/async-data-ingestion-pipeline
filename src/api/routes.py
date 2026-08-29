"""API routes."""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks

from src.models.data import (
    IngestionRequest, IngestionResponse,
    BatchIngestionRequest, BatchIngestionResponse,
    JobStatusResponse, MetricsResponse, DeadLetterItem,
)
from src.services.ingestion import IngestionService
from src.services.batch_processor import BatchProcessor
from src.services.job_store import JobStore
from src.services.metrics import Metrics
from src.core.circuit_breaker import CircuitBreaker

router = APIRouter()

_job_store = JobStore()
_metrics = Metrics()
_circuit_breaker = CircuitBreaker()


def get_ingestion_service() -> IngestionService:
    return IngestionService(metrics=_metrics, circuit_breaker=_circuit_breaker)


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_single(
    request: IngestionRequest,
    service: IngestionService = Depends(get_ingestion_service)
):
    return await service.ingest_data(url=request.url, params=request.params)


@router.post("/ingest/batch", response_model=BatchIngestionResponse)
async def ingest_batch(
    request: BatchIngestionRequest,
    background_tasks: BackgroundTasks,
):
    job_id = _job_store.create_job(total=len(request.urls))
    processor = BatchProcessor(
        job_store=_job_store,
        metrics=_metrics,
        circuit_breaker=_circuit_breaker,
    )
    background_tasks.add_task(processor.process, job_id, request.urls, request.params)

    return BatchIngestionResponse(
        job_id=job_id,
        status="pending",
        total=len(request.urls),
        pending=len(request.urls),
        created_at=str(_job_store.get_job(job_id)["created_at"]),
    )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    job = _job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        total=job["total"],
        completed=job["completed"],
        failed=job["failed"],
        pending=job["pending"],
        results=job["results"],
        created_at=str(job["created_at"]),
        updated_at=str(job["updated_at"]),
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    metrics = _metrics.get()
    return MetricsResponse(
        total_requests=metrics["total_requests"],
        successful_requests=metrics["successful_requests"],
        failed_requests=metrics["failed_requests"],
        avg_latency_ms=metrics["avg_latency_ms"],
        active_jobs=_job_store.active_jobs(),
        circuit_breakers=_circuit_breaker.get_states(),
        dead_letter_count=_job_store.dead_letter_count(),
    )


@router.get("/dead-letter", response_model=list[DeadLetterItem])
async def get_dead_letter(limit: int = 50):
    items = _job_store.get_dead_letter(limit=limit)
    return [DeadLetterItem(**item) for item in items]
