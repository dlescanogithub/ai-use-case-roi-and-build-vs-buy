"""One-at-a-time tornado and named scenario sets."""

from __future__ import annotations

from dataclasses import dataclass

from roi_and_build_vs_buy.roi.assumptions import (
    AssumptionError,
    Assumptions,
    CaseFile,
    apply_parameter,
    assumptions_for_scenario,
    assumptions_from_case,
)
from roi_and_build_vs_buy.roi.model import ModelResult, build_result


@dataclass(frozen=True)
class TornadoRow:
    name: str
    low_value: float
    high_value: float
    low_npv: float
    high_npv: float
    base_npv: float
    swing: float
    abs_swing: float


@dataclass(frozen=True)
class ScenarioOutcome:
    name: str
    assumptions: Assumptions
    result: ModelResult


def tornado(case: CaseFile, *, override: float | None = None) -> tuple[TornadoRow, ...]:
    """Vary each assumption to its low and high while the others stay at base.

    Rows are sorted by absolute NPV swing, largest first. A measured per-run
    cost override is held fixed, so token-price swings collapse to zero.
    """
    base_assumptions = assumptions_from_case(case, override=override)
    base_npv = build_result(base_assumptions).npv
    rows: list[TornadoRow] = []
    for name, spec in case.parameters.items():
        low_npv = build_result(apply_parameter(base_assumptions, name, spec.low)).npv
        high_npv = build_result(apply_parameter(base_assumptions, name, spec.high)).npv
        swing = high_npv - low_npv
        rows.append(
            TornadoRow(
                name=name,
                low_value=spec.low,
                high_value=spec.high,
                low_npv=low_npv,
                high_npv=high_npv,
                base_npv=base_npv,
                swing=swing,
                abs_swing=abs(swing),
            )
        )
    rows.sort(key=lambda row: row.abs_swing, reverse=True)
    return tuple(rows)


def scenarios(case: CaseFile, *, override: float | None = None) -> tuple[ScenarioOutcome, ...]:
    ordered = ("pessimistic", "base", "optimistic")
    outcomes: list[ScenarioOutcome] = []
    for name in ordered:
        assumptions = assumptions_for_scenario(case, name, override=override)
        outcomes.append(ScenarioOutcome(name=name, assumptions=assumptions, result=build_result(assumptions)))
    return tuple(outcomes)


def require_implemented(case: CaseFile) -> None:
    if case.meta.status != "implemented":
        raise AssumptionError(f"{case.meta.case_id} is design-only; it is not evaluated as a result")
