from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

import roi_and_build_vs_buy.build_vs_buy.__main__ as entrypoint
from roi_and_build_vs_buy.build_vs_buy.config import load_settings
from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError, ValidationError
from roi_and_build_vs_buy.build_vs_buy.matrix import load_weights
from roi_and_build_vs_buy.build_vs_buy.prices import validate_tree
from roi_and_build_vs_buy.build_vs_buy.quantities import parse_decimal, parse_quantity
from roi_and_build_vs_buy.build_vs_buy.tco import load_tco, project
from roi_and_build_vs_buy.build_vs_buy.yaml_io import load_mapping
from roi_and_build_vs_buy.evalkit.prices.cassette import CassettePriceProvider
from roi_and_build_vs_buy.evalkit.prices.fake import FakePriceProvider
from roi_and_build_vs_buy.evalkit.prices.http import HttpPriceProvider
from roi_and_build_vs_buy.evalkit.trace import append_trace, read_trace
from roi_and_build_vs_buy.retry import retry_call
from roi_and_build_vs_buy.secretscan import main as scan_main

ROOT = Path(__file__).resolve().parents[1]


def test_entrypoint_imports() -> None:
    assert callable(entrypoint.main)


def test_trace_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "trace.jsonl"
    append_trace(path, {"case_id": "tiny", "external_action": False})
    rows = read_trace(path)
    assert rows[0]["case_id"] == "tiny"
    assert read_trace(tmp_path / "missing.jsonl") == []


def test_config_rejects_bad_bounds() -> None:
    with pytest.raises(DecisionKitError):
        load_settings({"DECIDE_MAX_ATTEMPTS": "9"})
    with pytest.raises(DecisionKitError):
        load_settings({"DECIDE_MAX_ATTEMPTS": "nope"})
    with pytest.raises(DecisionKitError):
        load_settings({"DECIDE_BACKOFF_CAP_SECONDS": "0"})
    with pytest.raises(DecisionKitError):
        load_settings({"DECIDE_COST_CAP_USD": "-1"})
    with pytest.raises(DecisionKitError):
        load_settings({"DECIDE_LOG_LEVEL": "LOUD"})


def test_retry_rejects_bad_arguments() -> None:
    with pytest.raises(ValueError):
        retry_call(lambda: "x", max_attempts=0, backoff_cap=1)
    with pytest.raises(ValueError):
        retry_call(lambda: "x", max_attempts=1, backoff_cap=-1)


def test_yaml_and_weight_errors(tmp_path: Path) -> None:
    missing = tmp_path / "nope.yaml"
    with pytest.raises(ValidationError):
        load_mapping(missing)
    bad = tmp_path / "list.yaml"
    bad.write_text("- 1\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_mapping(bad)
    weights = tmp_path / "weights.yaml"
    weights.write_text("case_id: x\n", encoding="utf-8")
    with pytest.raises(ValidationError):
        load_weights(weights)


def test_quantity_and_tree_errors() -> None:
    with pytest.raises(ValidationError):
        parse_decimal("nope", "field")
    with pytest.raises(ValidationError):
        parse_quantity(
            {
                "value": "-1",
                "unit": "USD",
                "source": "x",
                "date": "2026-10-17",
                "estimate": True,
            },
            "p",
        )
    with pytest.raises(ValidationError):
        validate_tree({"horizon_years": "3"}, "sample")
    with pytest.raises(ValidationError):
        validate_tree([1], "sample")


def test_cassette_and_http_errors(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(ValidationError):
        CassettePriceProvider(path)
    path.write_text(
        json.dumps({"vendor_a": {"usd_per_seat_year": "1", "source": "x", "simulated": False}}),
        encoding="utf-8",
    )
    with pytest.raises(ValidationError):
        CassettePriceProvider(path)
    good = tmp_path / "good.json"
    good.write_text(
        json.dumps({"vendor_a": {"usd_per_seat_year": "1", "source": "cassette", "simulated": True}}),
        encoding="utf-8",
    )
    provider = CassettePriceProvider(good)
    with pytest.raises(ValidationError):
        provider.quote("missing")
    assert FakePriceProvider().quote("vendor_a").simulated is True
    with pytest.raises(DecisionKitError):
        HttpPriceProvider("", "", transport=lambda _u, _h: {}, max_attempts=1, backoff_cap=0.1)

    def bad_transport(_url: str, _headers: dict[str, str]) -> dict[str, object]:
        return {"nope": True}

    http = HttpPriceProvider(
        "https://example.invalid",
        "key",
        transport=bad_transport,
        max_attempts=1,
        backoff_cap=0.1,
        sleep=lambda _seconds: None,
    )
    with pytest.raises(DecisionKitError):
        http.quote("vendor_a")


def test_unknown_scenario_is_rejected() -> None:
    model = load_tco(ROOT / "examples" / "bruma_freight" / "tco.yaml")
    with pytest.raises(ValidationError):
        project(model, "missing")


def test_secret_scan_cli(tmp_path: Path) -> None:
    clean = tmp_path / "notes.txt"
    clean.write_text("no secrets here\n", encoding="utf-8")
    assert scan_main([str(clean)]) == 0
    dirty = tmp_path / "leak.txt"
    dirty.write_text("AKIA" + "A" * 16, encoding="utf-8")
    assert scan_main([str(dirty)]) == 1


def test_real_provider_without_transport_is_refused() -> None:
    from roi_and_build_vs_buy.evalkit.prices import build_provider

    settings = load_settings(
        {
            "DECIDE_REAL_PROVIDER": "1",
            "DECIDE_PROVIDER_BASE_URL": "https://example.invalid",
            "DECIDE_PROVIDER_API_KEY": "k",
        }
    )
    with pytest.raises(DecisionKitError):
        build_provider(settings)


def test_parse_decimal_rejects_bool() -> None:
    with pytest.raises(ValidationError):
        parse_decimal(True, "flag")
    assert parse_decimal(Decimal("1.5"), "ok") == Decimal("1.5")
