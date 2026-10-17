"""Append-only JSONL traces for both eval gates."""

from __future__ import annotations

import json
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def append_event(path: Path, event: dict[str, Any]) -> None:
    """Append one object. Does not add a timestamp."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")


def read_events(path: Path) -> list[dict[str, Any]]:
    """Read a JSONL trace. Missing file is an empty list."""

    return _read(path)


def append_trace(path: Path, event: Mapping[str, object]) -> None:
    """Append one object and stamp ``ts``. Used by the decision-kit gate."""

    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"ts": datetime.now(UTC).isoformat(), **dict(event)}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True, default=str) + "\n")


def read_trace(path: Path) -> list[dict[str, object]]:
    """Read a JSONL trace file."""

    return _read(path)


def _read(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        loaded: object = json.loads(line)
        if not isinstance(loaded, dict):
            raise ValueError("trace line is not an object")
        events.append({str(key): value for key, value in loaded.items()})
    return events
