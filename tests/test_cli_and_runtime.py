from __future__ import annotations

import json
import logging
from decimal import Decimal
from pathlib import Path

import pytest

from roi_and_build_vs_buy.build_vs_buy.cli import main
from roi_and_build_vs_buy.build_vs_buy.config import load_settings
from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError
from roi_and_build_vs_buy.evalkit.decide_regression import main as regression_main
from roi_and_build_vs_buy.evalkit.decide_run import main as eval_main
from roi_and_build_vs_buy.evalkit.prices import build_eval_provider, build_provider
from roi_and_build_vs_buy.evalkit.prices.cassette import CassettePriceProvider
from roi_and_build_vs_buy.evalkit.prices.fake import FakePriceProvider
from roi_and_build_vs_buy.evalkit.prices.http import HttpPriceProvider
from roi_and_build_vs_buy.logging_setup import configure_logging, log_event
from roi_and_build_vs_buy.retry import retry_call
from roi_and_build_vs_buy.secretscan import scan

ROOT = Path(__file__).resolve().parents[1]


def test_cli_score_tco_and_report(tmp_path: Path) -> None:
    score_out = tmp_path / "score.md"
    tco_out = tmp_path / "tco.md"
    report_out = tmp_path / "report.md"
    adr_out = tmp_path / "adr.md"
    case = ROOT / "examples" / "bruma_freight"
    assert (
        main(
            [
                "score",
                "--weights",
                str(case / "weights.yaml"),
                "--scores",
                str(case / "scores.yaml"),
                "--out",
                str(score_out),
            ]
        )
        == 0
    )
    assert main(["tco", "--input", str(case / "tco.yaml"), "--out", str(tco_out)]) == 0
    assert (
        main(
            [
                "report",
                "--case",
                str(case),
                "--out",
                str(report_out),
                "--adr-id",
                "0002",
                "--adr-out",
                str(adr_out),
            ]
        )
        == 0
    )
    report = report_out.read_text(encoding="utf-8")
    assert "simulated" in report
    assert "[EST]" in report
    assert "`build`" in report
    assert "BEGIN PRIVATE KEY" not in report
    assert "Decision" in adr_out.read_text(encoding="utf-8")


def test_cli_rejects_non_fictional_case(tmp_path: Path) -> None:
    case = tmp_path / "case"
    case.mkdir()
    source = ROOT / "examples" / "bruma_freight"
    for name in ("weights.yaml", "scores.yaml", "tco.yaml"):
        text = (source / name).read_text(encoding="utf-8").replace("fictional: true", "fictional: false", 1)
        (case / name).write_text(text, encoding="utf-8")
    assert main(["report", "--case", str(case), "--out", str(tmp_path / "out.md")]) == 2


def test_retries_respect_attempt_cap_and_backoff() -> None:
    delays: list[float] = []
    calls = {"n": 0}

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("not yet")
        return "ok"

    result = retry_call(
        flaky,
        max_attempts=3,
        backoff_cap=0.15,
        base_delay=0.1,
        sleep=delays.append,
    )
    assert result == "ok"
    assert delays == [0.1, 0.15]

    def always() -> str:
        raise TimeoutError("no")

    try:
        retry_call(always, max_attempts=2, backoff_cap=0.2, base_delay=0.05, sleep=delays.append)
    except TimeoutError:
        pass
    else:
        raise AssertionError("expected the last error to propagate")


def test_logs_are_json_and_drop_secrets(capsys: pytest.CaptureFixture[str]) -> None:
    logger = configure_logging("INFO")
    log_event(logger, "scored", winner="build", api_key="secret-value")
    captured = capsys.readouterr()
    line = captured.err.strip().splitlines()[-1]
    payload = json.loads(line)
    assert payload["msg"] == "scored"
    assert payload["winner"] == "build"
    assert "api_key" not in payload
    assert "secret-value" not in line
    assert logger.name == "roi_and_build_vs_buy"
    assert logging.getLogger("roi_and_build_vs_buy").propagate is False


def test_settings_keep_real_provider_off() -> None:
    settings = load_settings({})
    assert settings.real_provider is False
    assert settings.max_attempts == 3
    assert settings.cost_cap_usd == Decimal(0)
    try:
        load_settings({"DECIDE_REAL_PROVIDER": "yes"})
    except DecisionKitError as exc:
        assert "DECIDE_REAL_PROVIDER" in str(exc)
    else:
        raise AssertionError("expected a config failure")


def test_eval_provider_ignores_real_flag(tmp_path: Path) -> None:
    cassette = tmp_path / "quotes.json"
    cassette.write_text(
        json.dumps(
            {
                "vendor_a": {
                    "usd_per_seat_year": "10",
                    "source": "fictional cassette",
                    "simulated": True,
                }
            }
        ),
        encoding="utf-8",
    )
    settings = load_settings(
        {
            "DECIDE_REAL_PROVIDER": "1",
            "DECIDE_PROVIDER_BASE_URL": "https://example.invalid",
            "DECIDE_PROVIDER_API_KEY": "test-key",
        }
    )
    provider = build_eval_provider(cassette)
    assert isinstance(provider, CassettePriceProvider)
    quote = provider.quote("vendor_a")
    assert quote.simulated is True
    assert quote.cost_usd == Decimal(0)
    fake = build_provider(load_settings({}))
    assert isinstance(fake, FakePriceProvider)
    transport_calls: list[str] = []

    def transport(url: str, headers: dict[str, str]) -> dict[str, object]:
        transport_calls.append(url)
        assert headers["Authorization"].startswith("Bearer ")
        if len(transport_calls) < 2:
            raise TimeoutError("try again")
        return {"usd_per_seat_year": "15"}

    http = build_provider(settings, transport=transport)
    assert isinstance(http, HttpPriceProvider)
    quoted = http.quote("vendor_a")
    assert quoted.usd_per_seat_year == Decimal(15)
    assert len(transport_calls) == 2


def test_secret_scan_detects_a_token_and_the_repo_is_clean(tmp_path: Path) -> None:
    sample = tmp_path / "notes.txt"
    sample.write_text("token=" + "ghp_" + ("a" * 36) + "\n", encoding="utf-8")
    findings = scan(sample)
    assert findings and findings[0].kind == "github_token"
    assert scan(ROOT) == []


def test_eval_gate_passes_and_regression_fails() -> None:
    assert eval_main([]) == 0
    assert regression_main([]) == 1
