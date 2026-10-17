"""Provider seam. Live vendors are not called from this package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    cost: float
    tokens: int
    provider: str


class Provider(Protocol):
    name: str

    def complete(self, prompt_id: str) -> ProviderResponse:
        """Return commentary for a known prompt id. Must not perform side effects."""
