"""Tests for batch processor."""

import pytest
import httpx
from src.services.batch_processor import BatchProcessor
from src.services.job_store import JobStore
from src.services.metrics import Metrics
from src.core.circuit_breaker import CircuitBreaker


@pytest.mark.asyncio
async def test_batch_processing():
    store = JobStore(db_path=":memory:")
    metrics = Metrics()
    circuit = CircuitBreaker()

    def handler(request: httpx.Request):
        if "fail" in str(request.url):
            return httpx.Response(500)
        return httpx.Response(200, json={"ok": True})

    transport = httpx.MockTransport(handler)
    from src.services.ingestion import IngestionService
    service = IngestionService(transport=transport, metrics=metrics, circuit_breaker=circuit)
    processor = BatchProcessor(store, metrics, circuit, service)

    job_id = store.create_job(total=3)
    urls = [
        "https://ok.com/1",
        "https://fail.com/2",
        "https://ok.com/3",
    ]
    await processor.process(job_id, urls)

    job = store.get_job(job_id)
    assert job["status"] == "completed"
    assert job["completed"] == 2
    assert job["failed"] == 1
    assert store.dead_letter_count() == 1
