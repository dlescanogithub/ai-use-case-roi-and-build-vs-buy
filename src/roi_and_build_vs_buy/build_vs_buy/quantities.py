"""Dated numeric inputs. Every figure carries a source, a date, and an estimate flag."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from roi_and_build_vs_buy.assumptions import marker as shared_marker
from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError

MONEY_UNIT = "USD"


@dataclass(frozen=True)
class Quantity:
    """A single sourced number."""

    value: Decimal
    unit: str
    source: str
    date: str
    estimate: bool

    @property
    def marker(self) -> str:
        """Label used in reports."""

        return shared_marker(estimate=self.estimate)


def parse_decimal(raw: object, path: str) -> Decimal:
    """Parse a YAML number or numeric string into Decimal."""

    if isinstance(raw, bool) or raw is None:
        raise ValidationError([f"{path} must be a number"])
    if isinstance(raw, (int, float, str, Decimal)):
        try:
            value = Decimal(str(raw))
        except (InvalidOperation, ValueError) as exc:
            raise ValidationError([f"{path} is not a number"]) from exc
        if not value.is_finite():
            raise ValidationError([f"{path} must be finite"])
        return value
    raise ValidationError([f"{path} must be a number"])


def parse_quantity(raw: object, path: str) -> Quantity:
    """Parse a quantity envelope `{value, unit, source, date, estimate}`."""

    if not isinstance(raw, dict):
        raise ValidationError([f"{path} must be a mapping with value, unit, source, date, estimate"])
    missing = [key for key in ("value", "unit", "source", "date", "estimate") if key not in raw]
    if missing:
        raise ValidationError([f"{path} is missing {', '.join(missing)}"])
    value = parse_decimal(raw["value"], f"{path}.value")
    unit = raw["unit"]
    source = raw["source"]
    date = raw["date"]
    estimate = raw["estimate"]
    errors: list[str] = []
    if not isinstance(unit, str) or not unit.strip():
        errors.append(f"{path}.unit must be a non-empty string")
        unit = ""
    if not isinstance(source, str) or not source.strip():
        errors.append(f"{path}.source must be a non-empty string")
        source = ""
    if not isinstance(date, str) or not _valid_date(date):
        errors.append(f"{path}.date must be a real YYYY-MM-DD date")
        date = ""
    if not isinstance(estimate, bool):
        errors.append(f"{path}.estimate must be true or false")
        estimate = True
    if value < 0:
        errors.append(f"{path}.value must be >= 0")
    if errors:
        raise ValidationError(errors)
    quantity = Quantity(
        value=value,
        unit=unit,
        source=source.strip(),
        date=date,
        estimate=estimate,
    )
    _reject_unsourced_real_price(quantity, path)
    return quantity


def _valid_date(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _reject_unsourced_real_price(quantity: Quantity, path: str) -> None:
    """Reject a price that claims to be real without an official URL and a date.

    `estimate: false` means the author is asserting a real public price. That
    assertion is accepted only when `source` contains an https URL and `date`
    is already valid. Illustrative figures use `estimate: true` and stay [EST].
    """

    if quantity.unit != MONEY_UNIT or quantity.estimate:
        return
    if "https://" not in quantity.source:
        raise ValidationError(
            [f"{path} looks like a real price (estimate: false) and has no https source URL and dated citation"]
        )
