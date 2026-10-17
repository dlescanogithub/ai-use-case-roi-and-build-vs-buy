from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import yaml

from roi_and_build_vs_buy.build_vs_buy.case import load_case
from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.prices import validate_tree
from roi_and_build_vs_buy.build_vs_buy.tco import load_tco, probe_monotonicity, project

ROOT = Path(__file__).resolve().parents[1]


def _qty(value: str, unit: str) -> dict[str, object]:
    return {
        "value": value,
        "unit": unit,
        "source": "fictional planning assumption for a unit test",
        "date": "2026-10-17",
        "estimate": True,
    }


def _tiny_model() -> dict[str, object]:
    return {
        "case_id": "tiny",
        "org": "Tiny Co-op",
        "title": "Tiny case",
        "as_of": "2026-10-17",
        "currency": "USD",
        "horizon_years": 3,
        "fictional": True,
        "simulated": True,
        "assumptions": {"volume_growth_per_year": _qty("0", "fraction")},
        "build": {
            "engineering_hours": _qty("10", "hours"),
            "engineering_rate_per_hour": _qty("100", "USD"),
            "infra_per_year": _qty("100", "USD"),
            "runs_per_year": _qty("1000", "runs"),
            "tokens_per_run": _qty("1000", "tokens"),
            "cost_per_1k_tokens": _qty("1", "USD"),
            "maintenance_pct_of_initial_build": _qty("0.10", "fraction"),
            "eval_ops_hours_per_year": _qty("0", "hours"),
            "review_hours_per_year": _qty("0", "hours"),
        },
        "buy_options": [
            {
                "id": "vendor_a",
                "label": "Vendor A",
                "vendor": "Vendor A",
                "seats": _qty("1", "seats"),
                "license_per_seat_per_year": _qty("500", "USD"),
                "integration_hours": _qty("2", "hours"),
                "integration_rate_per_hour": _qty("100", "USD"),
                "exit_cost": _qty("50", "USD"),
                "annual_price_increase": _qty("0", "fraction"),
                "usage_tiers": [
                    {"up_to_runs": None, "price_per_run": _qty("0.10", "USD")},
                ],
            }
        ],
        "scenarios": [
            {
                "id": "base",
                "label": "Base",
                "engineering_hours_multiplier": "1",
                "runs_multiplier": "1",
                "annual_price_increase_override": None,
            }
        ],
    }


def test_tiny_tco_matches_hand_calculation(tmp_path: Path) -> None:
    path = tmp_path / "tco.yaml"
    path.write_text(yaml.safe_dump(_tiny_model()), encoding="utf-8")
    model = load_tco(path)
    projection = project(model, "base")
    build = projection.option("build")
    buy = projection.option("vendor_a")
    assert [year.cumulative for year in build.years] == [
        Decimal("2100.00"),
        Decimal("3300.00"),
        Decimal("4500.00"),
    ]
    assert buy.operating_total == Decimal("2000.00")
    assert buy.total_with_exit == Decimal("2050.00")
    assert projection.break_evens[0].operating_crossover_year is None
    assert probe_monotonicity(model) == []


def test_crossover_in_year_two(tmp_path: Path) -> None:
    raw = _tiny_model()
    build = raw["build"]
    assert isinstance(build, dict)
    build["engineering_hours"] = _qty("1", "hours")
    build["infra_per_year"] = _qty("0", "USD")
    build["runs_per_year"] = _qty("0", "runs")
    build["cost_per_1k_tokens"] = _qty("0", "USD")
    build["maintenance_pct_of_initial_build"] = _qty("0", "fraction")
    buy_options = raw["buy_options"]
    assert isinstance(buy_options, list)
    offer = buy_options[0]
    assert isinstance(offer, dict)
    offer["license_per_seat_per_year"] = _qty("80", "USD")
    offer["integration_hours"] = _qty("0", "hours")
    offer["exit_cost"] = _qty("0", "USD")
    offer["usage_tiers"] = [{"up_to_runs": None, "price_per_run": _qty("0", "USD")}]
    path = tmp_path / "tco.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    projection = project(load_tco(path), "base")
    assert projection.break_evens[0].operating_crossover_year == 2


def test_examples_are_monotonic() -> None:
    for name in ("bruma_freight", "cedro_records"):
        model = load_case(ROOT / "examples" / name).tco
        assert probe_monotonicity(model) == []
        base = project(model, "base")
        assert base.options[0].option_id == "build"


def test_bare_price_is_rejected() -> None:
    try:
        validate_tree({"license": 4200, "horizon_years": 3}, "sample")
    except ValidationError as exc:
        assert any("bare number" in item for item in exc.errors)
    else:
        raise AssertionError("expected a bare-number failure")


def test_real_looking_price_without_url_is_rejected() -> None:
    node = {
        "license_per_seat_per_year": {
            "value": "19.99",
            "unit": "USD",
            "source": "vendor price list",
            "date": "2026-10-17",
            "estimate": False,
        }
    }
    try:
        validate_tree(node, "sample")
    except ValidationError as exc:
        assert any("real price" in item for item in exc.errors)
    else:
        raise AssertionError("expected a provenance failure")


def test_sourced_https_price_is_accepted() -> None:
    node = {
        "license_per_seat_per_year": {
            "value": "19.99",
            "unit": "USD",
            "source": "https://example.invalid/pricing accessed for a fixture",
            "date": "2026-10-17",
            "estimate": False,
        }
    }
    validate_tree(node, "sample")


def test_bad_date_is_rejected() -> None:
    node = {
        "infra_per_year": {
            "value": "10",
            "unit": "USD",
            "source": "fictional planning assumption for a unit test",
            "date": "2026-13-40",
            "estimate": True,
        }
    }
    try:
        validate_tree(node, "sample")
    except ValidationError as exc:
        assert any("date" in item for item in exc.errors)
    else:
        raise AssertionError("expected a date failure")
