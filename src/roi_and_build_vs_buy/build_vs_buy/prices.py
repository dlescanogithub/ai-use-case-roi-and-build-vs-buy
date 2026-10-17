"""Policy-as-code for price and quantity provenance.

Bare numbers are rejected outside scenario knobs. A USD figure with
`estimate: false` and no https URL is rejected as a real-looking price
without a source and a date.
"""

from __future__ import annotations

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.quantities import parse_quantity

_STRUCTURAL_INTS = {"up_to_runs", "horizon_years"}
_ENVELOPE_KEYS = {"value", "unit", "source", "date", "estimate"}


def validate_tree(node: object, path: str = "$", *, in_scenario: bool = False) -> None:
    """Walk a loaded YAML tree and reject unsourced numbers."""

    errors: list[str] = []
    _walk(node, path, in_scenario=in_scenario, errors=errors)
    if errors:
        raise ValidationError(errors)


def _walk(node: object, path: str, *, in_scenario: bool, errors: list[str]) -> None:
    if isinstance(node, dict):
        if "value" in node and set(node.keys()) >= _ENVELOPE_KEYS and not in_scenario:
            try:
                parse_quantity(node, path)
            except ValidationError as exc:
                errors.extend(exc.errors)
            return
        for key, value in node.items():
            if not isinstance(key, str):
                errors.append(f"{path} has a non-string key")
                continue
            child_scenario = in_scenario or key == "scenarios"
            child = f"{path}.{key}"
            if key in _STRUCTURAL_INTS:
                if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
                    errors.append(f"{child} must be an integer or null")
                continue
            if _is_bare_number(value) and not child_scenario:
                errors.append(f"{child} is a bare number; money and drivers must use value/unit/source/date/estimate")
                continue
            _walk(value, child, in_scenario=child_scenario, errors=errors)
        return
    if isinstance(node, list):
        for index, item in enumerate(node):
            _walk(item, f"{path}[{index}]", in_scenario=in_scenario, errors=errors)
        return
    if _is_bare_number(node) and not in_scenario:
        errors.append(f"{path} is a bare number")


def _is_bare_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)
