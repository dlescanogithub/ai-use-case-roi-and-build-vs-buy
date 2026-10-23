"""Write a report bundle to disk. No network."""

from __future__ import annotations

import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from roi_and_build_vs_buy import __version__
from roi_and_build_vs_buy.evalkit.commentary.base import Provider
from roi_and_build_vs_buy.evalkit.trace import append_event
from roi_and_build_vs_buy.retry import retry
from roi_and_build_vs_buy.roi.analysis import Analysis, analyze
from roi_and_build_vs_buy.roi.assumptions import apply_measured_cost, assumptions_from_case, load_case
from roi_and_build_vs_buy.roi.export_tabular import write_csv, write_xlsx
from roi_and_build_vs_buy.roi.report import chart_for, render_html, render_markdown, render_one_pager
from roi_and_build_vs_buy.roi.sensitivity import require_implemented


def git_revision(root: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return "unknown"
    if completed.returncode != 0:
        return "unknown"
    revision = completed.stdout.strip()
    return revision or "unknown"


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def load_for_run(
    path: Path,
    *,
    measured_cost: Path | None,
    draws: int,
    seed: int,
) -> Analysis:
    case = load_case(path)
    require_implemented(case)
    assumptions = assumptions_from_case(case)
    used_measured = False
    if measured_cost is not None:
        assumptions = apply_measured_cost(assumptions, measured_cost)
        used_measured = True
    return analyze(
        case,
        draws=draws,
        seed=seed,
        measured_override=used_measured,
        assumptions=assumptions,
    )


def summary_payload(
    analysis: Analysis,
    *,
    generated_at: str,
    command: str,
    git_revision_value: str,
) -> dict[str, object]:
    result = analysis.result
    mc = analysis.monte_carlo
    return {
        "case_id": analysis.case.meta.case_id,
        "generated_at": generated_at,
        "command": command,
        "version": __version__,
        "git_revision": git_revision_value,
        "simulated": True,
        "inputs": "EST",
        "currency": analysis.case.meta.currency,
        "measured_override": analysis.measured_override,
        "net_monthly_savings_steady": result.net_monthly_steady,
        "payback_status": result.payback.status,
        "payback_months": result.payback.months,
        "payback_reason": result.payback.reason,
        "break_even_volume": result.break_even_volume,
        "break_even_reason": result.break_even_reason,
        "npv_3y": result.npv,
        "cost_per_completed_item": result.unit.cost_per_completed_item,
        "quality_adjusted_savings_per_item": result.unit.quality_adjusted_savings,
        "residual_error_cost_per_item": result.unit.residual_error_cost,
        "agent_cost_per_run": result.unit.agent_run_cost,
        "scenarios": {
            outcome.name: {
                "npv": outcome.result.npv,
                "net_monthly": outcome.result.net_monthly_steady,
                "payback_status": outcome.result.payback.status,
                "payback_months": outcome.result.payback.months,
            }
            for outcome in analysis.scenario_outcomes
        },
        "monte_carlo": {
            "draws": mc.draws,
            "seed": mc.seed,
            "npv_p10": mc.npv_p10,
            "npv_p50": mc.npv_p50,
            "npv_p90": mc.npv_p90,
            "net_p10": mc.net_p10,
            "net_p50": mc.net_p50,
            "net_p90": mc.net_p90,
            "top_drivers": [{"name": name, "spearman": score} for name, score in mc.drivers[:5]],
        },
        "top_tornado": [
            {"name": row.name, "abs_swing": row.abs_swing, "swing": row.swing} for row in analysis.tornado[:5]
        ],
    }


def write_bundle(
    analysis: Analysis,
    directory: Path,
    *,
    command: str,
    generated_at: str,
    git_revision_value: str,
    provider: Provider,
    prompt_id: str,
) -> dict[str, object]:
    directory.mkdir(parents=True, exist_ok=True)
    trace_path = directory / "trace.jsonl"
    if trace_path.exists():
        trace_path.unlink()
    append_event(trace_path, {"action": "read_assumptions", "cost": 0.0})

    def _complete() -> str:
        response = provider.complete(prompt_id)
        append_event(
            trace_path,
            {
                "action": "provider_replay",
                "cost": response.cost,
                "text": response.text,
                "provider": response.provider,
            },
        )
        return response.text

    commentary = retry(_complete, max_attempts=3, base_delay=0.01, backoff_cap=0.05)
    append_event(trace_path, {"action": "compute", "cost": 0.0})
    markdown = render_markdown(
        analysis,
        generated_at=generated_at,
        command=command,
        git_revision=git_revision_value,
    )
    markdown = markdown + "\n## Commentary\n\n" + commentary + "\n"
    svg = chart_for(analysis)
    (directory / "report.md").write_text(markdown, encoding="utf-8")
    (directory / "report.html").write_text(render_html(analysis, markdown, svg), encoding="utf-8")
    (directory / "tornado.svg").write_text(svg, encoding="utf-8")
    write_csv(analysis, directory)
    write_xlsx(analysis, directory / "model.xlsx")
    payload = summary_payload(
        analysis,
        generated_at=generated_at,
        command=command,
        git_revision_value=git_revision_value,
    )
    (directory / "summary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_event(trace_path, {"action": "write_report", "cost": 0.0})
    return payload


def write_one_pagers(
    analysis: Analysis,
    directory: Path,
    *,
    stem: str,
    command: str,
    generated_at: str,
    git_revision_value: str,
) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    text = render_one_pager(
        analysis,
        generated_at=generated_at,
        command=command,
        git_revision=git_revision_value,
    )
    (directory / f"{stem}_EN.md").write_text(text, encoding="utf-8")
