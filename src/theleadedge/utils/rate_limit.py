"""Circuit breaker for external service calls.

Prevents cascading failures when an external service (CRM, skip trace API,
email provider) goes down. Stops sending requests after repeated failures,
then gradually tests recovery.

Usage:
    from theleadedge.utils.rate_limit import CircuitBreaker

    crm_breaker = CircuitBreaker(
        "follow_up_boss", failure_threshold=5, recovery_timeout=60.0,
    )

    if crm_breaker.is_available:
        try:
            result = await call_crm(...)
            crm_breaker.record_success()
        except Exception:
            crm_breaker.record_failure()
    else:
        logger.warning(
            "circuit open", service=crm_breaker.name, state=crm_breaker.state,
        )
"""

from __future__ import annotations

import time
from enum import StrEnum


class CircuitState(StrEnum):
    """State of a circuit breaker."""

    CLOSED = "closed"  # Normal operation — requests flow through
    OPEN = "open"  # Failing — requests are rejected
    HALF_OPEN = "half_open"  # Testing recovery — one request allowed


class CircuitBreaker:
    """Simple circuit breaker for external service calls.

    State transitions:
        CLOSED -> OPEN:      after ``failure_threshold`` consecutive failures
        OPEN -> HALF_OPEN:   after ``recovery_timeout`` seconds
        HALF_OPEN -> CLOSED: on first success
        HALF_OPEN -> OPEN:   on first failure

    Args:
        name: Human-readable service name (for logging).
        failure_threshold: Number of consecutive failures before opening.
        recovery_timeout: Seconds to wait before testing recovery.
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ) -> None:
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0.0

    @property
    def is_available(self) -> bool:
        """Check whether the circuit allows a request through.

        Returns True if CLOSED or HALF_OPEN. Transitions from OPEN to
        HALF_OPEN if the recovery timeout has elapsed.
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                return True
            return False

        # HALF_OPEN: allow one request through to test recovery
        return True

    def record_success(self) -> None:
        """Record a successful call. Resets failure count and closes circuit."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def record_failure(self) -> None:
        """Record a failed call. Opens circuit if threshold is reached."""
        self.failure_count += 1
        self.last_failure_time = time.monotonic()

        if self.state == CircuitState.HALF_OPEN:
            # Recovery attempt failed — reopen
            self.state = CircuitState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
