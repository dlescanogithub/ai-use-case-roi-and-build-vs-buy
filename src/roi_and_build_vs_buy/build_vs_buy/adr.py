"""Render a build-vs-buy ADR from a scored case."""

from __future__ import annotations

from decimal import Decimal

from roi_and_build_vs_buy import __version__
from roi_and_build_vs_buy.build_vs_buy.matrix import CRITERION_LABELS, Ranking
from roi_and_build_vs_buy.build_vs_buy.sensitivity import Sensitivity
from roi_and_build_vs_buy.build_vs_buy.tco import TcoInput, TcoProjection


def render_adr(
    *,
    adr_id: str,
    ranking: Ranking,
    sensitivity: Sensitivity,
    model: TcoInput,
    projection: TcoProjection,
    case_dir: str,
) -> str:
    """Render the build-vs-buy ADR body for one worked example."""

    winner = ranking.winner
    lines: list[str] = [
        f"# ADR {adr_id}: Build vs buy — {model.title}",
        "",
        "- Status: proposed (fictional worked example, illustrative [EST] inputs)",
        f"- Date: {model.as_of}",
        f"- Tool: roi_and_build_vs_buy {__version__}",
        f"- Organisation: {model.org} (fictional)",
        f"- Case: `{case_dir}`",
        "",
        "## Decision",
        "",
        (
            f"On the weighted criteria, prefer **{winner.label}** (`{winner.option_id}`) "
            f"with score {_fmt(winner.total)}."
        ),
        "",
        (
            "This ADR records the matrix result and the cash result side by side. "
            "A person accepts, rejects, or revises it. The tool does not buy, provision, "
            "or contact a vendor."
        ),
        "",
        "## Options considered",
        "",
        "| Option | Id | Weighted score | 3-year operating USD | 3-year USD with exit |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    by_id = {item.option_id: item for item in projection.options}
    for ranked in ranking.ranked:
        cash = by_id[ranked.option_id]
        lines.append(
            f"| {ranked.label} | `{ranked.option_id}` | {_fmt(ranked.total)} | "
            f"{cash.operating_total} | {cash.total_with_exit} |"
        )
    lines.extend(
        [
            "",
            "Operating totals exclude exit. The with-exit column adds exit cost in the last year. "
            "Every score and every dollar figure in the source YAML is illustrative "
            "and marked [EST]. Dollar figures are simulated.",
            "",
            "## Criteria",
            "",
            "Scores run from 1 to 5. A higher score is better for the buyer, including on cost "
            "and risk. Weights sum to 1.",
            "",
            "| Criterion | Weight |",
            "| --- | ---: |",
        ]
    )
    for name, weight in ranking.weights.items():
        lines.append(f"| {CRITERION_LABELS[name]} | {weight} |")
    lines.extend(["", "### Rationales for the leading option", ""])
    for name, cell in winner.cells.items():
        marker = " [EST], illustrative" if cell.estimate else ""
        lines.append(f"- **{CRITERION_LABELS[name]}** ({cell.score}/5){marker}: {cell.rationale}")
    lines.extend(["", "## Cash picture (base scenario)", ""])
    for item in projection.break_evens:
        lines.append(f"- Against `{item.buy_option_id}`: {item.operating_note}")
        lines.append(f"- Against `{item.buy_option_id}` including exit: {item.with_exit_note}")
    cheapest = min(projection.options, key=lambda item: (item.operating_total, item.option_id))
    lines.extend(
        [
            "",
            (
                "Lowest 3-year operating total in the base scenario: "
                f"**{cheapest.label}** (`{cheapest.option_id}`) "
                f"at {cheapest.operating_total} USD, simulated."
            ),
            "",
            "## What would have to change to flip the decision",
            "",
        ]
    )
    if sensitivity.flips:
        for flip in sensitivity.flips:
            lines.append(
                f"- If **{CRITERION_LABELS[flip.criterion]}** weight {flip.direction}s by "
                f"{flip.delta} (new weight {flip.new_weight}) and the other weights scale "
                f"proportionally, the winner becomes `{flip.new_winner}`."
            )
        lines.append("- A criterion missing from this list stays put inside the searched band.")
    else:
        lines.append(
            "- Inside the searched band (each weight from 0.01 to 0.90), no one-at-a-time change flips the winner."
        )
    lines.extend(
        [
            "",
            (
                f"Winner stability under ±0.05 and ±0.10 one-at-a-time shifts: "
                f"{sensitivity.winner_stability_pct}% of feasible scenarios. "
                f"Full rank stability: {sensitivity.rank_stability_pct}%."
            ),
            "",
            "## Exit and revisit triggers",
            "",
            (f"- Revisit on or before **{_plus_months(model.as_of, 6)}** (six months after {model.as_of})."),
            "- Revisit sooner when any of these show up in a re-run of this case:",
            "  - The weighted winner changes.",
            "  - Winner stability falls below 50% on the same perturbation grid.",
            "  - A realized vendor increase exceeds the annual price-increase assumption.",
            "  - Build engineering hours exceed the build_overrun multiplier (1.5x).",
            "  - With-exit cash and the weighted ranking pick different options,",
            "    and the gap is larger than the exit cost already modeled.",
            "",
            (
                "Exit trigger for a buy choice: a failed export drill, a price increase "
                "above the modeled assumption, or a change in the data-use terms "
                "described in the score rationales. Exit trigger for a build choice: "
                "loss of the team that owns the eval set, or a time-to-value slip "
                "that fails the revisit above."
            ),
            "",
            "## Consequences",
            "",
            "- The decision record is this ADR plus the YAML inputs. Both stay in git.",
            ("- Re-running the report after an input change is the rollback. The previous ADR remains in history."),
            "- No vendor is contacted and no budget is committed by generating this file.",
            "",
            "## Reproduce",
            "",
            "```bash",
            (
                "python -m roi_and_build_vs_buy decide report "
                f"--case {case_dir} --out out/report.md "
                f"--adr-id {adr_id} --adr-out out/adr.md"
            ),
            "```",
            "",
            "Cost of that command: 0 USD. It does not call a model or a vendor API.",
            "",
        ]
    )
    return "\n".join(lines)


def _fmt(value: Decimal) -> str:
    return f"{value.quantize(Decimal('0.0001'))}"


def _plus_months(iso_date: str, months: int) -> str:
    year_s, month_s, day_s = iso_date.split("-")
    year = int(year_s)
    month = int(month_s) + months
    day = int(day_s)
    while month > 12:
        month -= 12
        year += 1
    return f"{year:04d}-{month:02d}-{day:02d}"
