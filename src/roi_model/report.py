"""Markdown and HTML reports, plus EN/ES one-pagers.

Numbers are formatted from a model run. Inputs stay tagged [EST].
Outputs of the run are simulated. Nothing here is a vendor price.
"""

from __future__ import annotations

from html import escape

from roi_model import __version__
from roi_model.analysis import Analysis
from roi_model.model import ModelResult, Payback
from roi_model.svgchart import tornado_svg

MEASURED_SLOT = (
    "Measured per-run cost slot: plug a figure from agent-runtime-evals "
    "(private) only through a file with status measured. Stub numbers are not "
    "vendor prices and are not applied unless that status is set."
)


def money(amount: float, currency: str) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}{currency} {abs(amount):,.2f}"


def months(value: float | None) -> str:
    if value is None:
        return "never"
    return f"{value:.2f}"


def _payback_phrase(payback: Payback) -> str:
    if payback.status == "never":
        return f"never ({payback.reason})"
    if payback.status == "immediate":
        return "immediate (0 months)"
    return f"{payback.months:.2f} months"


def _payback_phrase_es(payback: Payback) -> str:
    if payback.status == "never":
        return "nunca (en régimen el ahorro mensual no recupera la inversión)"
    if payback.status == "immediate":
        return "inmediato (0 meses)"
    return f"{payback.months:.2f} meses"


def render_markdown(
    analysis: Analysis,
    *,
    generated_at: str,
    command: str,
    git_revision: str,
) -> str:
    case = analysis.case
    result = analysis.result
    currency = case.meta.currency
    lines = [
        f"# ROI report: {case.meta.title}",
        "",
        f"- Generated: {generated_at}",
        f"- Command: `{command}`",
        f"- Package version: {__version__}",
        f"- Git revision: {git_revision}",
        "- Data: 100% synthetic. Every input is [EST] unless a measured-cost file was applied.",
        "- Outputs: simulated.",
        f"- Company: {case.meta.company} (fictional).",
        "",
        "## Decision",
        "",
        "This model does not approve an action, send a message, or spend money.",
        "A person has to read the assumptions and decide.",
        "",
        "## Result",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| Net monthly savings, steady state | {money(result.net_monthly_steady, currency)} |",
        f"| Payback | {_payback_phrase(result.payback)} |",
        _break_even_row(result, currency),
        f"| 3-year NPV | {money(result.npv, currency)} |",
        (f"| Cost per completed item, with reviewer time | {money(result.unit.cost_per_completed_item, currency)} |"),
        (f"| Quality-adjusted savings per item | {money(result.unit.quality_adjusted_savings, currency)} |"),
        (f"| Residual error cost per item | {money(result.unit.residual_error_cost, currency)} |"),
        "",
        "## Unit economics [EST]",
        "",
        "| Piece | Per item |",
        "| --- | --- |",
        f"| Manual labor | {money(result.unit.manual_labor_cost, currency)} |",
        f"| Manual expected error | {money(result.unit.manual_error_cost, currency)} |",
        (f"| Agent run (tokens x price, or measured override) | {money(result.unit.agent_run_cost, currency)} |"),
        f"| Reviewer time | {money(result.unit.review_cost, currency)} |",
        f"| Residual error | {money(result.unit.residual_error_cost, currency)} |",
        "",
        "## Scenarios (simulated)",
        "",
        "| Scenario | Net monthly | Payback | NPV |",
        "| --- | --- | --- | --- |",
    ]
    for outcome in analysis.scenario_outcomes:
        net = money(outcome.result.net_monthly_steady, currency)
        payback = _payback_phrase(outcome.result.payback)
        npv = money(outcome.result.npv, currency)
        lines.append(f"| {outcome.name} | {net} | {payback} | {npv} |")
    mc = analysis.monte_carlo
    lines.extend(
        [
            "",
            "## Monte Carlo (simulated)",
            "",
            f"Draws: {mc.draws}. Seed: {mc.seed}.",
            "",
            "|  | P10 | P50 | P90 |",
            "| --- | --- | --- | --- |",
            (
                f"| NPV | {money(mc.npv_p10, currency)} | {money(mc.npv_p50, currency)} | "
                f"{money(mc.npv_p90, currency)} |"
            ),
            (
                f"| Net monthly | {money(mc.net_p10, currency)} | {money(mc.net_p50, currency)} | "
                f"{money(mc.net_p90, currency)} |"
            ),
            "",
            "## Which assumptions move the result most",
            "",
            "Tornado (absolute swing of 3-year NPV):",
            "",
            "| Parameter | Low NPV | High NPV | Swing (high minus low) |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in analysis.tornado[:8]:
        lines.append(
            f"| {row.name} | {money(row.low_npv, currency)} | {money(row.high_npv, currency)} | "
            f"{money(row.swing, currency)} |"
        )
    lines.extend(["", "Rank correlation of each draw with NPV (Spearman):", ""])
    for name, score in mc.drivers[:8]:
        lines.append(f"- {name}: {score:.3f}")
    lines.extend(
        [
            "",
            "## Assumptions",
            "",
            "| Parameter | Value | Range | Why it is here |",
            "| --- | --- | --- | --- |",
        ]
    )
    for spec in case.parameters.values():
        lines.append(f"| {spec.name} | {spec.value} {spec.unit} | {spec.low} to {spec.high} | {spec.rationale} |")
    lines.extend(
        [
            "",
            "## Measured-cost slot",
            "",
            MEASURED_SLOT,
            ("Applied in this run: yes." if analysis.measured_override else "Applied in this run: no."),
            "",
            case.meta.measured_cost_slot,
            "",
        ]
    )
    return "\n".join(lines)


def render_html(analysis: Analysis, markdown_preface: str, svg: str) -> str:
    """Self-contained HTML. The SVG is inlined. No remote assets."""
    title = escape(analysis.case.meta.title)
    body = escape(markdown_preface)
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{title}</title>"
        "<style>body{font-family:sans-serif;margin:2rem;line-height:1.45}"
        "pre{white-space:pre-wrap}</style></head><body>"
        f"<h1>{title}</h1>"
        "<p>Simulated report. Inputs are [EST]. This page does not call a network.</p>"
        f"{svg}"
        f"<pre>{body}</pre></body></html>"
    )


def render_one_pager(
    analysis: Analysis,
    *,
    lang: str,
    generated_at: str,
    command: str,
    git_revision: str,
) -> str:
    if lang not in {"en", "es"}:
        raise ValueError("lang must be en or es")
    if lang == "en":
        return _one_pager_en(analysis, generated_at, command, git_revision)
    return _one_pager_es(analysis, generated_at, command, git_revision)


def _one_pager_en(analysis: Analysis, generated_at: str, command: str, git_revision: str) -> str:
    result = analysis.result
    currency = analysis.case.meta.currency
    top = ", ".join(row.name for row in analysis.tornado[:3])
    return "\n".join(
        [
            f"# {analysis.case.meta.title}",
            "",
            f"Generated {generated_at} by `{command}` (package {__version__}, git {git_revision}).",
            "Simulated. Every input is [EST]. This page is not a measured business result.",
            "",
            analysis.case.meta.narrative,
            "",
            "## What the model says",
            "",
            f"- Steady-state net monthly savings: {money(result.net_monthly_steady, currency)}.",
            f"- Payback: {_payback_phrase(result.payback)}.",
            f"- {_break_even_sentence(result, currency)}",
            f"- 3-year NPV: {money(result.npv, currency)}.",
            (
                "- Cost per completed item, including reviewer time: "
                f"{money(result.unit.cost_per_completed_item, currency)}."
            ),
            (
                "- Quality-adjusted savings per item (after residual errors): "
                f"{money(result.unit.quality_adjusted_savings, currency)}."
            ),
            f"- Assumptions that move NPV the most: {top}.",
            "",
            "## What a person still has to do",
            "",
            "The model does not approve a purchase, a vendor, or a rollout.",
            "Replace [EST] inputs with measurements before anyone treats the NPV as a plan.",
            "",
            "## Link to measured data",
            "",
            MEASURED_SLOT,
            "Applied in this run: " + ("yes." if analysis.measured_override else "no."),
            "",
        ]
    )


def _one_pager_es(analysis: Analysis, generated_at: str, command: str, git_revision: str) -> str:
    result = analysis.result
    currency = analysis.case.meta.currency
    top = ", ".join(row.name for row in analysis.tornado[:3])
    payback = _payback_phrase_es(result.payback)
    return "\n".join(
        [
            f"# {analysis.case.meta.title}",
            "",
            (f"Generado el {generated_at} con `{command}` (paquete {__version__}, git {git_revision})."),
            "Simulado. Cada insumo es [EST]. Esto no es un resultado medido de un negocio real.",
            "",
            "Mirá: el número de abajo sale de supuestos, no de una factura.",
            "Fijate que el tiempo de revisión y el error que queda están adentro del cálculo.",
            "",
            analysis.case.meta.narrative_es,
            "",
            "## Qué dice el modelo",
            "",
            f"- Ahorro mensual neto en régimen: {money(result.net_monthly_steady, currency)}.",
            f"- Recupero de la inversión: {payback}.",
            f"- {_break_even_sentence_es(result, currency)}",
            f"- VPN a 3 años: {money(result.npv, currency)}.",
            (
                "- Costo por ítem terminado, con el tiempo de quien revisa: "
                f"{money(result.unit.cost_per_completed_item, currency)}."
            ),
            (
                "- Ahorro por ítem ajustado por calidad (después del error residual): "
                f"{money(result.unit.quality_adjusted_savings, currency)}."
            ),
            f"- Los supuestos que más mueven la VPN: {top}.",
            "",
            "## Lo que una persona tiene que hacer",
            "",
            "El modelo no aprueba una compra, un proveedor ni un despliegue.",
            "Tenés que cambiar los [EST] por mediciones antes de tratar la VPN como un plan.",
            "",
            "## Lugar para un dato medido",
            "",
            (
                "Slot de costo medido por corrida: podés enchufar un número medido en "
                "agent-runtime-evals (privado) solo con un archivo en status measured. "
                "Los stubs no son precios de proveedor y no se aplican si el status no es measured."
            ),
            "Aplicado en esta corrida: " + ("sí." if analysis.measured_override else "no."),
            "",
        ]
    )


def chart_for(analysis: Analysis) -> str:
    return tornado_svg(analysis.tornado)


def _break_even_row(result: ModelResult, currency: str) -> str:
    if result.break_even_volume is None:
        return f"| Break-even volume | none ({result.break_even_reason}) |"
    return f"| Break-even volume | {result.break_even_volume:,.2f} items/month ({result.break_even_reason}) |"


def _break_even_sentence(result: ModelResult, currency: str) -> str:
    del currency
    if result.break_even_volume is None:
        return f"Break-even volume: none. {result.break_even_reason}."
    return f"Break-even volume: {result.break_even_volume:,.2f} items/month. {result.break_even_reason}."


def _break_even_sentence_es(result: ModelResult, currency: str) -> str:
    del currency
    if result.break_even_volume is None:
        return "Volumen de equilibrio: no hay. El ahorro por ítem no cubre el costo fijo."
    volume = f"{result.break_even_volume:,.2f}"
    return (
        f"Volumen de equilibrio: {volume} ítems por mes "
        "(ahorro mensual neto en cero; la implementación no entra en este volumen)."
    )
