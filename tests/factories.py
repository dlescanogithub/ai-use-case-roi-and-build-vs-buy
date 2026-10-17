"""Small assumption objects for hand-computed cases."""

from __future__ import annotations

from roi_and_build_vs_buy.roi.assumptions import Assumptions


def hand_assumptions(**overrides: float | int | str | None) -> Assumptions:
    base: dict[str, float | int | str | None] = {
        "volume_per_day": None,
        "volume_per_month": 10.0,
        "working_days_per_month": 0.0,
        "manual_minutes_per_item": 60.0,
        "loaded_cost_per_hour": 60.0,
        "manual_error_rate": 0.0,
        "agent_error_rate": 0.0,
        "cost_of_error": 0.0,
        "input_tokens": 0.0,
        "output_tokens": 0.0,
        "input_price_per_million": 0.0,
        "output_price_per_million": 0.0,
        "agent_cost_per_run_override": 10.0,
        "review_minutes": 0.0,
        "review_rate": 0.0,
        "implementation_cost": 100.0,
        "monthly_run_cost": 0.0,
        "adoption_ramp_months": 0.0,
        "discount_rate_annual": 0.0,
        "horizon_months": 2,
        "currency": "USD",
        "case_id": "hand",
    }
    base.update(overrides)
    return Assumptions(**base)  # type: ignore[arg-type]
