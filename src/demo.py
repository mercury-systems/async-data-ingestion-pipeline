#!/usr/bin/env python3
"""Live demo of the ingestion pipeline."""

import asyncio
import json
from datetime import datetime

import httpx
from src.services.ingestion import IngestionService
from src.services.job_store import JobStore
from src.services.metrics import Metrics
from src.core.circuit_breaker import CircuitBreaker


async def main():
    print("=" * 72)
    print("  MERCURY-OPS  |  Async Data Ingestion Pipeline  |  Live Demo")
    print("=" * 72)
    print()

    metrics = Metrics()
    circuit = CircuitBreaker()
    job_store = JobStore(db_path=":memory:")
    service = IngestionService(metrics=metrics, circuit_breaker=circuit)

    # Demo 1: Working ingestion
    print("  [1/2] Working ingestion — https://httpbin.org/get")
    print("-" * 50)
    result = await service.ingest_data("https://httpbin.org/get", params={"foo": "bar"})
    print(f"      Status: {result.status_code}")
    print(f"      Latency: {result.latency_ms}ms")
    print(f"      Retries: {result.retries}")
    print(f"      Error: {result.error or 'None'}")
    print()

    # Demo 2: Failing ingestion (with retry)
    print("  [2/2] Failing ingestion — https://httpbin.org/status/500")
    print("        (This endpoint always returns 500. Watch the retry system.)")
    print("-" * 50)
    result = await service.ingest_data("https://httpbin.org/status/500")
    print(f"      Status: {result.status_code}")
    print(f"      Retries: {result.retries}")
    print(f"      Error: {result.error}")
    print()

    # Summary
    print("=" * 72)
    print("  SUMMARY")
    print("=" * 72)
    m = metrics.get()
    print(f"      Total requests: {m['total_requests']}")
    print(f"      Successful: {m['successful_requests']}")
    print(f"      Failed: {m['failed_requests']}")
    print(f"      Avg latency: {m['avg_latency_ms']}ms")
    print()
    print(f"      Circuit breakers: {json.dumps(circuit.get_states(), indent=6)}")
    print()
    print("=" * 72)
    print("  Demo complete. Start the server with: uvicorn src.main:app --reload")
    print("=" * 72)


if __name__ == "__main__":
    asyncio.run(main())
