"""Monthly ROI model.

Definitions (see docs/adr/0002-quality-adjusted-savings.md):

* Manual cost per item = labor + expected cost of manual errors.
* Agent cost per completed item = token cost + reviewer time.
* Residual error cost is subtracted in quality-adjusted savings.
* Fixed monthly run cost is charged in full from month 1 (it does not scale with adoption).
* Break-even volume is the steady-state monthly volume where net savings are zero.
* Payback searches up to 360 months and is explicit when the case never pays back.
* NPV discounts monthly cash flows over the case horizon. Implementation sits at month 0.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from roi_model.assumptions import Assumptions, validate_assumptions

PAYBACK_SEARCH_MONTHS = 360
PaybackStatus = Literal["immediate", "pays_back", "never"]


@dataclass(frozen=True)
class UnitEconomics:
    manual_labor_cost: float
    manual_error_cost: float
    manual_cost: float
    agent_run_cost: float
    review_cost: float
    residual_error_cost: float
    gross_operating_savings: float
    quality_adjusted_savings: float
    cost_per_completed_item: float


@dataclass(frozen=True)
class Payback:
    status: PaybackStatus
    months: float | None
    reason: str


@dataclass(frozen=True)
class ModelResult:
    unit: UnitEconomics
    monthly_volume_steady: float
    net_monthly_steady: float
    break_even_volume: float | None
    break_even_reason: str
    payback: Payback
    npv: float
    cashflows: tuple[float, ...]
    monthly_discount_rate: float


def unit_economics(assumptions: Assumptions) -> UnitEconomics:
    labor = assumptions.manual_minutes_per_item / 60.0 * assumptions.loaded_cost_per_hour
    manual_error = assumptions.manual_error_rate * assumptions.cost_of_error
    manual_cost = labor + manual_error
    agent_run = assumptions.agent_cost_per_run
    review = assumptions.review_rate * (assumptions.review_minutes / 60.0) * assumptions.loaded_cost_per_hour
    residual = assumptions.agent_error_rate * assumptions.cost_of_error
    gross = manual_cost - (agent_run + review)
    return UnitEconomics(
        manual_labor_cost=labor,
        manual_error_cost=manual_error,
        manual_cost=manual_cost,
        agent_run_cost=agent_run,
        review_cost=review,
        residual_error_cost=residual,
        gross_operating_savings=gross,
        quality_adjusted_savings=gross - residual,
        cost_per_completed_item=agent_run + review,
    )


def steady_monthly_volume(assumptions: Assumptions) -> float:
    if assumptions.volume_per_month is not None:
        return assumptions.volume_per_month
    assert assumptions.volume_per_day is not None
    return assumptions.volume_per_day * assumptions.working_days_per_month


def adoption_at_month(ramp_months: float, month: int) -> float:
    """Linear ramp. Month is 1-based. A ramp of 0 means full adoption immediately."""
    if month < 1:
        raise ValueError("month must be >= 1")
    if ramp_months <= 0:
        return 1.0
    return min(1.0, month / ramp_months)


def net_monthly(volume: float, unit_savings: float, fixed_cost: float) -> float:
    return volume * unit_savings - fixed_cost


def monthly_discount_rate(annual: float) -> float:
    return float((1.0 + annual) ** (1.0 / 12.0) - 1.0)


def cashflow_for_month(assumptions: Assumptions, unit_savings: float, month: int) -> float:
    volume = steady_monthly_volume(assumptions) * adoption_at_month(assumptions.adoption_ramp_months, month)
    return net_monthly(volume, unit_savings, assumptions.monthly_run_cost)


def break_even(unit_savings: float, fixed_cost: float) -> tuple[float | None, str]:
    """Operating break-even. Implementation cost is not part of this volume."""
    if unit_savings > 0:
        return (
            fixed_cost / unit_savings,
            "steady-state monthly volume where net monthly savings are zero",
        )
    if unit_savings == 0 and fixed_cost == 0:
        return 0.0, "unit savings and fixed cost are both zero, so every volume breaks even"
    if unit_savings == 0:
        return (
            None,
            "unit savings are zero and fixed cost is positive; there is no break-even volume",
        )
    return (
        None,
        "unit savings are negative; more volume lowers savings and there is no break-even volume",
    )


def payback_for(assumptions: Assumptions, unit_savings: float) -> Payback:
    steady = net_monthly(steady_monthly_volume(assumptions), unit_savings, assumptions.monthly_run_cost)
    if assumptions.implementation_cost == 0:
        first = cashflow_for_month(assumptions, unit_savings, 1)
        if first >= 0:
            return Payback(
                status="immediate",
                months=0.0,
                reason="no implementation cost and the first month is not negative",
            )
    if steady <= 0 and assumptions.implementation_cost > 0:
        return Payback(
            status="never",
            months=None,
            reason=("steady-state net monthly savings are not positive; the case never pays back"),
        )
    cumulative = -assumptions.implementation_cost
    for month in range(1, PAYBACK_SEARCH_MONTHS + 1):
        cashflow = cashflow_for_month(assumptions, unit_savings, month)
        previous = cumulative
        cumulative += cashflow
        if cumulative >= 0:
            fraction = 0.0 if cashflow <= 0 else -previous / cashflow
            fraction = min(1.0, max(0.0, fraction))
            return Payback(
                status="pays_back",
                months=(month - 1) + fraction,
                reason="cumulative cash flow reaches zero inside the search window",
            )
    return Payback(
        status="never",
        months=None,
        reason=(f"cumulative cash flow did not reach zero within {PAYBACK_SEARCH_MONTHS} months"),
    )


def npv_for(assumptions: Assumptions, unit_savings: float) -> tuple[float, tuple[float, ...], float]:
    rate = monthly_discount_rate(assumptions.discount_rate_annual)
    flows: list[float] = []
    total = -assumptions.implementation_cost
    for month in range(1, assumptions.horizon_months + 1):
        cashflow = cashflow_for_month(assumptions, unit_savings, month)
        flows.append(cashflow)
        total += cashflow / (1.0 + rate) ** month
    return total, tuple(flows), rate


def build_result(assumptions: Assumptions, *, savings_override: float | None = None) -> ModelResult:
    """Evaluate one case.

    ``savings_override`` exists so the forced-regression fixture can inject a
    deliberately wrong unit saving. The CLI never sets it.
    """
    validate_assumptions(assumptions)
    unit = unit_economics(assumptions)
    if savings_override is not None:
        unit = replace(unit, quality_adjusted_savings=savings_override)
    savings = unit.quality_adjusted_savings
    volume = steady_monthly_volume(assumptions)
    net = net_monthly(volume, savings, assumptions.monthly_run_cost)
    be_volume, be_reason = break_even(savings, assumptions.monthly_run_cost)
    payback = payback_for(assumptions, savings)
    npv, flows, rate = npv_for(assumptions, savings)
    return ModelResult(
        unit=unit,
        monthly_volume_steady=volume,
        net_monthly_steady=net,
        break_even_volume=be_volume,
        break_even_reason=be_reason,
        payback=payback,
        npv=npv,
        cashflows=flows,
        monthly_discount_rate=rate,
    )
