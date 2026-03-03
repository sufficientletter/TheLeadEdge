"""Tenacity retry decorators for external service calls.

Provides pre-configured retry strategies for different failure domains:
- ``api_retry``: For external HTTP APIs (MLS, CRM, skip trace) with
  aggressive backoff and 3 attempts.
- ``gentle_retry``: For local I/O operations (file reads, database writes)
  with shorter waits and 2 attempts.

Usage:
    from theleadedge.utils.retry import api_retry, gentle_retry

    @api_retry
    async def fetch_from_crm(lead_id: str) -> dict:
        ...

    @gentle_retry
    async def write_to_db(record: dict) -> None:
        ...
"""

from __future__ import annotations

import logging

import httpx
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# For external API calls — aggressive retry with exponential backoff
api_retry = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type(
        (httpx.TimeoutException, httpx.HTTPStatusError, ConnectionError),
    ),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)

# For gentle operations (file I/O, DB writes) — fewer retries, shorter waits
gentle_retry = retry(
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((OSError, TimeoutError)),
    before_sleep=before_sleep_log(logger, logging.INFO),
    reraise=True,
)
