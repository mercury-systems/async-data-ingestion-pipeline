from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class IngestionRequest(BaseModel):
    url: str = Field(..., description="The target URL to ingest data from.")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters.")

class IngestionResponse(BaseModel):
    status_code: int
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
