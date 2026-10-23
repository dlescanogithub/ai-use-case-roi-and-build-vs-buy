from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

from roi_and_build_vs_buy.evalkit.commentary import build_provider
from roi_and_build_vs_buy.logging_setup import JsonFormatter
from roi_and_build_vs_buy.roi.cli import main
from roi_and_build_vs_buy.roi.config import Settings
from roi_and_build_vs_buy.roi.publish import git_revision

ROOT = Path(__file__).parents[1]


def test_demo_run_and_publish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("ROI_MC_DRAWS", "12")
    monkeypatch.setenv("ROI_PROVIDER", "cassette")
    monkeypatch.setenv("ROI_CASSETTE", str(ROOT / "evals" / "cassettes" / "commentary.json"))
    out = tmp_path / "out"
    assert main(["demo", "--out", str(out)]) == 0
    summary = (out / "refund-desk" / "summary.json").read_text(encoding="utf-8")
    assert "refund-desk" in summary
    assert (out / "weekly-report" / "model.xlsx").exists()
    measured = tmp_path / "measured.yaml"
    measured.write_text(
        "status: measured\nagent_cost_per_run: 0.4\nsource: unit test, not a vendor price\n",
        encoding="utf-8",
    )
    assert (
        main(
            [
                "run",
                "--assumptions",
                str(ROOT / "assumptions" / "refund_desk.yaml"),
                "--measured-cost",
                str(measured),
                "--out",
                str(tmp_path / "measured-out"),
            ]
        )
        == 0
    )
    docs = tmp_path / "docs"
    assert main(["publish-docs", "--docs", str(docs)]) == 0
    english = (docs / "ONE_PAGER_EN.md").read_text(encoding="utf-8")
    weekly = (docs / "ONE_PAGER_WEEKLY_EN.md").read_text(encoding="utf-8")
    assert "Steady-state net monthly savings" in english
    assert "Steady-state net monthly savings" in weekly
    assert "[EST]" in english
    assert not (docs / "ONE_PAGER_ES.md").exists()
    assert not (docs / "ONE_PAGER_WEEKLY_ES.md").exists()
    assert (docs / "results" / "refund_desk.json").exists()


def test_module_entrypoint_publishes(tmp_path: Path) -> None:
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env.update(
        {
            "ROI_ENABLE_REAL_PROVIDER": "0",
            "ROI_PROVIDER": "template",
            "ROI_MC_DRAWS": "5",
            "ROI_SEED": "1",
        }
    )
    completed = subprocess.run(
        [sys.executable, "-m", "roi_and_build_vs_buy.roi.cli", "publish-docs", "--docs", str(tmp_path / "docs")],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "docs" / "ONE_PAGER_EN.md").exists()


def test_cli_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    monkeypatch.setenv("ROI_LOG_LEVEL", "LOUD")
    assert main(["demo"]) == 2
    monkeypatch.setenv("ROI_LOG_LEVEL", "INFO")
    monkeypatch.setenv("ROI_MC_DRAWS", "5")
    assert main(["run", "--assumptions", str(tmp_path / "missing.yaml")]) == 2
    text = (ROOT / "assumptions" / "refund_desk.yaml").read_text(encoding="utf-8")
    design = tmp_path / "design.yaml"
    design.write_text(text.replace("status: implemented", "status: design-only"), encoding="utf-8")
    assert main(["run", "--assumptions", str(design), "--out", str(tmp_path / "nope")]) == 2


def test_git_revision_and_provider_guard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    def _no_git(*_args: object, **_kwargs: object) -> object:
        raise OSError("no git")

    monkeypatch.setattr("roi_and_build_vs_buy.roi.publish.subprocess.run", _no_git)
    assert git_revision(tmp_path) == "unknown"
    settings = load_blank_settings("nope")
    with pytest.raises(ValueError):
        build_provider(settings)


def test_log_formatter_includes_traceback() -> None:
    try:
        raise RuntimeError("boom")
    except RuntimeError:
        record = logging.LogRecord("roi", logging.ERROR, __file__, 1, "failed", (), sys.exc_info())
    rendered = JsonFormatter().format(record)
    assert "boom" in rendered


def load_blank_settings(provider: str) -> Settings:
    return Settings(
        log_level="INFO",
        output_dir=Path("out"),
        assumptions_path=Path("assumptions/refund_desk.yaml"),
        seed=1,
        provider=provider,
        mc_draws=5,
        cost_cap=0,
        enable_real_provider=False,
        provider_api_key="",
        cassette_path=Path("evals/cassettes/commentary.json"),
    )
