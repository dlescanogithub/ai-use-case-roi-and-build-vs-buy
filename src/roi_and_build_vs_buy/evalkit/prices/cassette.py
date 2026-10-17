"""Replay a JSON cassette of fictional quotes. No network."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.evalkit.prices.base import Quote


class CassettePriceProvider:
    """Replay quotes from a JSON object keyed by vendor id."""

    def __init__(self, path: Path) -> None:
        raw: object = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValidationError([f"{path} cassette must be a JSON object"])
        self._quotes: dict[str, Quote] = {}
        for key, value in raw.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                raise ValidationError([f"{path} has an invalid cassette entry"])
            self._quotes[key] = _parse_quote(key, value, path)

    def quote(self, vendor_id: str) -> Quote:
        try:
            return self._quotes[vendor_id]
        except KeyError as exc:
            raise ValidationError([f"cassette has no quote for {vendor_id}"]) from exc


def _parse_quote(vendor_id: str, node: dict[object, object], path: Path) -> Quote:
    amount = node.get("usd_per_seat_year")
    source = node.get("source")
    simulated = node.get("simulated")
    if isinstance(amount, bool) or not isinstance(amount, (int, float, str)):
        raise ValidationError([f"{path} {vendor_id} usd_per_seat_year is missing"])
    if not isinstance(source, str) or not source.strip():
        raise ValidationError([f"{path} {vendor_id} source is missing"])
    if simulated is not True:
        raise ValidationError([f"{path} {vendor_id} must set simulated: true"])
    return Quote(
        vendor_id=vendor_id,
        usd_per_seat_year=Decimal(str(amount)),
        source=source.strip(),
        simulated=True,
        cost_usd=Decimal(0),
    )
