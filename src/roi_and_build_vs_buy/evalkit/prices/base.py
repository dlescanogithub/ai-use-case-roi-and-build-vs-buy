"""Price-quote providers.

The decision math reads YAML. Providers exist so the regression test can replay a cassette.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Quote:
    """A fictional or replayed seat price. `simulated` stays true on the default path."""

    vendor_id: str
    usd_per_seat_year: Decimal
    source: str
    simulated: bool
    cost_usd: Decimal


class PriceProvider(Protocol):
    """Something that can return a seat quote."""

    def quote(self, vendor_id: str) -> Quote:
        """Return a quote for `vendor_id`."""
