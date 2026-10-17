"""The 23-case eval bill stays separate from the invented case inputs."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from roi_and_build_vs_buy.roi.measured_cost import (
    MeasuredCostError,
    list_price_usd,
    load_measured_eval_sample,
    per_case_est,
    render_measured_markdown,
)

ROOT = Path(__file__).parents[1]


def test_recorded_sample_is_labeled_and_not_the_list_price() -> None:
    sample = load_measured_eval_sample(ROOT / "assumptions" / "measured_eval_run_cost.yaml")
    assert sample.commit == "c1efdfd"
    assert sample.measured_on == "2026-10-17"
    assert sample.provider == "xAI"
    assert sample.cases == 23
    assert sample.conversion_formula == "per_production_item_usd = billed_eval_run_usd / 23"
    non_reasoning, grok = sample.runs
    assert non_reasoning.billed_usd_low == Decimal("0.036")
    assert non_reasoning.billed_usd_high == Decimal("0.037")
    assert non_reasoning.input_tokens_low == 66000
    assert non_reasoning.input_tokens_high == 70000
    assert non_reasoning.output_tokens_low == 3000
    assert non_reasoning.output_tokens_high == 3400
    assert grok.billed_usd_low == Decimal("0.072")
    assert grok.input_tokens_low == 62700
    assert grok.output_tokens_low == 14500
    assert grok.reasoning_tokens == 11600
    price = sample.price_for("grok-4.3")
    reconstructed = list_price_usd(62700, 14500, price)
    assert reconstructed == Decimal("62700") * Decimal("1.25") / Decimal(1_000_000) + Decimal("14500") * Decimal(
        "2.50"
    ) / Decimal(1_000_000)
    assert reconstructed != Decimal("0.072")
    assert per_case_est(Decimal("0.072"), 23) == Decimal("0.072") / Decimal(23)
    assert per_case_est(Decimal("0.036"), 23) == Decimal("0.036") / Decimal(23)
    note = render_measured_markdown()
    assert "c1efdfd" in note
    assert "[EST]" in note
    assert "not applied" in note
    assert "US$0.036-0.037" in note
    assert "US$0.072" in note
    spanish = render_measured_markdown(lang="es")
    assert "23" in spanish
    assert "[EST]" in spanish
    with pytest.raises(ValueError):
        render_measured_markdown(lang="fr")
    with pytest.raises(MeasuredCostError):
        per_case_est(Decimal("1"), 0)


def test_stub_and_bad_records_are_refused(tmp_path: Path) -> None:
    with pytest.raises(MeasuredCostError):
        load_measured_eval_sample(ROOT / "assumptions" / "measured_per_run_cost.stub.yaml")
    broken = tmp_path / "bad.yaml"
    broken.write_text("status: measured\nkind: other\n", encoding="utf-8")
    with pytest.raises(MeasuredCostError):
        load_measured_eval_sample(broken)
