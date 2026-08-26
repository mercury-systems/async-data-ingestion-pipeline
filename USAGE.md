# High-Throughput Async Ingestion Pipeline: Operational Guide

This document outlines the setup, execution, and testing procedures for the FastAPI ingestion pipeline.

## Quick Start

This project is built to be deterministic and blazing fast. Using `uv` to manage the Python 3.12+ environment is recommended.

### 1. Installation

```bash
# 1. Ensure you have the ultra-fast 'uv' package manager installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Scaffold a deterministic Python 3.12 virtual environment
uv python install 3.12
uv venv -p 3.12 venv
source venv/bin/activate

# 3. Install dependencies natively
uv pip install -r requirements.txt
```

### 2. Running the Server

Start the FastAPI application using Uvicorn:

```bash
uvicorn src.main:app --reload
```

The server will run natively on `http://127.0.0.1:8000`. Access the auto-generated Swagger documentation at `http://127.0.0.1:8000/docs`.

### 3. Usage Example

**Endpoint:** `POST /api/ingest`

**Payload:**
```json
{
  "url": "https://api.example.com/v1/data",
  "params": {
    "limit": 100
  }
}
```

## Testing

Run the localized verification suite to validate mock transport logic:

```bash
pytest tests/ -v
```
