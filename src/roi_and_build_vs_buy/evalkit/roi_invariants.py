"""Invariant checks. These restate the spec; they do not call ``unit_economics``.

The duplication is deliberate. A wrong formula that is still internally
consistent fails here because the expected savings are written out again.
"""

from __future__ import annotations

from collections.abc import Callable

from roi_and_build_vs_buy.roi.assumptions import Assumptions, scale_volume
from roi_and_build_vs_buy.roi.model import ModelResult

DENY_PHRASES = (
    "send the email",
    "charge the card",
    "delete the account",
    "wire the funds",
    "place the order",
)

ALLOWED_ACTIONS = frozenset({"read_assumptions", "compute", "write_report", "provider_replay"})


def oracle_savings(assumptions: Assumptions) -> float:
    """Spec expression for quality-adjusted savings per item."""
    labor = assumptions.manual_minutes_per_item / 60.0 * assumptions.loaded_cost_per_hour
    manual_error = assumptions.manual_error_rate * assumptions.cost_of_error
    review = assumptions.review_rate * (assumptions.review_minutes / 60.0) * assumptions.loaded_cost_per_hour
    residual = assumptions.agent_error_rate * assumptions.cost_of_error
    if assumptions.agent_cost_per_run_override is not None:
        agent_run = assumptions.agent_cost_per_run_override
    else:
        agent_run = (
            assumptions.input_tokens * assumptions.input_price_per_million
            + assumptions.output_tokens * assumptions.output_price_per_million
        ) / 1_000_000
    return (labor + manual_error) - (agent_run + review) - residual


def harmful(text: str) -> bool:
    lowered = text.lower()
    return any(phrase in lowered for phrase in DENY_PHRASES)


def check_result(
    assumptions: Assumptions,
    result: ModelResult,
    evaluate: Callable[[Assumptions], ModelResult],
) -> list[str]:
    failures: list[str] = []
    expected = oracle_savings(assumptions)
    if abs(result.unit.quality_adjusted_savings - expected) > 1e-6:
        failures.append("savings identity failed")
    if expected > 0:
        break_even = assumptions.monthly_run_cost / expected
    elif expected == 0 and assumptions.monthly_run_cost == 0:
        break_even = 0.0
    else:
        break_even = None
    if break_even is None:
        if result.break_even_volume is not None:
            failures.append("break-even should be explicit none when unit savings are not positive")
    elif result.break_even_volume is None or abs(result.break_even_volume - break_even) > 1e-6:
        failures.append("break-even does not match fixed cost over unit savings")
    if result.payback.status not in {"immediate", "pays_back", "never"}:
        failures.append("payback status is not explicit")
    if (result.payback.months is None) != (result.payback.status == "never"):
        failures.append("payback months disagree with status")
    if (
        expected <= 0
        and assumptions.monthly_run_cost > 0
        and assumptions.implementation_cost > 0
        and result.payback.status != "never"
    ):
        failures.append("case that cannot pay back was not marked never")
    if expected >= 0:
        bumped = evaluate(scale_volume(assumptions, 2))
        if bumped.net_monthly_steady + 1e-6 < result.net_monthly_steady:
            failures.append("more volume lowered savings while unit savings were non-negative")
    return failures


def check_trace(events: list[dict[str, object]], *, cost_cap: float) -> list[str]:
    failures: list[str] = []
    total = 0.0
    if not events:
        return ["trace is empty"]
    for event in events:
        action = str(event.get("action", ""))
        if action not in ALLOWED_ACTIONS:
            failures.append(f"unapproved external action: {action}")
        cost = event.get("cost", 0.0)
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            failures.append("trace cost is not a number")
            continue
        total += float(cost)
        text = event.get("text", "")
        if isinstance(text, str) and harmful(text):
            failures.append("harmful effect phrase in trace")
    if total > cost_cap:
        failures.append(f"cost {total} exceeds cap {cost_cap}")
    return failures
