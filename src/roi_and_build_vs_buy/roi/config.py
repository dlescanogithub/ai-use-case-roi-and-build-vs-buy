"""Process configuration from the environment only."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ALLOWED_PROVIDERS = ("template", "fake", "cassette", "real")
ALLOWED_LOG_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR")


class ConfigError(ValueError):
    """Raised when an environment variable is present but invalid."""


@dataclass(frozen=True)
class Settings:
    log_level: str
    output_dir: Path
    assumptions_path: Path
    seed: int
    provider: str
    mc_draws: int
    cost_cap: float
    enable_real_provider: bool
    provider_api_key: str
    cassette_path: Path


def _int(name: str, default: str) -> int:
    raw = os.environ.get(name, default)
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer") from exc


def _float(name: str, default: str) -> float:
    raw = os.environ.get(name, default)
    try:
        value = float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number") from exc
    if value != value or value in (float("inf"), float("-inf")):
        raise ConfigError(f"{name} must be finite")
    return value


def load_settings() -> Settings:
    """Read settings from the environment.

    Missing variables fall back to local, zero-cost defaults. A real provider
    key has no default. This function does not read a ``.env`` file.
    """
    level = os.environ.get("ROI_LOG_LEVEL", "INFO").upper()
    if level not in ALLOWED_LOG_LEVELS:
        raise ConfigError(f"ROI_LOG_LEVEL must be one of {ALLOWED_LOG_LEVELS}")
    provider = os.environ.get("ROI_PROVIDER", "template")
    if provider not in ALLOWED_PROVIDERS:
        raise ConfigError(f"ROI_PROVIDER must be one of {ALLOWED_PROVIDERS}")
    draws = _int("ROI_MC_DRAWS", "2000")
    if not 1 <= draws <= 100_000:
        raise ConfigError("ROI_MC_DRAWS must be between 1 and 100000")
    cost_cap = _float("ROI_COST_CAP", "0")
    if cost_cap < 0:
        raise ConfigError("ROI_COST_CAP must be >= 0")
    flag = os.environ.get("ROI_ENABLE_REAL_PROVIDER", "0")
    if flag not in {"0", "1"}:
        raise ConfigError("ROI_ENABLE_REAL_PROVIDER must be 0 or 1")
    return Settings(
        log_level=level,
        output_dir=Path(os.environ.get("ROI_OUTPUT_DIR", "out")),
        assumptions_path=Path(os.environ.get("ROI_ASSUMPTIONS", "assumptions/refund_desk.yaml")),
        seed=_int("ROI_SEED", "42"),
        provider=provider,
        mc_draws=draws,
        cost_cap=cost_cap,
        enable_real_provider=flag == "1",
        provider_api_key=os.environ.get("ROI_PROVIDER_API_KEY", ""),
        cassette_path=Path(os.environ.get("ROI_CASSETTE", "evals/cassettes/commentary.json")),
    )
