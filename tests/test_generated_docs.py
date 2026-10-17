"""Committed worked examples must match a fresh CLI run."""

from __future__ import annotations

from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_committed_reports_match_the_cli(tmp_path: Path) -> None:
    cases = (
        (
            "examples/bruma_freight",
            "0002",
            "docs/examples/bruma-freight-report.md",
            "docs/adr/bvb-0002-bruma-freight-support-agent.md",
        ),
        (
            "examples/cedro_records",
            "0003",
            "docs/examples/cedro-records-report.md",
            "docs/adr/bvb-0003-cedro-records-document-assistant.md",
        ),
    )
    for case_dir, adr_id, report_rel, adr_rel in cases:
        report_out = tmp_path / f"{adr_id}-report.md"
        adr_out = tmp_path / f"{adr_id}-adr.md"
        code = main(
            [
                "report",
                "--case",
                case_dir,
                "--out",
                str(report_out),
                "--adr-id",
                adr_id,
                "--adr-out",
                str(adr_out),
            ]
        )
        assert code == 0
        fresh_report = report_out.read_text(encoding="utf-8")
        committed_report = (ROOT / report_rel).read_text(encoding="utf-8")
        assert fresh_report == committed_report
        fresh_adr = adr_out.read_text(encoding="utf-8")
        committed_adr = (ROOT / adr_rel).read_text(encoding="utf-8")
        assert fresh_adr == committed_adr
