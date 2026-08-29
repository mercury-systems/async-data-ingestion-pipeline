"""SQLite-backed job and dead letter storage."""

import sqlite3
import uuid
import time
import threading
import json
from typing import List, Optional, Dict
from contextlib import contextmanager

from src.core.config import settings


class JobStore:
    def __init__(self, db_path: str = None):
        self._db = db_path or settings.job_db
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    total INTEGER NOT NULL,
                    completed INTEGER DEFAULT 0,
                    failed INTEGER DEFAULT 0,
                    pending INTEGER NOT NULL,
                    results TEXT DEFAULT '[]',
                    created_at REAL DEFAULT (unixepoch()),
                    updated_at REAL DEFAULT (unixepoch())
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS dead_letter (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    url TEXT NOT NULL,
                    error TEXT NOT NULL,
                    status_code INTEGER,
                    timestamp REAL DEFAULT (unixepoch())
                )
            """)
            conn.commit()

    @contextmanager
    def _connect(self):
        if self._db == ":memory:":
            if not hasattr(self, "_persistent_conn"):
                self._persistent_conn = sqlite3.connect(self._db, check_same_thread=False)
            yield self._persistent_conn
        else:
            conn = sqlite3.connect(self._db, check_same_thread=False)
            try:
                yield conn
            finally:
                conn.close()

    def create_job(self, total: int) -> str:
        job_id = str(uuid.uuid4())[:8]
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO jobs (job_id, status, total, pending) VALUES (?, ?, ?, ?)",
                    (job_id, "pending", total, total)
                )
                conn.commit()
        return job_id

    def update_job(self, job_id: str, status: str = None, completed: int = None,
                   failed: int = None, pending: int = None, results: List[dict] = None):
        with self._lock:
            with self._connect() as conn:
                updates = ["updated_at = ?"]
                params = [time.time()]
                if status:
                    updates.append("status = ?")
                    params.append(status)
                if completed is not None:
                    updates.append("completed = ?")
                    params.append(completed)
                if failed is not None:
                    updates.append("failed = ?")
                    params.append(failed)
                if pending is not None:
                    updates.append("pending = ?")
                    params.append(pending)
                if results is not None:
                    updates.append("results = ?")
                    params.append(json.dumps(results))
                params.append(job_id)
                conn.execute(
                    f"UPDATE jobs SET {', '.join(updates)} WHERE job_id = ?",
                    params
                )
                conn.commit()

    def get_job(self, job_id: str) -> Optional[dict]:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    "job_id": row[0],
                    "status": row[1],
                    "total": row[2],
                    "completed": row[3],
                    "failed": row[4],
                    "pending": row[5],
                    "results": json.loads(row[6]),
                    "created_at": row[7],
                    "updated_at": row[8],
                }

    def add_dead_letter(self, job_id: str, url: str, error: str, status_code: Optional[int] = None):
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO dead_letter (job_id, url, error, status_code) VALUES (?, ?, ?, ?)",
                    (job_id, url, error, status_code)
                )
                conn.commit()

    def get_dead_letter(self, limit: int = 50) -> List[dict]:
        with self._lock:
            with self._connect() as conn:
                cursor = conn.execute(
                    "SELECT url, error, status_code, timestamp FROM dead_letter ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return [
                    {"url": r[0], "error": r[1], "status_code": r[2], "timestamp": r[3]}
                    for r in cursor.fetchall()
                ]

    def dead_letter_count(self) -> int:
        with self._lock:
            with self._connect() as conn:
                return conn.execute("SELECT COUNT(*) FROM dead_letter").fetchone()[0]

    def active_jobs(self) -> int:
        with self._lock:
            with self._connect() as conn:
                return conn.execute(
                    "SELECT COUNT(*) FROM jobs WHERE status IN ('pending', 'running')"
                ).fetchone()[0]
