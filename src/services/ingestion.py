import httpx
import logging
from typing import Optional, Dict, Any

from src.core.config import settings
from src.models.data import IngestionResponse

logger = logging.getLogger(__name__)

class IngestionService:
    def __init__(self, transport: Optional[httpx.AsyncBaseTransport] = None):
        limits = httpx.Limits(
            max_connections=settings.ingestion_max_connections,
            max_keepalive_connections=settings.ingestion_max_keepalive,
        )
        self.transport = transport
        self.limits = limits
        self.timeout = httpx.Timeout(settings.ingestion_timeout)

    async def ingest_data(self, url: str, params: Optional[Dict[str, Any]] = None) -> IngestionResponse:
        """
        Asynchronously fetches data from the given URL.
        Demonstrates connection pooling, context management, and graceful error handling.
        """
        async with httpx.AsyncClient(
            limits=self.limits,
            timeout=self.timeout,
            transport=self.transport
        ) as client:
            try:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                # Check for standard 2xx responses
                return IngestionResponse(
                    status_code=response.status_code,
                    data=response.json()
                )
                
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429:
                    error_msg = f"Rate limit exceeded (429) for {url}"
                    logger.warning(error_msg)
                elif status >= 500:
                    error_msg = f"Server error ({status}) when accessing {url}"
                    logger.error(error_msg)
                else:
                    error_msg = f"HTTP Error {status}: {str(e)}"
                    logger.error(error_msg)
                
                return IngestionResponse(
                    status_code=status,
                    error=error_msg
                )
            except httpx.RequestError as e:
                error_msg = f"Request failed: {str(e)}"
                logger.error(error_msg)
                return IngestionResponse(
                    status_code=503, # Service Unavailable/Gateway Timeout concept
                    error=error_msg
                )
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                return IngestionResponse(
                    status_code=500,
                    error=error_msg
                )
