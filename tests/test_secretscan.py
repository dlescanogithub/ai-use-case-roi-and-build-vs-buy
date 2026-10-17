"""Key-shape tests. Fixtures are concatenated at runtime so this file has no literal key."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from roi_model.secretscan import PATTERNS, scan
from roi_model.secretscan import main as scan_main

ROOT = Path(__file__).parents[1]
SCANNER = ROOT / "src" / "roi_model" / "secretscan.py"


def _piece(*parts: str) -> str:
    return "".join(parts)


def _rules(text: str) -> set[str]:
    matched: set[str] = set()
    for rule, pattern in PATTERNS:
        if pattern.search(text):
            matched.add(rule)
    return matched


def test_each_key_shape_matches_and_short_values_do_not() -> None:
    samples = {
        "xai_key": _piece("xai-", "A" * 20),
        "openai_key": _piece("sk-", "b" * 20),
        "openai_proj": _piece("sk-proj-", "c" * 20),
        "anthropic_key": _piece("sk-ant-", "d" * 20),
        "elevenlabs_key": _piece("sk_", "e1" * 10),
        "github_token": _piece("ghp_", "f" * 20),
        "github_pat": _piece("github_pat_", "g" * 20),
        "aws_access_key": _piece("AKIA", "0" * 16),
        "bearer_token": _piece("Bearer ", "h" * 20),
        "private_key": _piece("-----BEGIN ", "PRIVATE KEY-----"),
        "private_key_rsa": _piece("-----BEGIN RSA ", "PRIVATE KEY-----"),
    }
    expected = {
        "xai_key": {"xai_key"},
        "openai_key": {"openai_key"},
        "openai_proj": {"openai_key"},
        "anthropic_key": {"anthropic_key", "openai_key"},
        "elevenlabs_key": {"elevenlabs_key"},
        "github_token": {"github_token"},
        "github_pat": {"github_pat"},
        "aws_access_key": {"aws_access_key"},
        "bearer_token": {"bearer_token"},
        "private_key": {"private_key"},
        "private_key_rsa": {"private_key"},
    }
    for name, text in samples.items():
        assert _rules(text) == expected[name], name

    negatives = [
        _piece("xai-", "A" * 19),
        _piece("sk-", "b" * 19),
        _piece("sk-proj-", "c" * 13),
        _piece("sk-ant-", "d" * 15),
        _piece("sk_", "e" * 19),
        _piece("ghp_", "f" * 19),
        _piece("github_pat_", "g" * 19),
        _piece("AKIA", "0" * 15),
        _piece("Bearer ", "h" * 19),
        "Bearer",
        _piece("-----BEGIN ", "PUBLIC KEY-----"),
        "xai-replace-me",
        "sk-example",
        "no secrets here",
    ]
    for text in negatives:
        assert _rules(text) == set(), text


def test_scan_finds_shapes_in_a_file_and_ignores_the_repo(tmp_path: Path) -> None:
    leaked = tmp_path / "leak.txt"
    leaked.write_text(_piece("token ", "xai-", "Z" * 22, "\n"), encoding="utf-8")
    found = scan(tmp_path)
    assert [item.rule for item in found] == ["xai_key"]
    assert scan_main(["--root", str(tmp_path)]) == 1
    assert scan(ROOT) == []
    assert scan_main(["--root", str(ROOT)]) == 0


def test_pattern_names_cover_the_shared_list() -> None:
    names = [name for name, _pattern in PATTERNS]
    for required in (
        "xai_key",
        "openai_key",
        "anthropic_key",
        "elevenlabs_key",
        "github_token",
        "github_pat",
        "aws_access_key",
        "bearer_token",
        "private_key",
    ):
        assert required in names


def test_secretscan_sha256_is_recorded() -> None:
    digest = hashlib.sha256(SCANNER.read_bytes()).hexdigest()
    text = (ROOT / "docs" / "PROVENANCE.md").read_text(encoding="utf-8")
    assert re.search(rf"sha256:\s*{digest}", text)
    assert "vendored" in text.lower()
    assert "secretscan.py" in text


def test_scanner_source_does_not_match_its_own_patterns() -> None:
    assert scan(SCANNER.parent) == [] or all(item.path.name != "secretscan.py" for item in scan(SCANNER.parent))
    for line in SCANNER.read_text(encoding="utf-8").splitlines():
        assert _rules(line) == set()


@pytest.mark.parametrize(
    "rule",
    [
        "xai_key",
        "openai_key",
        "anthropic_key",
        "elevenlabs_key",
        "github_token",
        "github_pat",
        "aws_access_key",
        "bearer_token",
        "private_key",
    ],
)
def test_rule_is_compiled(rule: str) -> None:
    assert any(name == rule for name, _pattern in PATTERNS)
