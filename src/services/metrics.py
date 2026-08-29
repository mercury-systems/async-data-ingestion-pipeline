"""In-memory metrics tracking."""

import time
import threading
from typing import Dict


class Metrics:
    def __init__(self):
        self._total = 0
        self._success = 0
        self._failed = 0
        self._latencies: list = []
        self._lock = threading.Lock()

    def record(self, success: bool, latency: float):
        with self._lock:
            self._total += 1
            if success:
                self._success += 1
            else:
                self._failed += 1
            self._latencies.append(latency)
            if len(self._latencies) > 10000:
                self._latencies = self._latencies[-5000:]

    def get(self) -> Dict:
        with self._lock:
            avg = sum(self._latencies) / len(self._latencies) * 1000 if self._latencies else 0
            return {
                "total_requests": self._total,
                "successful_requests": self._success,
                "failed_requests": self._failed,
                "avg_latency_ms": round(avg, 2),
            }
