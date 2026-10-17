"""Forced regression. This command is supposed to fail.

The fixture keeps the Bruma Freight scores and cost model and replaces the
weights with a set that flips the approved winner. The same invariant gate
then goes red on `golden_winner`. CI asserts that this process exits non-zero.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.matrix import load_scores, load_weights
from roi_and_build_vs_buy.build_vs_buy.tco import load_tco
from roi_and_build_vs_buy.evalkit.decide_gate import evaluate_case
from roi_and_build_vs_buy.evalkit.decide_run import repo_root


def run_regression(root: Path | None = None, *, trace_path: Path | None = None) -> dict[str, object]:
    """Run the gate against the mis-weighted fixture."""

    base = root or repo_root()
    spec_raw: object = json.loads((base / "evals" / "regression" / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(spec_raw, dict):
        raise RuntimeError("regression manifest must be an object")
    golden_raw: object = json.loads((base / "evals" / "golden" / "decisions.json").read_text(encoding="utf-8"))
    if not isinstance(golden_raw, dict):
        raise RuntimeError("golden file must be an object")
    golden_case = str(spec_raw["golden_case"])
    golden_entry = golden_raw.get(golden_case)
    if not isinstance(golden_entry, dict):
        raise RuntimeError(f"golden entry missing for {golden_case}")
    winner = golden_entry.get("winner")
    floor = golden_entry.get("min_winner_stability_pct")
    if not isinstance(winner, str) or not isinstance(floor, str):
        raise RuntimeError("golden winner entry is incomplete")
    weights = load_weights(base / str(spec_raw["weights"]))
    scores = load_scores(base / str(spec_raw["scores"]))
    model = load_tco(base / str(spec_raw["tco"]))
    trace = trace_path or (base / "out" / "traces" / "regression.jsonl")
    failures = evaluate_case(
        case_id=str(spec_raw["id"]),
        weights=weights,
        scores=scores,
        model=model,
        cassette_path=base / str(spec_raw["cassette"]),
        golden_winner=winner,
        min_winner_stability_pct=Decimal(floor),
        trace_path=trace,
        case_dir_display="evals/regression/bruma_freight_misweighted",
    )
    return {"ok": not failures, "failures": failures, "expected_to_fail": True}


def main(argv: list[str] | None = None) -> int:
    """Exit 1 when the gate catches the flipped decision."""

    del argv
    summary = run_regression()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
