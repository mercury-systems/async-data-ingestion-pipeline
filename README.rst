=======================================================
High-Throughput Async Ingestion Pipeline
=======================================================

An enterprise-grade, concurrent data routing pipeline I built with Python and FastAPI. Engineered to handle high-volume public API ingestion using strict asynchronous context managers, localized connection pooling, and fault-tolerant rate-limit backoffs.

Systems Documentation Matrix
----------------------------

* **Technical Architecture Deep-Dive:** Read `ARCHITECTURE.md <./ARCHITECTURE.md>`_ to review my async connection pooling constraints and mock transport testing architecture.
* **User Operation Manual:** Read `USAGE.md <./USAGE.md>`_ for setup instructions, starting the Uvicorn server, and example API endpoint payloads.
