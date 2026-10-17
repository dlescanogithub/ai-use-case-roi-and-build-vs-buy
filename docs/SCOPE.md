# Scope

No fees, no day rates, no proposal prices. This is a portfolio calculator with two modules.

## Phase 0 — implemented

The decision kit and the monthly ROI model, sharing the `[EST]` tag.

Decision kit: weighted matrix, winner stability, 3-year TCO, scenarios, break-even year, CLI reports, two worked examples (Bruma Freight, Cedro Records), an invariant gate, and a forced regression that exits non-zero.

ROI model: monthly NPV, payback, break-even, unit cost, quality adjustment, tornado, three named scenarios, seeded Monte Carlo, CSV, an XLSX with live formulas, Markdown and HTML, an inline SVG, EN/ES one-pagers, an invariant gate, and a forced regression that exits non-zero.

Exit criteria for this phase, checked in this repo on 2026-10-17, package 0.2.0, Python 3.12.3:

- `python3 -m pytest` coverage at least 80% (measured 91.02%, 80 passed).
- `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit` exits 0.
- `python3 -m roi_and_build_vs_buy.evalkit.roi_regression` exits non-zero.
- `python3 -m roi_and_build_vs_buy.evalkit.decide_regression` exits non-zero.
- One-pagers and the committed decision reports match a fresh CLI run and are tagged [EST] / simulated.
- Default run cost is zero. No paid API.

## Phase 1 — design only

Replace `[EST]` inputs with measurements, one field at a time, in a private file. A live connector (ticket export, warehouse feed, a quote feed) is not built. A connector would be a new input path with the same validation, still behind a person who commits the refreshed YAML. It would not auto-publish a one-pager or accept an ADR.

## Phase 2 — design only

A dashboard, or a gated effect such as sending a reply, moving a ticket, or placing a call. Not built. The HTML report is a static file. A dashboard would need an owner, a refresh rule, and a rule that [EST] and measured numbers cannot share a label.

## Assumptions

- One currency, USD in the sample files.
- One case at a time. No portfolio optimization across use cases.
- The decision horizon is 3 years. The ROI horizon in the sample files is 36 months.
- Monthly ROI steps are enough. No hourly simulation.
- The fixed ROI run cost does not scale down during the ramp.
- Adoption in the ROI model is linear up to 1, then flat.
- The discount rate is annual, converted to an effective monthly rate.
- Excel payback formulas cover the sheet's month rows (360). Python uses the same 360-month search.
- Decision scores run from 1 to 5. Higher is better, including on cost and risk.
- Exit cost is outside the operating total and is added in the last year.

## Out of scope

Tax, depreciation books, multi-currency, hiring lead time, queueing, model-quality benchmarks, prompt design, production rollout, authentication, procurement workflow, live price scraping, and any real client's numbers.

## Exit

Phase 0 is the whole product of this repository. Later phases are not started. There is no fee to stay in phase 0.
