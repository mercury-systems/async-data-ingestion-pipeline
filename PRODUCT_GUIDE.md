# Product Guide — Async Data Ingestion Pipeline

## 1. Product Name
**Async Data Ingestion Pipeline**

## 2. One-Line Pitch
High-throughput async data routing pipeline with FastAPI, connection pooling, and fault-tolerant error handling.

## 3. Problem Statement
FastAPI backends often degrade under load when making synchronous downstream network calls or using improperly scoped async HTTP clients. Connection exhaustion (EMFILE), event loop blocking, and unhandled rate limits crash services. This pipeline solves all three through strict async context managers, localized connection pooling, and graceful error state machines.

## 4. Target Audience
- Backend engineers building high-volume API ingestion layers
- DevOps teams needing resilient microservices with deterministic testing
- Data platform teams routing public API feeds into internal pipelines
- SREs requiring connection-safe, rate-limit-aware HTTP clients

## 5. Key Features
- **Async HTTPX Client** — Non-blocking I/O with dedicated connection pools
- **Connection Pool Tuning** — `max_connections` and `max_keepalive` limits prevent socket exhaustion
- **Graceful Error Handling** — 429 rate-limit detection, 5xx server error classification, network failure recovery
- **Mock Transport Testing** — 100% offline test coverage via `httpx.MockTransport`
- **FastAPI Integration** — Auto-generated Swagger docs, dependency injection, Pydantic validation
- **Docker Ready** — Single-container deployment with Uvicorn

## 6. Technical Stack
- **Language:** Python 3.12+
- **Framework:** FastAPI
- **HTTP Client:** httpx (async)
- **Configuration:** pydantic-settings
- **Testing:** pytest + pytest-asyncio + httpx.MockTransport
- **Server:** Uvicorn

## 7. Architecture Overview
```
src/
├── main.py              # FastAPI app, health check, router inclusion
├── api/
│   └── routes.py        # POST /api/ingest endpoint with DI
├── core/
│   └── config.py        # Pydantic settings with .env support
├── models/
│   └── data.py          # IngestionRequest / IngestionResponse schemas
└── services/
    └── ingestion.py     # IngestionService with httpx pooling
```

## 8. Getting Started
```bash
pip install -e .
uvicorn src.main:app --reload
# POST to http://127.0.0.1:8000/api/ingest
# {"url": "https://api.example.com/data", "params": {"limit": 100}}
```

## 9. Deployment
- **Local:** `uvicorn src.main:app --reload`
- **Docker:** `docker compose up`
- **CI:** GitHub Actions runs pytest and lint on every push

## 10. Related Products
- **Universal Extraction Engine** — Structured web data extraction (feeds into this pipeline for raw ingestion)
- **Distributed Stealth Scraper** — Anonymous large-scale scraping (provides target URLs for ingestion)
- **AetherScan** — Infrastructure discovery (identifies API endpoints to ingest from)

All four products share the MERCURY-OPS core philosophy: async-first, resource-safe, deterministic testing.
