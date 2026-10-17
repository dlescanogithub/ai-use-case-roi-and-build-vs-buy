"""Guard for a vendor adapter that this repository does not ship.

The flag defaults off. Turning it on still does not open a socket: there is
no HTTP client here, so a paid API cannot be called by accident or from CI.
"""

from __future__ import annotations

from roi_model.evalkit.providers.base import ProviderResponse


class RealProviderDisabled(RuntimeError):
    """The real provider must not run."""


class RealProvider:
    name = "real"

    def __init__(self, *, enabled: bool, api_key: str) -> None:
        self.enabled = enabled
        self.api_key = api_key

    def complete(self, prompt_id: str) -> ProviderResponse:
        del prompt_id
        if not self.enabled:
            raise RealProviderDisabled("real provider is off (ROI_ENABLE_REAL_PROVIDER is not 1)")
        if not self.api_key:
            raise RealProviderDisabled("real provider has no key")
        raise RealProviderDisabled("no vendor client is shipped; the real provider cannot make a network call")
