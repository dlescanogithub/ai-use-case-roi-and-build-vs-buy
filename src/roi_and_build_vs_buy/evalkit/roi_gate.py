"""Eval gate: invariants, cassette replay, cost cap, no unapproved action.

No network. No paid API. Exact tool-call trajectories are not asserted.
"""

from __future__ import annotations

from pathlib import Path

from roi_and_build_vs_buy.evalkit.commentary.cassette import CassetteProvider
from roi_and_build_vs_buy.evalkit.commentary.fake import FakeProvider
from roi_and_build_vs_buy.evalkit.commentary.real import RealProvider
from roi_and_build_vs_buy.evalkit.roi_invariants import check_result, check_trace, harmful
from roi_and_build_vs_buy.evalkit.trace import append_event, read_events
from roi_and_build_vs_buy.retry import retry
from roi_and_build_vs_buy.roi.analysis import analyze
from roi_and_build_vs_buy.roi.assumptions import assumptions_from_case, load_case
from roi_and_build_vs_buy.roi.model import build_result
from roi_and_build_vs_buy.roi.montecarlo import run_monte_carlo
from roi_and_build_vs_buy.roi.report import render_one_pager


def _track(provider_name: str, complete_text: str, cost: float, path: Path) -> None:
    append_event(path, {"action": "read_assumptions", "cost": 0.0, "provider": provider_name})
    append_event(path, {"action": "compute", "cost": 0.0, "provider": provider_name})
    append_event(
        path,
        {
            "action": "provider_replay",
            "cost": cost,
            "text": complete_text,
            "provider": provider_name,
        },
    )
    append_event(path, {"action": "write_report", "cost": 0.0, "provider": provider_name})


def run_gate(root: Path, *, trace_dir: Path) -> list[str]:
    failures: list[str] = []
    case = load_case(root / "assumptions" / "refund_desk.yaml")
    weekly = load_case(root / "assumptions" / "weekly_report.yaml")
    for loaded in (case, weekly):
        assumptions = assumptions_from_case(loaded)
        result = build_result(assumptions)
        failures.extend(check_result(assumptions, result, build_result))
    left = run_monte_carlo(case, draws=40, seed=7)
    right = run_monte_carlo(case, draws=40, seed=7)
    if (left.npv_p10, left.npv_p50, left.npv_p90) != (right.npv_p10, right.npv_p50, right.npv_p90):
        failures.append("monte carlo seed was not reproducible")
    analysis = analyze(case, draws=20, seed=1)
    page = render_one_pager(
        analysis,
        generated_at="2000-01-01T00:00:00Z",
        command="eval-gate",
        git_revision="eval",
    )
    if harmful(page) or "[EST]" not in page or "Simulated" not in page:
        failures.append("report failed the no-harm or labeling check")
    fake = FakeProvider()
    fake_response = retry(lambda: fake.complete("refund-commentary"))
    fake_trace = trace_dir / "fake.jsonl"
    _track(fake.name, fake_response.text, fake_response.cost, fake_trace)
    failures.extend(check_trace(read_events(fake_trace), cost_cap=0.0))
    cassette = CassetteProvider(root / "evals" / "cassettes" / "commentary.json")
    recorded = retry(lambda: cassette.complete("refund-commentary"))
    cassette_trace = trace_dir / "cassette.jsonl"
    _track(cassette.name, recorded.text, recorded.cost, cassette_trace)
    failures.extend(check_trace(read_events(cassette_trace), cost_cap=0.0))
    real = RealProvider(enabled=False, api_key="")
    try:
        real.complete("refund-commentary")
    except Exception as exc:
        if "off" not in str(exc):
            failures.append("real provider did not refuse while off")
    else:
        failures.append("real provider ran while off")
    return failures


def main() -> int:
    root = Path.cwd()
    failures = run_gate(root, trace_dir=root / "out" / "eval-traces")
    if failures:
        print("EVAL GATE FAILED")
        for item in failures:
            print(f"- {item}")
        return 1
    print("EVAL GATE PASSED")
    print("- savings identity, break-even, payback explicit, monotonicity")
    print("- seed reproducibility")
    print("- no harmful effect phrase")
    print("- cost within cap (0)")
    print("- no unapproved external action")
    print("- cassette replay, real provider off")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
