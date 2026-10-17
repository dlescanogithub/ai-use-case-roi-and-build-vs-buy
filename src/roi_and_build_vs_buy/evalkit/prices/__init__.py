"""Provider factory. The real adapter stays off unless the env flag is exactly 1."""

from __future__ import annotations

from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.config import Settings
from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError
from roi_and_build_vs_buy.evalkit.prices.base import PriceProvider
from roi_and_build_vs_buy.evalkit.prices.cassette import CassettePriceProvider
from roi_and_build_vs_buy.evalkit.prices.fake import FakePriceProvider
from roi_and_build_vs_buy.evalkit.prices.http import HttpPriceProvider, Transport


def build_provider(
    settings: Settings,
    *,
    cassette_path: Path | None = None,
    transport: Transport | None = None,
) -> PriceProvider:
    """Select a provider.

    Evals should call `build_eval_provider` instead. This factory is the only
    place that can construct the HTTP adapter, and only when the flag is on.
    """

    if settings.real_provider:
        if transport is None:
            raise DecisionKitError(
                "DECIDE_REAL_PROVIDER=1 requires an explicit transport; the default CLI does not open one"
            )
        return HttpPriceProvider(
            settings.provider_base_url,
            settings.provider_api_key,
            transport=transport,
            max_attempts=settings.max_attempts,
            backoff_cap=settings.backoff_cap_seconds,
        )
    if cassette_path is not None:
        return CassettePriceProvider(cassette_path)
    return FakePriceProvider()


def build_eval_provider(cassette_path: Path) -> CassettePriceProvider:
    """Provider used by the regression test. Ignores DECIDE_REAL_PROVIDER on purpose."""

    return CassettePriceProvider(cassette_path)
