# Async Data Ingestion Pipeline

FastAPI service for ingesting data from external APIs with retry, circuit breaker, and job tracking.

## What It Does

- **Single ingestion**: POST a URL, get back the fetched JSON with latency and retry count.
- **Batch ingestion**: POST a list of URLs, get a job ID immediately. Processing happens in the background via FastAPI BackgroundTasks.
- **Retry with jitter**: 3 retries on 429/500/network errors, with exponential backoff and jitter.
- **Circuit breaker**: Per-domain failure tracking. If a domain fails 5 times in 2 minutes, requests are blocked until it recovers.
- **Job tracking**: SQLite-backed job store. Check status, progress, and results via job ID.
- **Dead letter queue**: Failed ingestions stored with error reason and URL.
- **Metrics**: Request count, success rate, average latency, active jobs, circuit breaker states.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/ingest` | Single URL ingestion |
| POST | `/api/ingest/batch` | Batch ingestion (returns job ID) |
| GET | `/api/jobs/{job_id}` | Job status and results |
| GET | `/api/metrics` | System metrics |
| GET | `/api/dead-letter` | Failed ingestions |

## Installation

```bash
git clone https://github.com/mercury-systems/async-data-ingestion-pipeline.git
cd async-data-ingestion-pipeline
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

For running tests:

```bash
pip install -r requirements-dev.txt
```

> **Note:** Always activate the virtual environment (`source .venv/bin/activate`) before working with this project.

## Quick Start

    # Start server
    uvicorn src.main:app --reload

    # Single ingestion
    curl -X POST http://localhost:8000/api/ingest \
      -H "Content-Type: application/json" \
      -d '{"url": "https://api.example.com/data"}'

    # Batch ingestion
    curl -X POST http://localhost:8000/api/ingest/batch \
      -H "Content-Type: application/json" \
      -d '{"urls": ["https://api1.com", "https://api2.com"]}'

    # Check job status (replace {job_id} with actual ID from batch response)
    curl http://localhost:8000/api/jobs/{job_id}

    # View metrics
    curl http://localhost:8000/api/metrics

    # View dead letter queue
    curl http://localhost:8000/api/dead-letter

    # Interactive API docs
    # Open http://localhost:8000/docs in your browser

## Demo

Run the live demo against httpbin.org (no server needed):

    make demo

## Docker

    docker compose up --build

## Test

    make test        # Unit tests only (no network)
    make test-all    # All tests including integration

## License

MIT
