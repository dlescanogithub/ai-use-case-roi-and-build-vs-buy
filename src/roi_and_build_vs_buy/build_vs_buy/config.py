"""Environment-only settings. This module does not read a .env file."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError

_MAX_ATTEMPTS_LIMIT = 5
_BACKOFF_CAP_LIMIT = Decimal("30")


@dataclass(frozen=True)
class Settings:
    """Process settings loaded from the environment."""

    log_level: str
    real_provider: bool
    provider_base_url: str
    provider_api_key: str
    max_attempts: int
    backoff_cap_seconds: float
    cost_cap_usd: Decimal


def load_settings(env: Mapping[str, str] | None = None) -> Settings:
    """Load settings from `env` or `os.environ`."""

    source = os.environ if env is None else env
    flag = source.get("DECIDE_REAL_PROVIDER", "0")
    if flag not in {"0", "1"}:
        raise DecisionKitError("DECIDE_REAL_PROVIDER must be 0 or 1")
    level = source.get("DECIDE_LOG_LEVEL", "INFO").upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR"}:
        raise DecisionKitError("DECIDE_LOG_LEVEL must be DEBUG, INFO, WARNING, or ERROR")
    try:
        attempts = int(source.get("DECIDE_MAX_ATTEMPTS", "3"))
    except ValueError as exc:
        raise DecisionKitError("DECIDE_MAX_ATTEMPTS must be an integer") from exc
    if attempts < 1 or attempts > _MAX_ATTEMPTS_LIMIT:
        raise DecisionKitError(f"DECIDE_MAX_ATTEMPTS must be between 1 and {_MAX_ATTEMPTS_LIMIT}")
    try:
        cap = Decimal(source.get("DECIDE_BACKOFF_CAP_SECONDS", "2"))
    except Exception as exc:
        raise DecisionKitError("DECIDE_BACKOFF_CAP_SECONDS must be a number") from exc
    if cap <= 0 or cap > _BACKOFF_CAP_LIMIT:
        raise DecisionKitError(f"DECIDE_BACKOFF_CAP_SECONDS must be > 0 and <= {_BACKOFF_CAP_LIMIT}")
    try:
        cost_cap = Decimal(source.get("DECIDE_COST_CAP_USD", "0"))
    except Exception as exc:
        raise DecisionKitError("DECIDE_COST_CAP_USD must be a number") from exc
    if cost_cap < 0:
        raise DecisionKitError("DECIDE_COST_CAP_USD must be >= 0")
    return Settings(
        log_level=level,
        real_provider=flag == "1",
        provider_base_url=source.get("DECIDE_PROVIDER_BASE_URL", ""),
        provider_api_key=source.get("DECIDE_PROVIDER_API_KEY", ""),
        max_attempts=attempts,
        backoff_cap_seconds=float(cap),
        cost_cap_usd=cost_cap,
    )
