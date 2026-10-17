"""Load a case directory: weights.yaml, scores.yaml, and tco.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from roi_and_build_vs_buy.build_vs_buy.errors import ValidationError
from roi_and_build_vs_buy.build_vs_buy.matrix import ScoreSheet, Weights, load_scores, load_weights
from roi_and_build_vs_buy.build_vs_buy.tco import TcoInput, load_tco


@dataclass(frozen=True)
class Case:
    """One fictional decision, loaded from a directory."""

    directory: Path
    weights: Weights
    scores: ScoreSheet
    tco: TcoInput


def load_case(directory: Path) -> Case:
    """Load the three YAML files and require matching ids."""

    weights = load_weights(directory / "weights.yaml")
    scores = load_scores(directory / "scores.yaml")
    tco = load_tco(directory / "tco.yaml")
    if len({weights.case_id, scores.case_id, tco.case_id}) != 1:
        raise ValidationError(
            [
                "case_id mismatch across weights.yaml, scores.yaml, and tco.yaml: "
                f"{weights.case_id}, {scores.case_id}, {tco.case_id}"
            ]
        )
    score_ids = {option.option_id for option in scores.options}
    tco_ids = {"build", *(option.option_id for option in tco.buy_options)}
    if score_ids != tco_ids:
        raise ValidationError([f"score options {sorted(score_ids)} must match TCO options {sorted(tco_ids)}"])
    if "build" not in score_ids:
        raise ValidationError(["scores must include an option id 'build'"])
    return Case(directory=directory, weights=weights, scores=scores, tco=tco)
