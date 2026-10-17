# Scope

No fees, no day rates, no proposal prices. This is a portfolio calculator.

## Phase 0 — implemented

A deterministic monthly model, validation, tornado, three named scenarios, seeded Monte Carlo (triangular and PERT), CSV, an XLSX with live formulas, Markdown and HTML, an inline SVG, EN/ES one-pagers, an invariant eval gate, and a forced regression that exits non-zero.

Exit criteria for this phase, checked in this repo:

- `python3 -m pytest` coverage at least 80% (measured 92.60% on 2026-10-17, 54 passed).
- `python -m roi_model.evalkit` exits 0.
- `python -m roi_model.evalkit.regression` exits non-zero.
- One-pagers match the assumption files and are tagged [EST] / simulated.
- Default run cost is zero. No paid API.

## Phase 1 — design only

Live connectors (ticket export, warehouse feed, spreadsheet on a share). Not built. A connector would be a new input path with the same validation, still behind a human who commits the refreshed YAML. It would not auto-publish a one-pager.

## Phase 2 — design only

A dashboard. Not built. The HTML report is a static file. A dashboard would need an owner, a refresh rule, and a rule that [EST] and measured numbers cannot share a color without a label.

## Assumptions

- One currency, USD in the sample files.
- One case at a time. No portfolio optimization across use cases.
- Monthly steps are enough. No hourly simulation.
- The fixed run cost does not scale down during the ramp.
- Adoption is linear up to 1, then flat.
- The discount rate is annual, converted to an effective monthly rate.
- Excel payback formulas cover the sheet's month rows (360). Python uses the same 360-month search.

## Out of scope

Tax, depreciation books, multi-currency, hiring lead time, queueing, model-quality benchmarks, prompt design, vendor selection, production rollout, authentication, and any real client's numbers.

## Exit

Phase 0 is the whole product of this repository. Later phases are not started. There is no fee to "stay in phase 0".
