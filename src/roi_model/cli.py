"""Command line. Settings come from the environment; flags only pick a case file."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from roi_model.assumptions import AssumptionError
from roi_model.config import ConfigError, load_settings
from roi_model.evalkit.providers import build_provider
from roi_model.logging_setup import configure_logging
from roi_model.publish import git_revision, load_for_run, now_iso, write_bundle, write_one_pagers

LOGGER = logging.getLogger("roi_model")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roi-model",
        description="Simulated ROI model. Inputs are assumptions. No paid API.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("demo", help="run the refund desk and the weekly-report example")
    demo.add_argument("--out", type=Path, default=None)

    run = sub.add_parser("run", help="evaluate one implemented case file")
    run.add_argument("--assumptions", type=Path, default=None)
    run.add_argument("--measured-cost", type=Path, default=None)
    run.add_argument("--out", type=Path, default=None)

    publish = sub.add_parser("publish-docs", help="regenerate one-pagers and docs/results")
    publish.add_argument("--docs", type=Path, default=Path("docs"))
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        settings = load_settings()
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    configure_logging(settings.log_level)
    args = _parser().parse_args(argv)
    try:
        if args.command == "demo":
            return _demo(settings.output_dir if args.out is None else args.out, settings)
        if args.command == "run":
            assumptions = args.assumptions or settings.assumptions_path
            out = args.out or settings.output_dir
            return _run(
                assumptions,
                args.measured_cost,
                out,
                settings,
                command="python -m roi_model.cli run",
            )
        if args.command == "publish-docs":
            return _publish(args.docs, settings)
    except (AssumptionError, OSError, RuntimeError) as exc:
        LOGGER.error("run failed", extra={"structured": {"error": str(exc)}})
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("error: unknown command", file=sys.stderr)
    return 2


def _run(
    assumptions: Path,
    measured: Path | None,
    out: Path,
    settings: object,
    *,
    command: str,
) -> int:
    from roi_model.config import Settings

    if not isinstance(settings, Settings):
        raise TypeError("settings")
    provider = build_provider(settings)
    analysis = load_for_run(
        assumptions,
        measured_cost=measured,
        draws=settings.mc_draws,
        seed=settings.seed,
    )
    payload = write_bundle(
        analysis,
        out,
        command=command,
        generated_at=now_iso(),
        git_revision_value=git_revision(Path.cwd()),
        provider=provider,
        prompt_id="refund-commentary",
    )
    LOGGER.info(
        "model evaluated",
        extra={
            "structured": {
                "case": analysis.case.meta.case_id,
                "npv": analysis.result.npv,
                "provider": settings.provider,
            }
        },
    )
    print(json.dumps({"case_id": payload["case_id"], "npv_3y": payload["npv_3y"], "out": str(out)}))
    return 0


def _demo(out: Path, settings: object) -> int:
    root = Path.cwd()
    code = _run(
        root / "assumptions" / "refund_desk.yaml",
        None,
        out / "refund-desk",
        settings,
        command="python -m roi_model.cli demo",
    )
    if code != 0:
        return code
    return _run(
        root / "assumptions" / "weekly_report.yaml",
        None,
        out / "weekly-report",
        settings,
        command="python -m roi_model.cli demo",
    )


def _publish(docs: Path, settings: object) -> int:
    from roi_model.config import Settings

    if not isinstance(settings, Settings):
        raise TypeError("settings")
    root = Path.cwd()
    command = "python -m roi_model.cli publish-docs"
    generated = now_iso()
    revision = git_revision(root)
    refund = load_for_run(
        root / "assumptions" / "refund_desk.yaml",
        measured_cost=None,
        draws=settings.mc_draws,
        seed=settings.seed,
    )
    weekly = load_for_run(
        root / "assumptions" / "weekly_report.yaml",
        measured_cost=None,
        draws=settings.mc_draws,
        seed=settings.seed,
    )
    write_one_pagers(
        refund,
        docs,
        stem="ONE_PAGER",
        command=command,
        generated_at=generated,
        git_revision_value=revision,
    )
    write_one_pagers(
        weekly,
        docs,
        stem="ONE_PAGER_WEEKLY",
        command=command,
        generated_at=generated,
        git_revision_value=revision,
    )
    results = docs / "results"
    results.mkdir(parents=True, exist_ok=True)
    provider = build_provider(settings)
    refund_payload = write_bundle(
        refund,
        results / "refund-desk",
        command=command,
        generated_at=generated,
        git_revision_value=revision,
        provider=provider,
        prompt_id="refund-commentary",
    )
    weekly_payload = write_bundle(
        weekly,
        results / "weekly-report",
        command=command,
        generated_at=generated,
        git_revision_value=revision,
        provider=provider,
        prompt_id="weekly-commentary",
    )
    # The weekly cassette id is not required for publish: template provider
    # accepts any id. Cassette evals use refund-commentary only.
    (results / "refund_desk.json").write_text(
        json.dumps(refund_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (results / "weekly_report.json").write_text(
        json.dumps(weekly_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({"published": True, "npv_3y": refund_payload["npv_3y"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
