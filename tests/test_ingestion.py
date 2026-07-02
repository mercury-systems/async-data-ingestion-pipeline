import pytest
import httpx
from src.services.ingestion import IngestionService

@pytest.fixture
def mock_success_transport():
    def handler(request: httpx.Request):
        return httpx.Response(200, json={"message": "Success", "data": [1, 2, 3]})
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


@pytest.mark.asyncio
async def test_ingest_data_success(mock_success_transport):
    service = IngestionService(transport=mock_success_transport)
    response = await service.ingest_data("https://api.example.com/data")
    
    assert response.status_code == 200
    assert response.data == {"message": "Success", "data": [1, 2, 3]}
    assert response.error is None

@pytest.mark.asyncio
async def test_ingest_data_rate_limit(mock_rate_limit_transport):
    service = IngestionService(transport=mock_rate_limit_transport)
    response = await service.ingest_data("https://api.example.com/data")
    
    assert response.status_code == 429
    assert response.data is None
    assert "Rate limit exceeded" in response.error

@pytest.mark.asyncio
async def test_ingest_data_server_error(mock_server_error_transport):
    service = IngestionService(transport=mock_server_error_transport)
    response = await service.ingest_data("https://api.example.com/data")
    
    assert response.status_code == 500
    assert response.data is None
    assert "Server error (500)" in response.error

@pytest.mark.asyncio
async def test_ingest_data_request_error():
    # Test request error without mock transport (e.g. invalid URL handling causing ConnectError)
    # Actually, let's use a transport that raises a RequestError
    def handler(request: httpx.Request):
        raise httpx.ConnectError("Network is unreachable")
    
    transport = httpx.MockTransport(handler)
    service = IngestionService(transport=transport)
    response = await service.ingest_data("https://api.example.com/data")
    
    assert response.status_code == 503
    assert response.data is None
    assert "Request failed: Network is unreachable" in response.error
