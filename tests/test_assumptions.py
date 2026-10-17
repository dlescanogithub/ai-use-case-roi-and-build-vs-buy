from __future__ import annotations

from pathlib import Path

import pytest

from roi_model.assumptions import (
    AssumptionError,
    apply_measured_cost,
    apply_parameter,
    assumptions_from_case,
    load_case,
)

ROOT = Path(__file__).parents[1]


def test_refund_and_weekly_cases_load() -> None:
    refund = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    weekly = load_case(ROOT / "assumptions" / "weekly_report.yaml")
    assert refund.meta.fictional is True
    assert refund.meta.status == "implemented"
    assert refund.volume_mode == "daily"
    assert weekly.volume_mode == "monthly"
    assert "[EST]" in refund.parameters["volume_per_day"].rationale
    assert refund.parameters["volume_per_day"].illustrative is True
    assert all(spec.illustrative for spec in weekly.parameters.values())
    assumptions = assumptions_from_case(refund)
    assert assumptions.volume_per_day == pytest.approx(120)
    assert assumptions.agent_cost_per_run > 0


def test_measured_override_replaces_token_price() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    base = assumptions_from_case(case)
    path = ROOT / "assumptions" / "measured_override_test.yaml"
    path.write_text(
        "\n".join(
            [
                "status: measured",
                "agent_cost_per_run: 0.25",
                "source: measured locally, not a vendor price",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    try:
        updated = apply_measured_cost(base, path)
    finally:
        path.unlink()
    assert updated.agent_cost_per_run == pytest.approx(0.25)


def test_eval_run_bill_is_not_applied_as_a_per_item_cost() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    base = assumptions_from_case(case)
    with pytest.raises(AssumptionError, match="not a per-item override"):
        apply_measured_cost(base, ROOT / "assumptions" / "measured_eval_run_cost.yaml")


def test_illustrative_flag_is_required(tmp_path: Path) -> None:
    text = (ROOT / "assumptions" / "weekly_report.yaml").read_text(encoding="utf-8")
    path = tmp_path / "missing.yaml"
    path.write_text(text.replace("    illustrative: true\n", "", 1), encoding="utf-8")
    with pytest.raises(AssumptionError, match="illustrative"):
        load_case(path)


def test_stub_measured_file_is_refused() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    base = assumptions_from_case(case)
    with pytest.raises(AssumptionError, match="status"):
        apply_measured_cost(base, ROOT / "assumptions" / "measured_per_run_cost.stub.yaml")


def test_bad_schema_version(tmp_path: Path) -> None:
    broken = tmp_path / "broken.yaml"
    broken.write_text("schema_version: 2\n", encoding="utf-8")
    with pytest.raises(AssumptionError):
        load_case(broken)


def test_apply_parameter_rejects_unknown_names() -> None:
    case = load_case(ROOT / "assumptions" / "weekly_report.yaml")
    assumptions = assumptions_from_case(case)
    with pytest.raises(AssumptionError):
        apply_parameter(assumptions, "agent_cost_per_run", 1)
    updated = apply_parameter(assumptions, "volume_per_month", 8)
    assert updated.volume_per_month == pytest.approx(8)


def test_scenario_override_out_of_domain_fails(tmp_path: Path) -> None:
    text = (ROOT / "assumptions" / "weekly_report.yaml").read_text(encoding="utf-8")
    text = text.replace("loaded_cost_per_hour: 15", "review_rate: 2")
    path = tmp_path / "bad.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(AssumptionError):
        load_case(path)
