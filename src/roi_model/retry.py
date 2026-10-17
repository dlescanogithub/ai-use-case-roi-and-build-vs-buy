"""Bounded retries with a capped exponential backoff."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


class RetryError(RuntimeError):
    """Raised when every attempt has failed."""


def retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.05,
    backoff_cap: float = 0.5,
    sleep: Callable[[float], None] = time.sleep,
) -> T:
    """Call ``fn`` until it returns or ``max_attempts`` is exhausted.

    The delay before attempt ``n+1`` is ``min(backoff_cap, base_delay * 2**(n-1))``.
    There is no delay after the final failure.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    if base_delay < 0 or backoff_cap < 0:
        raise ValueError("delays must be >= 0")
    last: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as exc:
            last = exc
            if attempt == max_attempts:
                break
            delay = min(backoff_cap, base_delay * (2 ** (attempt - 1)))
            sleep(delay)
    raise RetryError(f"failed after {max_attempts} attempts") from last
