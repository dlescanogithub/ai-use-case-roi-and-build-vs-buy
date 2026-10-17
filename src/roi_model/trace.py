"""Append-only JSONL traces for the eval gate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
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
