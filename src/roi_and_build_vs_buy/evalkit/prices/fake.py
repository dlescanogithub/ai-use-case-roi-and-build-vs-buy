"""In-memory provider. Cost is always zero. Used when no cassette is configured."""

from __future__ import annotations

from decimal import Decimal

from roi_and_build_vs_buy.evalkit.prices.base import Quote


class FakePriceProvider:
    """Return a fixed fictional quote. No network."""

    def quote(self, vendor_id: str) -> Quote:
        return Quote(
            vendor_id=vendor_id,
            usd_per_seat_year=Decimal("1000"),
            source="fake provider, fictional",
            simulated=True,
            cost_usd=Decimal(0),
        )
