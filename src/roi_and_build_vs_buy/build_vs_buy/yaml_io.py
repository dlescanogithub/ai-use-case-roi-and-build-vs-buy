"""YAML loading at the trust boundary."""

from __future__ import annotations

from pathlib import Path

import yaml

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError


def load_mapping(path: Path) -> dict[str, object]:
    """Load a YAML file and require a mapping at the root."""

    if not path.is_file():
        raise ValidationError([f"missing file: {path}"])
    raw: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValidationError([f"{path} root must be a mapping"])
    parsed: dict[str, object] = {}
    for key, value in raw.items():
        if not isinstance(key, str):
            raise ValidationError([f"{path} contains a non-string key"])
        parsed[key] = value
    return parsed
