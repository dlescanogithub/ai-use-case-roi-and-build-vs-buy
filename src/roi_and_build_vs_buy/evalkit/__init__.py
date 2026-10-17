"""Eval gates for the ROI formula and the build-vs-buy calculator.

``python -m roi_and_build_vs_buy.evalkit`` runs both gates.
"""

from roi_and_build_vs_buy.evalkit.decide_run import main as decide_main
from roi_and_build_vs_buy.evalkit.roi_gate import main as roi_main


def main() -> int:
    """Run both gates. Exit 0 only when each one passes."""

    roi_code = roi_main()
    decide_code = decide_main()
    if roi_code == 0 and decide_code == 0:
        print("BOTH EVAL GATES PASSED")
        return 0
    print("EVAL GATES FAILED")
    return 1


__all__ = ["main"]
