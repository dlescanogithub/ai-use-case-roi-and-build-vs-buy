"""Markdown reports for score, TCO, and the combined decision."""

from __future__ import annotations

from decimal import Decimal

from roi_and_build_vs_buy import __version__
from roi_and_build_vs_buy.build_vs_buy.matrix import CRITERION_LABELS, Ranking, ScoreCell
from roi_and_build_vs_buy.build_vs_buy.quantities import Quantity
from roi_and_build_vs_buy.build_vs_buy.sensitivity import Sensitivity
from roi_and_build_vs_buy.build_vs_buy.tco import TcoInput, TcoProjection, project, project_all


def render_score(ranking: Ranking, sensitivity: Sensitivity, *, case_dir: str) -> str:
    """Render the matrix and the sensitivity section."""

    lines = [
        f"# Score report — {ranking.case_id}",
        "",
        f"Tool: roi_and_build_vs_buy {__version__}",
        "",
        "Illustrative inputs, replace with your own.",
        (
            "Scores run from 1 to 5. A higher score is better for the buyer, "
            "including on cost and risk. A cell marked [EST] is an illustrative "
            "judgment, not a measurement."
        ),
        "Weights sum to 1. Figures in this section are weighted scores, not currency.",
        "",
        _ranking_table(ranking),
        "",
        _sensitivity_section(sensitivity),
        "",
        "## Reproduce",
        "",
        "```bash",
        (
            "python -m roi_and_build_vs_buy decide score "
            f"--weights {case_dir}/weights.yaml "
            f"--scores {case_dir}/scores.yaml --out out/score.md"
        ),
        "```",
        "",
    ]
    return "\n".join(lines)


def render_tco(model: TcoInput, projections: tuple[TcoProjection, ...]) -> str:
    """Render cash curves, break-even, and scenarios."""

    lines = [
        f"# TCO report — {model.title}",
        "",
        f"Tool: roi_and_build_vs_buy {__version__}",
        f"As of: {model.as_of}",
        f"Organisation: {model.org} (fictional)",
        "Illustrative inputs, replace with your own.",
        ("All currency figures are **simulated**, **[EST]**, and illustrative unless a source row says sourced."),
        f"Horizon: {model.horizon_years} years. Currency: {model.currency}.",
        "",
    ]
    for projection in projections:
        lines.extend(_projection_section(projection))
    lines.extend(
        [
            "## Reproduce",
            "",
            "```bash",
            "python -m roi_and_build_vs_buy decide tco --input <case>/tco.yaml --out out/tco.md",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def render_report(
    *,
    ranking: Ranking,
    sensitivity: Sensitivity,
    model: TcoInput,
    case_dir: str,
) -> str:
    """Render the combined decision report."""

    base = project(model, "base")
    projections = project_all(model)
    by_id = {item.option_id: item for item in base.options}
    cheapest = min(base.options, key=lambda item: (item.operating_total, item.option_id))
    lines = [
        f"# Build vs buy report — {model.title}",
        "",
        f"Tool: roi_and_build_vs_buy {__version__}",
        f"As of: {model.as_of}",
        f"Organisation: {model.org} (fictional)",
        "Illustrative inputs, replace with your own.",
        "Status of this case: implemented worked example. Inputs are synthetic.",
        (
            "Every score and every currency figure below is **[EST]** and illustrative. "
            "Currency figures are also **simulated**."
        ),
        "This command writes a file. It does not call a model, a vendor, or the network.",
        "",
        "## Weighted ranking",
        "",
        ("A higher score is better on every criterion, including 3-year TCO, vendor risk, and exit cost."),
        "",
        _ranking_table(ranking),
        "",
        "## Why each cell has that score",
        "",
    ]
    for ranked in ranking.ranked:
        lines.append(f"### {ranked.label} (`{ranked.option_id}`)")
        lines.append("")
        for name, cell in ranked.cells.items():
            lines.append(f"- **{CRITERION_LABELS[name]}** ({_score_text(cell)}/5): {cell.rationale}")
        lines.append("")
    lines.extend([_sensitivity_section(sensitivity), "", "## Base cash curves", ""])
    lines.extend(_projection_section(base))
    lines.extend(
        [
            "## Where the matrix and the cash model meet",
            "",
            (
                f"Weighted winner: `{ranking.winner.option_id}`. "
                f"Lowest base-scenario operating total: `{cheapest.option_id}` "
                f"at {cheapest.operating_total} {model.currency}, simulated."
            ),
            "",
        ]
    )
    if cheapest.option_id == ranking.winner.option_id:
        lines.append("On this case the weighted winner and the lowest operating total are the same option.")
    else:
        lines.append(
            "On this case the weighted winner and the lowest operating total "
            "are different options. The matrix is carrying control, risk, "
            "compliance, and exit, which the cash total does not. "
            "The decision owner has to say which of those stories they are buying."
        )
    lines.extend(
        [
            "",
            "### Operating totals by option",
            "",
            "| Option | Operating USD | With exit USD |",
            "| --- | ---: | ---: |",
        ]
    )
    for ranked in ranking.ranked:
        cash = by_id[ranked.option_id]
        lines.append(f"| {ranked.label} | {cash.operating_total} | {cash.total_with_exit} |")
    lines.extend(["", "## Scenarios", ""])
    for projection in projections:
        winner_cash = min(projection.options, key=lambda item: (item.operating_total, item.option_id))
        lines.append(
            f"- `{projection.scenario_id}` ({projection.scenario_label}): "
            f"lowest operating total is `{winner_cash.option_id}` "
            f"at {winner_cash.operating_total} {model.currency}, simulated [EST]."
        )
    lines.extend(
        [
            "",
            "## Provenance",
            "",
            "Every driver in the TCO file is an envelope with `source`, `date`, and `estimate`. "
            "The loader rejects a bare number and rejects a USD figure marked `estimate: false` "
            "when the source has no https URL.",
            "",
            "| Driver | Value | Unit | Estimate | Date | Source |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )
    lines.extend(_provenance_rows(model))
    lines.extend(
        [
            "",
            "## Reproduce",
            "",
            "```bash",
            f"python -m roi_and_build_vs_buy decide report --case {case_dir} --out out/report.md",
            "```",
            "",
            "Cost of that command: 0 USD.",
            "",
        ]
    )
    return "\n".join(lines)


def _score_text(cell: ScoreCell) -> str:
    if cell.estimate:
        return f"{cell.score} [EST]"
    return str(cell.score)


def _stability_reading(sensitivity: Sensitivity) -> str:
    held = sum(1 for item in sensitivity.scenarios if item.winner_held)
    total = len(sensitivity.scenarios)
    return (
        f"Winner stability is {held} of {total} feasible shifts on this grid, "
        "shown as a percentage rounded to two decimals. "
        "It is the share of those shifts that keep the same first-place option. "
        "It is not a probability that the decision is right, and it is not a field result. "
        "The scores and weights underneath it are illustrative [EST]."
    )


def _ranking_table(ranking: Ranking) -> str:
    names = list(ranking.weights.keys())
    header = [
        "| Rank | Option | Id | " + " | ".join(CRITERION_LABELS[name] for name in names) + " | Total |",
        "| ---: | --- | --- | " + " | ".join("---:" for _ in names) + " | ---: |",
    ]
    rows = []
    for index, option in enumerate(ranking.ranked, start=1):
        scores = " | ".join(_score_text(option.cells[name]) for name in names)
        total = option.total.quantize(Decimal("0.0001"))
        rows.append(f"| {index} | {option.label} | `{option.option_id}` | {scores} | {total} |")
    return "\n".join([*header, *rows])


def _sensitivity_section(sensitivity: Sensitivity) -> str:
    lines = [
        "## Sensitivity",
        "",
        (
            f"Rank stability (full order unchanged): **{sensitivity.rank_stability_pct}%**. "
            f"Winner stability: **{sensitivity.winner_stability_pct}%**."
        ),
        "",
        _stability_reading(sensitivity),
        "",
        (
            f"Grid: shift one weight by -0.10, -0.05, +0.05, or +0.10, then rescale the others "
            f"so they still sum to 1. Feasible scenarios: {len(sensitivity.scenarios)}. "
            f"A weight must stay inside 0.01 and 0.90."
        ),
        "",
        "| Criterion | Delta | Winner | Winner held | Full rank held |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for item in sensitivity.scenarios:
        lines.append(
            f"| {CRITERION_LABELS[item.criterion]} | {item.delta} | `{item.winner}` | "
            f"{'yes' if item.winner_held else 'no'} | {'yes' if item.full_rank_held else 'no'} |"
        )
    lines.extend(["", "### What would have to change to flip the decision", ""])
    if not sensitivity.flips:
        lines.append("No one-at-a-time weight change inside the searched band flips the winner.")
        return "\n".join(lines)
    for flip in sensitivity.flips:
        lines.append(
            f"- {CRITERION_LABELS[flip.criterion]} {flip.direction} by {flip.delta} "
            f"(new weight {flip.new_weight}) flips the winner to `{flip.new_winner}`."
        )
    lines.append("A criterion missing from this list stays put inside the searched band.")
    return "\n".join(lines)


def _projection_section(projection: TcoProjection) -> list[str]:
    lines = [
        f"### Scenario `{projection.scenario_id}` — {projection.scenario_label}",
        "",
        "USD, simulated, [EST].",
        "",
    ]
    for option in projection.options:
        lines.append(f"#### {option.label} (`{option.option_id}`)")
        lines.append("")
        component_names = list(option.years[-1].components.keys())
        lines.append("| Year | " + " | ".join(component_names) + " | Spend | Cumulative |")
        lines.append("| ---: | " + " | ".join("---:" for _ in component_names) + " | ---: | ---: |")
        for year in option.years:
            cells = " | ".join(str(year.components.get(name, Decimal(0))) for name in component_names)
            lines.append(f"| {year.year} | {cells} | {year.spend} | {year.cumulative} |")
        lines.append("")
        lines.append(
            f"Operating total {option.operating_total} USD. "
            f"Exit {option.exit_cost} USD. "
            f"With exit {option.total_with_exit} USD. Simulated."
        )
        lines.append("")
    if projection.break_evens:
        lines.append("Break-even against build:")
        lines.append("")
        for item in projection.break_evens:
            lines.append(f"- `{item.buy_option_id}` operating: {item.operating_note}")
            lines.append(f"- `{item.buy_option_id}` with exit: {item.with_exit_note}")
        lines.append("")
    return lines


def _provenance_rows(model: TcoInput) -> list[str]:
    rows: list[tuple[str, object]] = [
        ("assumptions.volume_growth_per_year", model.volume_growth_per_year),
        ("build.engineering_hours", model.build.engineering_hours),
        ("build.engineering_rate_per_hour", model.build.engineering_rate_per_hour),
        ("build.infra_per_year", model.build.infra_per_year),
        ("build.runs_per_year", model.build.runs_per_year),
        ("build.tokens_per_run", model.build.tokens_per_run),
        ("build.cost_per_1k_tokens", model.build.cost_per_1k_tokens),
        ("build.maintenance_pct_of_initial_build", model.build.maintenance_pct_of_initial_build),
        ("build.eval_ops_hours_per_year", model.build.eval_ops_hours_per_year),
        ("build.review_hours_per_year", model.build.review_hours_per_year),
    ]
    lines: list[str] = []

    def add(name: str, quantity: Quantity) -> None:
        flag = "[EST] illustrative" if quantity.estimate else "sourced"
        lines.append(
            f"| `{name}` | {quantity.value} | {quantity.unit} | {flag} | {quantity.date} | {quantity.source} |"
        )

    for name, quantity in rows:
        assert isinstance(quantity, Quantity)
        add(name, quantity)
    for spec in model.buy_options:
        prefix = spec.option_id
        add(f"{prefix}.seats", spec.seats)
        add(f"{prefix}.license_per_seat_per_year", spec.license_per_seat_per_year)
        add(f"{prefix}.integration_hours", spec.integration_hours)
        add(f"{prefix}.integration_rate_per_hour", spec.integration_rate_per_hour)
        add(f"{prefix}.exit_cost", spec.exit_cost)
        add(f"{prefix}.annual_price_increase", spec.annual_price_increase)
        for index, tier in enumerate(spec.usage_tiers):
            add(f"{prefix}.usage_tiers[{index}].price_per_run", tier.price_per_run)
    return lines
