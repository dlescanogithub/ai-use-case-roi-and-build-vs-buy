"""One evaluation bundle: base result, scenarios, tornado and Monte Carlo."""

from __future__ import annotations

from dataclasses import dataclass

from roi_model.assumptions import Assumptions, CaseFile, assumptions_from_case
from roi_model.model import ModelResult, build_result
from roi_model.montecarlo import MonteCarloResult, run_monte_carlo
from roi_model.sensitivity import ScenarioOutcome, TornadoRow, scenarios, tornado


@dataclass(frozen=True)
class Analysis:
    case: CaseFile
    assumptions: Assumptions
    result: ModelResult
    tornado: tuple[TornadoRow, ...]
    scenario_outcomes: tuple[ScenarioOutcome, ...]
    monte_carlo: MonteCarloResult
    measured_override: bool


def analyze(
    case: CaseFile,
    *,
    draws: int,
    seed: int,
    measured_override: bool = False,
    assumptions: Assumptions | None = None,
) -> Analysis:
    base = assumptions if assumptions is not None else assumptions_from_case(case)
    override = base.agent_cost_per_run_override
    return Analysis(
        case=case,
        assumptions=base,
        result=build_result(base),
        tornado=tornado(case, override=override),
        scenario_outcomes=scenarios(case, override=override),
        monte_carlo=run_monte_carlo(case, draws=draws, seed=seed, override=override),
        measured_override=measured_override,
    )
