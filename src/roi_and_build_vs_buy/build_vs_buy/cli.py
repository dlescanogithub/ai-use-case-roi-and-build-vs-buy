"""CLI: `decide score`, `decide tco`, `decide report`."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from roi_and_build_vs_buy import __version__
from roi_and_build_vs_buy.build_vs_buy.adr import render_adr
from roi_and_build_vs_buy.build_vs_buy.case import load_case
from roi_and_build_vs_buy.build_vs_buy.config import load_settings
from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError
from roi_and_build_vs_buy.build_vs_buy.matrix import load_scores, load_weights, score_matrix
from roi_and_build_vs_buy.build_vs_buy.report import render_report, render_score, render_tco
from roi_and_build_vs_buy.build_vs_buy.sensitivity import analyze
from roi_and_build_vs_buy.build_vs_buy.tco import load_tco, project, project_all
from roi_and_build_vs_buy.logging_setup import configure_logging, log_event


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""

    parser = argparse.ArgumentParser(
        prog="decide",
        description="Score a build-vs-buy matrix, project a 3-year TCO, and write a report.",
    )
    parser.add_argument("--version", action="version", version=f"roi_and_build_vs_buy {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    score = sub.add_parser("score", help="Rank options from weights and scores")
    score.add_argument("--weights", required=True, type=Path)
    score.add_argument("--scores", required=True, type=Path)
    score.add_argument("--out", required=True, type=Path)

    tco = sub.add_parser("tco", help="Project 3-year cost from a TCO file")
    tco.add_argument("--input", required=True, type=Path)
    tco.add_argument("--out", required=True, type=Path)

    report = sub.add_parser("report", help="Write the combined decision report")
    report.add_argument("--case", required=True, type=Path)
    report.add_argument("--out", required=True, type=Path)
    report.add_argument("--adr-id", default="0000")
    report.add_argument("--adr-out", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI. Returns a process exit code."""

    settings = load_settings()
    logger = configure_logging(settings.log_level)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.cmd == "score":
            return _score(args.weights, args.scores, args.out, logger)
        if args.cmd == "tco":
            return _tco(args.input, args.out, logger)
        if args.cmd == "report":
            return _report(args.case, args.out, args.adr_id, args.adr_out, logger)
    except DecisionKitError as exc:
        log_event(logger, "validation_failed", error=str(exc))
        return 2
    log_event(logger, "unknown_command", cmd=str(args.cmd))
    return 2


def _score(weights_path: Path, scores_path: Path, out: Path, logger: logging.Logger) -> int:
    weights = load_weights(weights_path)
    scores = load_scores(scores_path)
    ranking = score_matrix(weights, scores)
    sensitivity = analyze(ranking, scores)
    case_dir = _display_dir(weights_path)
    _write(out, render_score(ranking, sensitivity, case_dir=case_dir))
    log_event(
        logger,
        "scored",
        case=ranking.case_id,
        winner=ranking.winner.option_id,
        winner_stability_pct=str(sensitivity.winner_stability_pct),
        rank_stability_pct=str(sensitivity.rank_stability_pct),
    )
    return 0


def _tco(input_path: Path, out: Path, logger: logging.Logger) -> int:
    model = load_tco(input_path)
    projections = project_all(model)
    _write(out, render_tco(model, projections))
    base = project(model, "base")
    log_event(
        logger,
        "tco_projected",
        case=model.case_id,
        options=len(base.options),
        scenarios=len(projections),
    )
    return 0


def _report(
    case_dir: Path,
    out: Path,
    adr_id: str,
    adr_out: Path | None,
    logger: logging.Logger,
) -> int:
    case = load_case(case_dir)
    ranking = score_matrix(case.weights, case.scores)
    sensitivity = analyze(ranking, case.scores)
    shown = case_dir.as_posix()
    _write(
        out,
        render_report(
            ranking=ranking,
            sensitivity=sensitivity,
            model=case.tco,
            case_dir=shown,
        ),
    )
    if adr_out is not None:
        base = project(case.tco, "base")
        _write(
            adr_out,
            render_adr(
                adr_id=adr_id,
                ranking=ranking,
                sensitivity=sensitivity,
                model=case.tco,
                projection=base,
                case_dir=shown,
            ),
        )
    log_event(
        logger,
        "report_written",
        case=case.weights.case_id,
        winner=ranking.winner.option_id,
        out=out.as_posix(),
    )
    return 0


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _display_dir(weights_path: Path) -> str:
    parent = weights_path.parent.as_posix()
    return parent if parent else "."
