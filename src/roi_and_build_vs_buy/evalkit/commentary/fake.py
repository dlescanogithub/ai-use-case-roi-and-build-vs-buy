"""In-memory stand-in used by tests and the eval gate."""

from __future__ import annotations

from roi_and_build_vs_buy.evalkit.commentary.base import ProviderResponse


class FakeProvider:
    name = "fake"

    def complete(self, prompt_id: str) -> ProviderResponse:
        del prompt_id
        return ProviderResponse(
            text="Commentary stays inside the report. No external action.",
            cost=0.0,
            tokens=0,
            provider=self.name,
        )
