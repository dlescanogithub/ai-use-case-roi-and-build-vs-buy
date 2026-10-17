"""Forced regression: a deliberately wrong savings formula must fail the gate.

Exit 1 when the gate goes red (the expected outcome).
Exit 0 only if the wrong formula passes, which means the gate is blind.
"""

from __future__ import annotations

from pathlib import Path

from roi_and_build_vs_buy.evalkit.roi_invariants import check_result
from roi_and_build_vs_buy.roi.assumptions import Assumptions, assumptions_from_case, load_case
from roi_and_build_vs_buy.roi.model import ModelResult, build_result


def wrong_savings(assumptions: Assumptions) -> float:
    """Ignore errors, agent cost, review and residual error.

    Manual labor is treated as if it were pure savings. That is wrong on purpose.
    """
    return assumptions.manual_minutes_per_item / 60.0 * assumptions.loaded_cost_per_hour


def evaluate_wrong(assumptions: Assumptions) -> ModelResult:
    return build_result(assumptions, savings_override=wrong_savings(assumptions))


def regression_failures(root: Path) -> list[str]:
    case = load_case(root / "assumptions" / "refund_desk.yaml")
    assumptions = assumptions_from_case(case)
    result = evaluate_wrong(assumptions)
    return check_result(assumptions, result, evaluate_wrong)


def main() -> int:
    failures = regression_failures(Path.cwd())
    if not failures:
        print("GATE DID NOT GO RED: the wrong formula passed the invariants")
        return 0
    print("FORCED REGRESSION: invariants failed as required")
    for item in failures:
        print(f"- {item}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
