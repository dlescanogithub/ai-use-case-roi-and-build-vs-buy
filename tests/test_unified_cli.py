"""The top-level CLI dispatches to both modules."""

from __future__ import annotations

from pathlib import Path

import pytest

from roi_and_build_vs_buy.cli import main


def test_decide_score_through_the_dispatcher(tmp_path: Path) -> None:
    out = tmp_path / "score.md"
    code = main(
        [
            "decide",
            "score",
            "--weights",
            "examples/bruma_freight/weights.yaml",
            "--scores",
            "examples/bruma_freight/scores.yaml",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    text = out.read_text(encoding="utf-8")
    assert "Tool: roi_and_build_vs_buy 0.2.0" in text
    assert "python -m roi_and_build_vs_buy decide score" in text


def test_unknown_group_exits() -> None:
    with pytest.raises(SystemExit) as caught:
        main(["nope"])
    assert caught.value.code == 2
