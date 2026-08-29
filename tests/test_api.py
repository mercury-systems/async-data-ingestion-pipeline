"""Tests for API routes."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_single_ingest(client):
    response = client.post("/api/ingest", json={"url": "https://httpbin.org/get"})
    assert response.status_code in (200, 429, 503)


def test_batch_ingest(client):
    response = client.post("/api/ingest/batch", json={
        "urls": ["https://httpbin.org/get", "https://httpbin.org/get"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["total"] == 2
    assert data["status"] == "pending"


def test_metrics(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "circuit_breakers" in data


def test_dead_letter(client):
    response = client.get("/api/dead-letter")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
