"""Deterministic commentary. No model call."""

from __future__ import annotations

from roi_and_build_vs_buy.evalkit.commentary.base import ProviderResponse


class TemplateProvider:
    name = "template"

    def complete(self, prompt_id: str) -> ProviderResponse:
        return ProviderResponse(
            text=(
                "Planning sketch only. The report stays on disk. "
                f"Prompt {prompt_id} did not approve an external action."
            ),
            cost=0.0,
            tokens=0,
            provider=self.name,
        )
