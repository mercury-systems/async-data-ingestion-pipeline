"""Batch ingestion processor with background tasks."""

import asyncio
from typing import List, Dict, Any

from src.core.config import settings
from src.services.ingestion import IngestionService
from src.services.job_store import JobStore
from src.services.metrics import Metrics
from src.core.circuit_breaker import CircuitBreaker


class BatchProcessor:
    def __init__(self, job_store: JobStore, metrics: Metrics,
                 circuit_breaker: CircuitBreaker, ingestion_service: IngestionService = None):
        self.job_store = job_store
        self.metrics = metrics
        self.circuit = circuit_breaker
        self.ingestion = ingestion_service or IngestionService(
            metrics=metrics, circuit_breaker=circuit_breaker
        )

    async def process(self, job_id: str, urls: List[str], params: Dict[str, Any] = None):
        self.job_store.update_job(job_id, status="running")
        semaphore = asyncio.Semaphore(settings.batch_concurrency)
        results = []
        completed = 0
        failed = 0

        async def _fetch_one(url):
            async with semaphore:
                result = await self.ingestion.ingest_data(url, params)
                return {"url": url, "status_code": result.status_code,
                        "error": result.error, "latency_ms": result.latency_ms}

        tasks = [_fetch_one(url) for url in urls]
        for coro in asyncio.as_completed(tasks):
            result = await coro
            results.append(result)
            if result["error"]:
                failed += 1
                self.job_store.add_dead_letter(
                    job_id, result["url"], result["error"], result["status_code"]
                )
            else:
                completed += 1

        self.job_store.update_job(
            job_id,
            status="completed",
            completed=completed,
            failed=failed,
            pending=0,
            results=results,
        )
