"""Static tornado chart as inline SVG. No PNG and no external assets."""

from __future__ import annotations

from xml.sax.saxutils import escape

from roi_model.sensitivity import TornadoRow


def _compact(value: float) -> str:
    sign = "-" if value < 0 else ""
    magnitude = abs(value)
    if magnitude >= 1_000_000:
        return f"{sign}{magnitude / 1_000_000:.1f}M"
    if magnitude >= 1_000:
        return f"{sign}{magnitude / 1_000:.1f}k"
    return f"{sign}{magnitude:.0f}"


def tornado_svg(rows: tuple[TornadoRow, ...] | list[TornadoRow], *, limit: int = 10) -> str:
    """Horizontal bars from the low NPV to the high NPV, with a base marker."""
    chosen = list(rows)[:limit]
    width = 760
    label_w = 210
    right_pad = 70
    row_h = 28
    top = 36
    height = top + max(1, len(chosen)) * row_h + 24
    plot_w = width - label_w - right_pad
    title = "Tornado of 3-year NPV"
    if not chosen:
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="80" '
            f'role="img"><title>{title}</title><text x="16" y="40">'
            "No parameters to chart.</text></svg>"
        )
    values = [row.base_npv for row in chosen]
    for row in chosen:
        values.extend((row.low_npv, row.high_npv))
    low_bound = min(values)
    high_bound = max(values)
    if high_bound == low_bound:
        high_bound = low_bound + 1.0

    def x_of(value: float) -> float:
        return label_w + (value - low_bound) / (high_bound - low_bound) * plot_w

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" role="img">',
        f"<title>{title}</title>",
        "<desc>One-at-a-time NPV swings. Simulated. Inputs are assumptions.</desc>",
        f'<text x="16" y="22" font-family="sans-serif" font-size="14">{title}</text>',
    ]
    base_x = x_of(chosen[0].base_npv)
    parts.append(
        f'<line x1="{base_x:.1f}" y1="{top - 8}" x2="{base_x:.1f}" y2="{height - 12}" '
        'stroke="#444" stroke-dasharray="3 3"/>'
    )
    for index, row in enumerate(chosen):
        y = top + index * row_h
        start = min(row.low_npv, row.high_npv)
        end = max(row.low_npv, row.high_npv)
        color = "#3d6f8d" if row.high_npv >= row.low_npv else "#8d4a3d"
        bar_w = max(1.0, x_of(end) - x_of(start))
        parts.append(f'<rect x="{x_of(start):.1f}" y="{y + 6}" width="{bar_w:.1f}" height="14" fill="{color}"/>')
        parts.append(f'<text x="8" y="{y + 18}" font-family="sans-serif" font-size="12">{escape(row.name)}</text>')
        parts.append(
            f'<text x="{width - 8}" y="{y + 18}" font-family="sans-serif" font-size="11" '
            f'text-anchor="end">{_compact(row.swing)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)
