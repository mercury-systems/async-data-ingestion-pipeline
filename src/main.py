#!/usr/bin/env python3
"""FastAPI application entry point."""

import os
import sys

# Ensure src is importable when running directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from src.api.routes import router as api_router
from src.core.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

app.include_router(api_router, prefix="/api", tags=["Ingestion"])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
