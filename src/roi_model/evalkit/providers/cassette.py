"""Replay a recorded response. Missing ids fail closed (no live fallback)."""

from __future__ import annotations

import json
from pathlib import Path

from roi_model.evalkit.providers.base import ProviderResponse
from roi_model.retry import retry


class CassetteError(RuntimeError):
    """The cassette does not contain the requested id."""


class CassetteProvider:
    name = "cassette"

    def __init__(self, path: Path) -> None:
        self.path = path
        self._responses = _load(path)

    def complete(self, prompt_id: str) -> ProviderResponse:
        found = self._responses.get(prompt_id)
        if found is None:
            raise CassetteError(f"cassette has no response for {prompt_id}")
        return found


def _load(path: Path) -> dict[str, ProviderResponse]:
    def read() -> str:
        return path.read_text(encoding="utf-8")

    text = retry(read, max_attempts=3, base_delay=0.01, backoff_cap=0.05)
    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise CassetteError("cassette root must be an object")
    rows = raw.get("responses")
    if not isinstance(rows, list):
        raise CassetteError("cassette responses must be a list")
    loaded: dict[str, ProviderResponse] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise CassetteError("cassette row must be an object")
        prompt_id = row.get("id")
        output = row.get("output")
        cost = row.get("cost")
        tokens = row.get("tokens")
        if not isinstance(prompt_id, str) or not isinstance(output, str):
            raise CassetteError("cassette id and output must be strings")
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            raise CassetteError("cassette cost must be a number")
        if isinstance(tokens, bool) or not isinstance(tokens, int):
            raise CassetteError("cassette tokens must be an integer")
        loaded[prompt_id] = ProviderResponse(
            text=output,
            cost=float(cost),
            tokens=tokens,
            provider="cassette",
        )
    return loaded
