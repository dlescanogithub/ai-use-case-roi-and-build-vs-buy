from __future__ import annotations

import pytest
from tests.factories import hand_assumptions

from roi_and_build_vs_buy.roi.assumptions import AssumptionError, scale_volume
from roi_and_build_vs_buy.roi.model import (
    adoption_at_month,
    build_result,
    monthly_discount_rate,
)


def test_hand_computed_npv_payback_and_break_even() -> None:
    # Labor 60, agent override 10, no errors, no review.
    # Unit savings = 50. Volume 10. Fixed cost 0. Implementation 100. Discount 0.
    # Cash flow = 500 per month. NPV over 2 months = -100 + 500 + 500 = 900.
    # Payback fraction = 100 / 500 = 0.2. Break-even volume = 0.
    result = build_result(hand_assumptions())
    assert result.unit.manual_labor_cost == pytest.approx(60)
    assert result.unit.quality_adjusted_savings == pytest.approx(50)
    assert result.unit.cost_per_completed_item == pytest.approx(10)
    assert result.net_monthly_steady == pytest.approx(500)
    assert result.npv == pytest.approx(900)
    assert result.payback.status == "pays_back"
    assert result.payback.months == pytest.approx(0.2)
    assert result.break_even_volume == pytest.approx(0)


def test_ramp_payback_is_fractional() -> None:
    # Savings 50, volume 100, fixed 0, implementation 3000, ramp 2 months, discount 0.
    # Month 1 cash flow = 2500. Cumulative = -500.
    # Month 2 cash flow = 5000. Fraction = 0.1. Payback = 1.1.
    result = build_result(
        hand_assumptions(
            volume_per_month=100,
            implementation_cost=3000,
            adoption_ramp_months=2,
            horizon_months=2,
        )
    )
    assert result.cashflows[0] == pytest.approx(2500)
    assert result.cashflows[1] == pytest.approx(5000)
    assert result.payback.months == pytest.approx(1.1)
    assert result.npv == pytest.approx(4500)


def test_payback_never_when_steady_state_is_not_positive() -> None:
    result = build_result(
        hand_assumptions(
            manual_minutes_per_item=0,
            agent_cost_per_run_override=5,
            monthly_run_cost=20,
            implementation_cost=1000,
        )
    )
    assert result.unit.quality_adjusted_savings < 0
    assert result.payback.status == "never"
    assert result.payback.months is None
    assert "never pays back" in result.payback.reason
    assert result.break_even_volume is None


def test_payback_never_inside_search_window() -> None:
    # One unit of savings per month cannot repay 500 within 360 months.
    result = build_result(
        hand_assumptions(
            volume_per_month=1,
            manual_minutes_per_item=60,
            loaded_cost_per_hour=1,
            agent_cost_per_run_override=0,
            implementation_cost=500,
        )
    )
    assert result.net_monthly_steady == pytest.approx(1)
    assert result.payback.status == "never"
    assert "360" in result.payback.reason


def test_immediate_payback_when_there_is_no_implementation_cost() -> None:
    result = build_result(hand_assumptions(implementation_cost=0))
    assert result.payback.status == "immediate"
    assert result.payback.months == pytest.approx(0)


def test_zero_savings_and_zero_fixed_cost_break_even() -> None:
    result = build_result(
        hand_assumptions(
            manual_minutes_per_item=0,
            agent_cost_per_run_override=0,
            implementation_cost=0,
            monthly_run_cost=0,
        )
    )
    assert result.break_even_volume == pytest.approx(0)
    assert result.payback.status == "immediate"


def test_zero_unit_savings_with_fixed_cost_has_no_break_even() -> None:
    result = build_result(
        hand_assumptions(
            manual_minutes_per_item=0,
            agent_cost_per_run_override=0,
            monthly_run_cost=10,
            implementation_cost=0,
        )
    )
    assert result.unit.quality_adjusted_savings == pytest.approx(0)
    assert result.break_even_volume is None
    assert "zero" in result.break_even_reason


def test_more_volume_does_not_lower_savings_when_unit_savings_are_positive() -> None:
    low = build_result(hand_assumptions(volume_per_month=10, monthly_run_cost=25))
    high = build_result(scale_volume(hand_assumptions(volume_per_month=10, monthly_run_cost=25), 2))
    assert high.net_monthly_steady > low.net_monthly_steady


def test_token_price_sets_agent_cost() -> None:
    result = build_result(
        hand_assumptions(
            agent_cost_per_run_override=None,
            input_tokens=2_000_000,
            output_tokens=0,
            input_price_per_million=3,
        )
    )
    assert result.unit.agent_run_cost == pytest.approx(6)


def test_adoption_edges() -> None:
    assert adoption_at_month(0, 1) == 1
    assert adoption_at_month(6, 3) == pytest.approx(0.5)
    assert adoption_at_month(6, 6) == 1
    assert adoption_at_month(6, 7) == 1
    with pytest.raises(ValueError):
        adoption_at_month(6, 0)


def test_discount_rate_zero_is_zero() -> None:
    assert monthly_discount_rate(0) == pytest.approx(0)


def test_validation_rejects_bad_rates_and_volume_mode() -> None:
    with pytest.raises(AssumptionError):
        build_result(hand_assumptions(review_rate=1.2))
    with pytest.raises(AssumptionError):
        build_result(hand_assumptions(volume_per_day=1, volume_per_month=1))
    with pytest.raises(AssumptionError):
        scale_volume(hand_assumptions(), -1)
