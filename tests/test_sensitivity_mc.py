from __future__ import annotations

from pathlib import Path

import pytest

from roi_model.assumptions import load_case
from roi_model.montecarlo import percentile, run_monte_carlo, spearman
from roi_model.sensitivity import scenarios, tornado
from roi_model.svgchart import tornado_svg

ROOT = Path(__file__).parents[1]


def test_tornado_is_sorted_and_svg_mentions_a_driver() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    rows = tornado(case)
    swings = [row.abs_swing for row in rows]
    assert swings == sorted(swings, reverse=True)
    assert rows[0].abs_swing >= rows[-1].abs_swing
    chart = tornado_svg(rows)
    assert chart.startswith("<svg")
    assert rows[0].name in chart
    assert tornado_svg(()).startswith("<svg")


def test_named_scenarios_run() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    outcomes = {item.name: item.result.npv for item in scenarios(case)}
    assert set(outcomes) == {"pessimistic", "base", "optimistic"}
    assert outcomes["optimistic"] > outcomes["base"] > outcomes["pessimistic"]


def test_percentile_and_spearman_known_values() -> None:
    assert percentile([1, 2, 3, 4], 50) == pytest.approx(2.5)
    assert percentile([5], 10) == 5
    assert spearman([1, 2, 3], [1, 2, 3]) == pytest.approx(1)
    assert spearman([1, 1, 1], [1, 2, 3]) == pytest.approx(0)
    with pytest.raises(ValueError):
        percentile([], 10)
    with pytest.raises(ValueError):
        spearman([1], [1, 2])


def test_monte_carlo_is_reproducible_and_ordered() -> None:
    case = load_case(ROOT / "assumptions" / "refund_desk.yaml")
    left = run_monte_carlo(case, draws=80, seed=42)
    right = run_monte_carlo(case, draws=80, seed=42)
    other = run_monte_carlo(case, draws=80, seed=99)
    assert left.npv_p10 == right.npv_p10
    assert left.npv_p50 == right.npv_p50
    assert left.npv_p90 == right.npv_p90
    assert left.npv_p10 <= left.npv_p50 <= left.npv_p90
    assert (other.npv_p50, other.npv_p10) != (left.npv_p50, left.npv_p10)
    assert left.drivers
    with pytest.raises(ValueError):
        run_monte_carlo(case, draws=0, seed=1)
