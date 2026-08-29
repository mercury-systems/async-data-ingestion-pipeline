"""Tests for job store."""

import pytest
from src.services.job_store import JobStore


class TestJobStore:
    def test_create_and_get_job(self):
        store = JobStore(db_path=":memory:")
        job_id = store.create_job(total=5)
        job = store.get_job(job_id)
        assert job is not None
        assert job["total"] == 5
        assert job["status"] == "pending"
        assert job["pending"] == 5

    def test_update_job(self):
        store = JobStore(db_path=":memory:")
        job_id = store.create_job(total=5)
        store.update_job(job_id, status="running", completed=2, failed=1, pending=2)
        job = store.get_job(job_id)
        assert job["status"] == "running"
        assert job["completed"] == 2
        assert job["failed"] == 1
        assert job["pending"] == 2

    def test_dead_letter(self):
        store = JobStore(db_path=":memory:")
        store.add_dead_letter("job-1", "https://fail.com", "Timeout", 503)
        dl = store.get_dead_letter()
        assert len(dl) == 1
        assert dl[0]["url"] == "https://fail.com"
        assert dl[0]["error"] == "Timeout"

    def test_active_jobs(self):
        store = JobStore(db_path=":memory:")
        assert store.active_jobs() == 0
        store.create_job(total=3)
        assert store.active_jobs() == 1

    def test_dead_letter_count(self):
        store = JobStore(db_path=":memory:")
        assert store.dead_letter_count() == 0
        store.add_dead_letter("job-1", "https://a.com", "err")
        store.add_dead_letter("job-1", "https://b.com", "err")
        assert store.dead_letter_count() == 2
