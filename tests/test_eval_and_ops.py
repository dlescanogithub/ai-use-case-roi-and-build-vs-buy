from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from roi_and_build_vs_buy.evalkit.commentary.cassette import CassetteError, CassetteProvider
from roi_and_build_vs_buy.evalkit.commentary.real import RealProvider, RealProviderDisabled
from roi_and_build_vs_buy.evalkit.roi_gate import main as gate_main
from roi_and_build_vs_buy.evalkit.roi_gate import run_gate
from roi_and_build_vs_buy.evalkit.roi_invariants import check_trace, harmful
from roi_and_build_vs_buy.evalkit.roi_regression import main as regression_main
from roi_and_build_vs_buy.evalkit.trace import append_event, read_events
from roi_and_build_vs_buy.logging_setup import JsonFormatter, configure_logging
from roi_and_build_vs_buy.retry import RetryError, retry
from roi_and_build_vs_buy.roi.config import ConfigError, load_settings
from roi_and_build_vs_buy.secretscan import main as scan_main
from roi_and_build_vs_buy.secretscan import scan

ROOT = Path(__file__).parents[1]


def test_gate_passes_and_regression_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(ROOT)
    assert run_gate(ROOT, trace_dir=tmp_path) == []
    assert gate_main() == 0
    assert regression_main() == 1


def test_trace_invariants() -> None:
    assert harmful("Please charge the card now")
    assert not harmful("keep the sketch on disk")
    assert check_trace([], cost_cap=0) == ["trace is empty"]
    failures = check_trace(
        [{"action": "wire", "cost": 5, "text": "wire the funds"}],
        cost_cap=0,
    )
    assert any("unapproved" in item for item in failures)
    assert any("exceeds" in item for item in failures)
    assert any("harmful" in item for item in failures)
    assert check_trace([{"action": "compute", "cost": "nope"}], cost_cap=0)


def test_cassette_and_real_provider(tmp_path: Path) -> None:
    provider = CassetteProvider(ROOT / "evals" / "cassettes" / "commentary.json")
    assert provider.complete("refund-commentary").cost == 0
    with pytest.raises(CassetteError):
        provider.complete("missing")
    broken = tmp_path / "bad.json"
    broken.write_text("[]", encoding="utf-8")
    with pytest.raises(CassetteError):
        CassetteProvider(broken)
    off = RealProvider(enabled=False, api_key="secret")
    with pytest.raises(RealProviderDisabled, match="off"):
        off.complete("x")
    no_key = RealProvider(enabled=True, api_key="")
    with pytest.raises(RealProviderDisabled, match="key"):
        no_key.complete("x")
    enabled = RealProvider(enabled=True, api_key="present")
    with pytest.raises(RealProviderDisabled, match="vendor"):
        enabled.complete("x")


def test_retry_bounds_and_cap() -> None:
    calls = {"n": 0}
    delays: list[float] = []

    def flaky() -> str:
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("not yet")
        return "ok"

    assert retry(flaky, max_attempts=3, base_delay=1, backoff_cap=1.5, sleep=delays.append) == "ok"
    assert delays == [1, 1.5]

    def always() -> str:
        raise RuntimeError("no")

    with pytest.raises(RetryError):
        retry(always, max_attempts=2, base_delay=0, backoff_cap=0, sleep=delays.append)
    with pytest.raises(ValueError):
        retry(lambda: "x", max_attempts=0)


def test_secretscan_and_logging(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    clean = tmp_path / "note.txt"
    clean.write_text("no secrets here\n", encoding="utf-8")
    assert scan(tmp_path) == []
    dirty = tmp_path / "leak.txt"
    dirty.write_text("key " + "AKIA" + "IOSFODNN7EXAMPLE" + "\n", encoding="utf-8")
    found = scan(tmp_path)
    assert found and found[0].kind == "aws_access_key"
    assert scan_main([str(tmp_path)]) == 1
    assert scan_main([str(ROOT)]) == 0
    configure_logging("INFO")
    record = logging.LogRecord("roi", logging.INFO, __file__, 1, "hello", (), None)
    record.structured = {"case": "refund-desk"}  # type: ignore[attr-defined]
    line = JsonFormatter().format(record)
    payload = json.loads(line)
    assert payload["msg"] == "hello"
    assert payload["data"]["case"] == "refund-desk"
    capsys.readouterr()


def test_config_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROI_MC_DRAWS", "15")
    monkeypatch.setenv("ROI_PROVIDER", "fake")
    monkeypatch.setenv("ROI_ENABLE_REAL_PROVIDER", "0")
    settings = load_settings()
    assert settings.mc_draws == 15
    assert settings.provider == "fake"
    assert settings.enable_real_provider is False
    monkeypatch.setenv("ROI_PROVIDER", "nope")
    with pytest.raises(ConfigError):
        load_settings()
    monkeypatch.setenv("ROI_PROVIDER", "template")
    monkeypatch.setenv("ROI_COST_CAP", "-1")
    with pytest.raises(ConfigError):
        load_settings()


def test_trace_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "t.jsonl"
    append_event(path, {"action": "compute", "cost": 0})
    events = read_events(path)
    assert events[0]["action"] == "compute"
    assert read_events(tmp_path / "missing.jsonl") == []
