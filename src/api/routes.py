from fastapi import APIRouter, HTTPException, Depends
from src.models.data import IngestionRequest, IngestionResponse
from src.services.ingestion import IngestionService

router = APIRouter()

# Dependency to get the ingestion service
def get_ingestion_service() -> IngestionService:
    return IngestionService()

@router.post("/ingest", response_model=IngestionResponse)
async def ingest_endpoint(
    request: IngestionRequest,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Triggers the ingestion service for a given URL and parameters.
    """
    response = await service.ingest_data(url=request.url, params=request.params)
    if response.error:
        # We can either return the error in the schema or raise an HTTPException.
        # Given the schema design, we return it normally but with the corresponding status embedded in the response.
        pass
    
    return response
