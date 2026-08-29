"""Core ingestion service with retry and circuit breaker."""

import random
import time
import logging
from typing import Optional, Dict, Any
from urllib.parse import urlparse

import httpx

from src.core.config import settings
from src.core.circuit_breaker import CircuitBreaker
from src.models.data import IngestionResponse
from src.services.metrics import Metrics

logger = logging.getLogger(__name__)


def _jittered_delay(attempt: int, base: float, max_delay: float) -> float:
    delay = min(base * (2 ** attempt), max_delay)
    return delay + random.uniform(0, delay * 0.5)


class IngestionService:
    def __init__(self, transport: Optional[httpx.AsyncBaseTransport] = None,
                 metrics: Optional[Metrics] = None,
                 circuit_breaker: Optional[CircuitBreaker] = None):
        self.limits = httpx.Limits(
            max_connections=settings.ingestion_max_connections,
            max_keepalive_connections=settings.ingestion_max_keepalive,
        )
        self.timeout = httpx.Timeout(settings.ingestion_timeout)
        self.transport = transport
        self.metrics = metrics or Metrics()
        self.circuit = circuit_breaker or CircuitBreaker(
            threshold=settings.circuit_breaker_threshold,
            timeout=settings.circuit_breaker_timeout,
        )

    async def ingest_data(self, url: str, params: Optional[Dict[str, Any]] = None) -> IngestionResponse:
        domain = urlparse(url).netloc

        if not self.circuit.can_call(domain):
            return IngestionResponse(
                status_code=503,
                error=f"Circuit breaker open for {domain}",
            )

        start = time.time()
        last_error = None
        status_code = 0
        retries = 0

        for attempt in range(settings.max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    limits=self.limits,
                    timeout=self.timeout,
                    transport=self.transport,
                ) as client:
                    response = await client.get(url, params=params)
                    response.raise_for_status()
                    latency = time.time() - start
                    self.metrics.record(True, latency)
                    self.circuit.record_success(domain)
                    return IngestionResponse(
                        status_code=response.status_code,
                        data=response.json(),
                        latency_ms=round(latency * 1000, 2),
                        retries=retries,
                    )

            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                if status_code == 429:
                    last_error = f"Rate limit exceeded (429) for {url}"
                    logger.warning(last_error)
                elif status_code >= 500:
                    last_error = f"Server error ({status_code}) for {url}"
                    logger.error(last_error)
                else:
                    last_error = f"HTTP error {status_code}: {str(e)}"
                    logger.error(last_error)

            except httpx.RequestError as e:
                last_error = f"Request failed: {str(e)}"
                logger.error(last_error)
                status_code = 503

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(last_error)
                status_code = 500

            if attempt < settings.max_retries:
                retries += 1
                delay = _jittered_delay(attempt, settings.retry_base_delay, settings.max_retry_delay)
                logger.info(f"Retrying {url} in {delay:.2f}s (attempt {retries}/{settings.max_retries})")
                await _async_sleep(delay, self.transport)

        latency = time.time() - start
        self.metrics.record(False, latency)
        self.circuit.record_failure(domain)
        return IngestionResponse(
            status_code=status_code,
            error=last_error,
            latency_ms=round(latency * 1000, 2),
            retries=retries,
        )


async def _async_sleep(delay: float, transport):
    if transport is not None:
        return
    import asyncio
    await asyncio.sleep(delay)
