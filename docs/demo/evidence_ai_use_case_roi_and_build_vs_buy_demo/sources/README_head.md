Illustrative numbers, replace with your own

# AI use-case ROI and build-vs-buy

## Start here

This repo proves a local calculator: a weighted build-versus-buy score, a 3-year cash model, and a monthly ROI, with both eval gates green and both forced regressions red, and with no model call on the default path. It does not prove that a company saved the simulated NPV.
One command, cost 0 USD: `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python3 -m roi_and_build_vs_buy roi demo`
Walkthrough: [docs/HOW_IT_WORKS.md](docs/HOW_IT_WORKS.md). Value plan: [docs/BUSINESS_VALUE.md](docs/BUSINESS_VALUE.md).

The distribution name is `ai-use-case-roi-and-build-vs-buy`. The import package is `roi_and_build_vs_buy`, version 0.2.1. The command is `python -m roi_and_build_vs_buy` with subcommands `decide` and `roi`.

Puerto Gris Parcel Co., Bruma Freight, and Cedro Records are fictional. They are not clients and they are not employers.

## Problem

A build-versus-buy slide hides two questions: which option scores highest once control, risk, and exit are weighted, and which option is cheaper over three years. A token price then hides a third question: after review time, residual errors, a fixed monthly cost, and a slow ramp, does the sketch pay back. Those answers can diverge.

**Calculated result, from illustrative inputs:** on the fictional Bruma Freight case, winner stability is **67.86%**. That is 19 of 28 feasible weight shifts keeping `build` in first place.

- Date: 2026-10-17, and the same JSON fields again on 2026-10-22
- Version: `roi_and_build_vs_buy` 0.2.0
- Python: 3.12.3
- Command: `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit`
- Output: JSON field `cases[0].winner_stability_pct` = `"67.86"`

How to read 67.86%: the tool shifts one illustrative weight at a time by 0.05 or 0.10, drops shifts that would push a weight outside 0.01–0.90, rescales the rest so they still sum to 1, and counts how often `build` stays first. 19 of those 28 shifts keep `build`. The percentage is not a probability that building is the right choice, and it is not a success rate from a live desk. Cedro Records stays at 100.00% on the same grid (28 of 28).

**Simulated ROI, published 2026-10-17, same package:** command `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` finished in 0.751 seconds and wrote a 3-year NPV of **USD 180,923.12** for the fictional refund desk. Inputs are illustrative [EST]. The NPV is simulated. The pessimistic scenario never pays back (NPV USD -350,556.83). Full precision is in `docs/results/refund_desk.json`. That publish command was not re-timed on 2026-10-22.

Replace the inputs before you treat either figure as your decision. See [docs/REPLACE_THE_ASSUMPTIONS.md](docs/REPLACE_THE_ASSUMPTIONS.md).

## Architecture

```mermaid
flowchart TD
  decideYaml["decide YAML: weights, scores, TCO [EST]"] --> matrix["Weighted matrix"]
  decideYaml --> tco["3-year TCO"]
  matrix --> sens["Winner stability"]
  matrix --> decideReport["Decision report and ADR"]
