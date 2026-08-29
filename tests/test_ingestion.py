"""Tests for ingestion service."""

import asyncio
import pytest
import httpx

from src.services.ingestion import IngestionService
from src.services.metrics import Metrics
from src.core.circuit_breaker import CircuitBreaker


@pytest.fixture
def mock_success_transport():
    def handler(request: httpx.Request):
        return httpx.Response(200, json={"message": "ok"})
    return httpx.MockTransport(handler)


@pytest.fixture
def mock_rate_limit_transport():
    def handler(request: httpx.Request):
        return httpx.Response(429, text="Too Many Requests")
    return httpx.MockTransport(handler)


@pytest.fixture
def mock_server_error_transport():
    def handler(request: httpx.Request):
        return httpx.Response(500, text="Internal Server Error")
    return httpx.MockTransport(handler)


@pytest.fixture
def mock_network_error_transport():
    def handler(request: httpx.Request):
        raise httpx.ConnectError("Network unreachable")
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_ingest_success(mock_success_transport):
    service = IngestionService(transport=mock_success_transport)
    result = await service.ingest_data("https://api.example.com/data")
    assert result.status_code == 200
    assert result.data == {"message": "ok"}
    assert result.error is None
    assert result.retries == 0


@pytest.mark.asyncio
async def test_ingest_rate_limit(mock_rate_limit_transport):
    service = IngestionService(transport=mock_rate_limit_transport)
    result = await service.ingest_data("https://api.example.com/data")
    assert result.status_code == 429
    assert "Rate limit exceeded" in result.error
    assert result.retries == 3


@pytest.mark.asyncio
async def test_ingest_server_error(mock_server_error_transport):
    service = IngestionService(transport=mock_server_error_transport)
    result = await service.ingest_data("https://api.example.com/data")
    assert result.status_code == 500
    assert "Server error (500)" in result.error


@pytest.mark.asyncio
async def test_ingest_network_error(mock_network_error_transport):
    service = IngestionService(transport=mock_network_error_transport)
    result = await service.ingest_data("https://api.example.com/data")
    assert result.status_code == 503
    assert "Request failed" in result.error


@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    cb = CircuitBreaker(threshold=3, timeout=300)
    metrics = Metrics()

    def handler(request: httpx.Request):
        return httpx.Response(500)
    transport = httpx.MockTransport(handler)

    service = IngestionService(transport=transport, metrics=metrics, circuit_breaker=cb)

    for _ in range(3):
        await service.ingest_data("https://fail.example.com/data")

    assert cb.get_states()["fail.example.com"]["state"] == "open"

    result = await service.ingest_data("https://fail.example.com/data")
    assert result.status_code == 503
    assert "Circuit breaker open" in result.error


@pytest.mark.asyncio
async def test_circuit_breaker_closes_after_timeout():
    cb = CircuitBreaker(threshold=2, timeout=0)
    metrics = Metrics()

    def handler(request: httpx.Request):
        return httpx.Response(500)
    transport = httpx.MockTransport(handler)

    service = IngestionService(transport=transport, metrics=metrics, circuit_breaker=cb)

    for _ in range(2):
        await service.ingest_data("https://recover.example.com/data")

    assert cb.get_states()["recover.example.com"]["state"] == "open"

    # Wait for timeout
    await asyncio.sleep(0.1)

    # Should be half-open now, then succeed on next call
    def success_handler(request: httpx.Request):
        return httpx.Response(200, json={"ok": True})
    service = IngestionService(
        transport=httpx.MockTransport(success_handler),
        metrics=metrics,
        circuit_breaker=cb,
    )
    result = await service.ingest_data("https://recover.example.com/data")
    assert result.status_code == 200
    assert cb.get_states()["recover.example.com"]["state"] == "closed"
