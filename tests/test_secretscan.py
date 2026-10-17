"""Prefix checks for the shared secretscan module.

Positive samples are built at runtime from pieces so this file never stores a literal key.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from roi_and_build_vs_buy.secretscan import scan, scan_text

ROOT = Path(__file__).resolve().parents[1]
SCANNER = ROOT / "src" / "roi_and_build_vs_buy" / "secretscan.py"
PROVENANCE = ROOT / "docs" / "PROVENANCE.md"


def _kinds(text: str) -> set[str]:
    return {finding.kind for finding in scan_text(text)}


def test_detects_each_required_prefix() -> None:
    samples = {
        "xai_key": "xai-" + ("a" * 20),
        "openai_key": "sk-" + ("b" * 20),
        "anthropic_key": "sk-ant-" + ("c" * 20),
        "underscore_sk_key": "sk_" + ("d" * 20),
        "github_token": "ghp_" + ("e" * 20),
        "github_fine_grained": "github_pat_" + ("f" * 20),
        "aws_access_key": "AKIA" + ("G" * 16),
        "bearer_token": "Bearer " + ("h" * 20),
        "private_key": "-----BEGIN " + "PRIVATE KEY-----",
    }
    for kind, text in samples.items():
        assert _kinds(text) == {kind}


def test_openai_shape_includes_proj_prefix_and_not_the_ant_prefix() -> None:
    assert _kinds("sk-proj-" + ("a" * 20)) == {"openai_key"}
    assert "openai_key" not in _kinds("sk-ant-" + ("a" * 20))


def test_private_key_header_variants() -> None:
    for header in (
        "-----BEGIN RSA " + "PRIVATE KEY-----",
        "-----BEGIN OPENSSH " + "PRIVATE KEY-----",
        "-----BEGIN EC " + "PRIVATE KEY-----",
    ):
        assert _kinds(header) == {"private_key"}


def test_short_or_ordinary_text_is_ignored() -> None:
    negatives = [
        "xai-" + ("a" * 19),
        "sk-" + ("b" * 19),
        "sk-proj-" + ("b" * 11),
        "sk-ant-" + ("c" * 19),
        "sk_" + ("d" * 19),
        "ghp_" + ("e" * 19),
        "github_pat_" + ("f" * 19),
        "AKIA" + ("G" * 15),
        "Bearer " + ("h" * 19),
        "Bearer token",
        "weights sum to 1 and the score is 5",
        "https://example.invalid/pricing",
        "estimate: true",
    ]
    for text in negatives:
        assert scan_text(text) == []


def test_repo_tree_has_no_findings() -> None:
    assert scan(ROOT) == []


def test_documented_sha256_matches_the_scanner_file() -> None:
    digest = hashlib.sha256(SCANNER.read_bytes()).hexdigest()
    text = PROVENANCE.read_text(encoding="utf-8")
    found = re.findall(r"\b[0-9a-f]{64}\b", text)
    assert found == [digest]
