"""Shared secret scanner.

Vendored copy. Keep this file byte-identical across portfolio repos.
The sha256 of this file is recorded in docs/PROVENANCE.md.

Patterns are prefix shapes. They are not a customer list and they are not
a full secret-management product.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "htmlcov",
    "out",
    "dist",
    "build",
    ".eggs",
}
_SKIP_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".whl",
    ".pyc",
    ".zip",
    ".gz",
}

# Order matters: longer, more specific prefixes come before the general sk- shape
# so a single token is not classified as two kinds.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private_key", re.compile(r"-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github_fine_grained", re.compile(r"(?<![A-Za-z0-9])github_pat_[A-Za-z0-9_]{20,}")),
    ("github_token", re.compile(r"(?<![A-Za-z0-9])ghp_[A-Za-z0-9]{20,}")),
    ("bearer_token", re.compile(r"Bearer [A-Za-z0-9._~\-+/=]{20,}")),
    ("xai_key", re.compile(r"(?<![A-Za-z0-9])xai-[A-Za-z0-9_\-]{20,}")),
    ("anthropic_key", re.compile(r"(?<![A-Za-z0-9])sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai_key", re.compile(r"(?<![A-Za-z0-9])sk-(?!ant-)[A-Za-z0-9_\-]{20,}")),
    ("underscore_sk_key", re.compile(r"(?<![A-Za-z0-9])sk_[A-Za-z0-9]{20,}")),
)


@dataclass(frozen=True)
class Finding:
    """One match."""

    path: str
    line: int
    kind: str


def scan_text(text: str, *, label: str = "<memory>") -> list[Finding]:
    """Scan one string. Used by tests so fixtures are never stored on disk."""

    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in _PATTERNS:
            if pattern.search(line):
                findings.append(Finding(path=label, line=line_number, kind=kind))
    return findings


def scan(root: Path) -> list[Finding]:
    """Scan text files under `root` and return findings."""

    findings: list[Finding] = []
    for path in _files(root):
        findings.extend(_scan_file(path, root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """CLI entry: `python -m build_vs_buy.secretscan <path>`."""

    args = list(sys.argv[1:] if argv is None else argv)
    root = Path(args[0] if args else ".")
    findings = scan(root)
    if not findings:
        print('{"ok": true, "findings": 0}')
        return 0
    for finding in findings:
        print(f"{finding.path}:{finding.line}:{finding.kind}")
    return 1


def _files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    found: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in _SKIP_SUFFIXES:
            continue
        found.append(path)
    return found


def _scan_file(path: Path, root: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    try:
        display = path.relative_to(root).as_posix()
    except ValueError:
        display = path.as_posix()
    return scan_text(text, label=display)


if __name__ == "__main__":
    raise SystemExit(main())
