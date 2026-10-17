"""Run the regression test of the decision model on the approved fictional cases."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.case import load_case
from roi_and_build_vs_buy.evalkit.decide_gate import evaluate_case
from roi_and_build_vs_buy.evalkit.trace import append_trace


def repo_root() -> Path:
    """Find the repository root from the working directory or this file."""

    start = Path.cwd()
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "evals" / "manifest.json").is_file():
            return candidate
    here = Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate / "pyproject.toml").is_file() and (candidate / "evals" / "manifest.json").is_file():
            return candidate
    raise RuntimeError("repo root not found (need pyproject.toml and evals/manifest.json)")


def run_gate(root: Path | None = None, *, trace_path: Path | None = None) -> dict[str, object]:
    """Evaluate every approved case. The returned object is the JSON summary."""

    base = root or repo_root()
    manifest = _read_json(base / "evals" / "manifest.json")
    golden = _read_json(base / "evals" / "golden" / "decisions.json")
    cases = manifest.get("cases")
    if not isinstance(cases, list):
        raise RuntimeError("evals/manifest.json cases must be a list")
    trace = trace_path or (base / "out" / "traces" / "eval.jsonl")
    if trace.is_file():
        trace.unlink()
    results: list[dict[str, object]] = []
    failed = False
    for item in cases:
        if not isinstance(item, dict):
            raise RuntimeError("eval case entries must be objects")
        case_id = str(item["id"])
        case_dir = base / str(item["case_dir"])
        cassette = base / str(item["cassette"])
        spec = golden.get(case_id)
        if not isinstance(spec, dict):
            raise RuntimeError(f"golden entry missing for {case_id}")
        winner = spec.get("winner")
        floor = spec.get("min_winner_stability_pct")
        if not isinstance(winner, str) or not isinstance(floor, str):
            raise RuntimeError(f"golden entry for {case_id} needs winner and min_winner_stability_pct")
        loaded = load_case(case_dir)
        failures = evaluate_case(
            case_id=case_id,
            weights=loaded.weights,
            scores=loaded.scores,
            model=loaded.tco,
            cassette_path=cassette,
            golden_winner=winner,
            min_winner_stability_pct=Decimal(floor),
            trace_path=trace,
            case_dir_display=str(item["case_dir"]),
        )
        from roi_and_build_vs_buy.build_vs_buy.matrix import score_matrix
        from roi_and_build_vs_buy.build_vs_buy.sensitivity import analyze

        ranking = score_matrix(loaded.weights, loaded.scores)
        sensitivity = analyze(ranking, loaded.scores)
        results.append(
            {
                "id": case_id,
                "winner": ranking.winner.option_id,
                "winner_stability_pct": str(sensitivity.winner_stability_pct),
                "rank_stability_pct": str(sensitivity.rank_stability_pct),
                "failures": failures,
            }
        )
        if failures:
            failed = True
    summary: dict[str, object] = {"ok": not failed, "cases": results}
    append_trace(trace, {"event": "gate_finished", "ok": not failed, "external_action": False})
    return summary


def main(argv: list[str] | None = None) -> int:
    """Print the gate summary as JSON and return 0 only when every case passed."""

    del argv
    summary = run_gate()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["ok"] else 1


def _read_json(path: Path) -> dict[str, object]:
    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError(f"{path} must be a JSON object")
    return {str(key): value for key, value in raw.items()}


if __name__ == "__main__":
    raise SystemExit(main())
