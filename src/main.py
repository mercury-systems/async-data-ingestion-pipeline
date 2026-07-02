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
