"""Pydantic models."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class IngestionRequest(BaseModel):
    url: str = Field(..., description="Target URL to ingest")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")


class IngestionResponse(BaseModel):
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    retries: int = 0


class BatchIngestionRequest(BaseModel):
    urls: List[str] = Field(..., description="List of URLs to ingest")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Shared query parameters")


class BatchIngestionResponse(BaseModel):
    job_id: str
    status: str
    total: int
    completed: int = 0
    failed: int = 0
    pending: int = 0
    created_at: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    total: int
    completed: int
    failed: int
    pending: int
    results: List[dict]
    created_at: str
    updated_at: Optional[str] = None


class DeadLetterItem(BaseModel):
    url: str
    error: str
    status_code: Optional[int] = None
    timestamp: str


class MetricsResponse(BaseModel):
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_latency_ms: float
    active_jobs: int
    circuit_breakers: Dict[str, dict]
    dead_letter_count: int
