"""Per-domain circuit breaker."""

import time
import threading
from typing import Dict


class CircuitState:
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    def __init__(self, threshold: int = 5, timeout: int = 120):
        self._threshold = threshold
        self._timeout = timeout
        self._states: Dict[str, dict] = {}
        self._lock = threading.Lock()

    def _get_state(self, domain: str) -> dict:
        if domain not in self._states:
            self._states[domain] = {
                "state": CircuitState.CLOSED,
                "failures": 0,
                "last_failure": 0.0,
            }
        return self._states[domain]

    def can_call(self, domain: str) -> bool:
        with self._lock:
            state = self._get_state(domain)
            if state["state"] == CircuitState.OPEN:
                if time.time() - state["last_failure"] > self._timeout:
                    state["state"] = CircuitState.HALF_OPEN
                    return True
                return False
            return True

    def record_success(self, domain: str):
        with self._lock:
            state = self._get_state(domain)
            state["failures"] = 0
            state["state"] = CircuitState.CLOSED

    def record_failure(self, domain: str):
        with self._lock:
            state = self._get_state(domain)
            state["failures"] += 1
            state["last_failure"] = time.time()
            if state["failures"] >= self._threshold:
                state["state"] = CircuitState.OPEN

    def get_states(self) -> Dict[str, dict]:
        with self._lock:
            return {
                domain: {
                    "state": s["state"],
                    "failures": s["failures"],
                }
                for domain, s in self._states.items()
            }
