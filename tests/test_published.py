"""Committed one-pagers and JSON stay aligned with the formula."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from roi_and_build_vs_buy.roi.assumptions import assumptions_from_case, load_case
from roi_and_build_vs_buy.roi.model import build_result
from roi_and_build_vs_buy.roi.report import money

ROOT = Path(__file__).parents[1]


def test_committed_refund_and_weekly_match_the_model() -> None:
    for case_name, summary_name, pager in (
        ("refund_desk.yaml", "refund_desk.json", "ONE_PAGER_EN.md"),
        ("weekly_report.yaml", "weekly_report.json", "ONE_PAGER_WEEKLY_EN.md"),
    ):
        case = load_case(ROOT / "assumptions" / case_name)
        result = build_result(assumptions_from_case(case))
        summary = json.loads((ROOT / "docs" / "results" / summary_name).read_text(encoding="utf-8"))
        assert summary["simulated"] is True
        assert summary["inputs"] == "EST"
        assert summary["npv_3y"] == pytest.approx(result.npv)
        assert summary["net_monthly_savings_steady"] == pytest.approx(result.net_monthly_steady)
        assert summary["payback_months"] == pytest.approx(result.payback.months)
        assert summary["break_even_volume"] == pytest.approx(result.break_even_volume)
        text = (ROOT / "docs" / pager).read_text(encoding="utf-8")
        assert text.startswith("Illustrative numbers, replace with your own\n")
        assert money(result.npv, case.meta.currency) in text
        assert "[EST]" in text
        assert "illustrative" in text
        assert "What the model says" in text
    assert not (ROOT / "docs" / "ONE_PAGER_ES.md").exists()
    assert not (ROOT / "docs" / "ONE_PAGER_WEEKLY_ES.md").exists()
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    refund = build_result(assumptions_from_case(load_case(ROOT / "assumptions" / "refund_desk.yaml")))
    assert readme.startswith("Illustrative numbers, replace with your own\n")
    assert money(refund.npv, "USD") in readme
