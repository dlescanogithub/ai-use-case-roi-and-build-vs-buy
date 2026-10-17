# Metrics

Two layers. Do not mix them.

## What this repository actually measures

| Metric | Measured value | Date | Command |
| --- | --- | --- | --- |
| Test coverage | 91.02% | 2026-10-17 | `python3 -m pytest` (Python 3.12.3, package 0.2.0) |
| Tests passed | 80 | 2026-10-17 | same |
| Both eval gates | exit 0, printed `BOTH EVAL GATES PASSED` | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit` |
| Bruma Freight winner stability | 67.86 (19 of 28) | 2026-10-17 | same command, JSON `cases[0].winner_stability_pct` |
| Cedro Records winner stability | 100.00 (28 of 28) | 2026-10-17 | same command, JSON `cases[1].winner_stability_pct` |
| Forced ROI regression | exit 1, savings identity and break-even failed on the wrong formula | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.roi_regression` |
| Forced decision regression | exit 1, `golden_winner: expected build got vendor_b`, winner stability 59.09 below the 67.86 floor | 2026-10-17 | `DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.decide_regression` |
| Secret scan | `{"ok": true, "findings": 0}` | 2026-10-17 | `python3 -m roi_and_build_vs_buy.secretscan .` |
| Types | no issues in 55 source files | 2026-10-17 | `python3 -m mypy` |
| Publish wall time | 0.751 seconds | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` |
| Decision-report latency | p50 0.152 s, p95 0.158 s | 2026-10-17 | 30 runs of `python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out /tmp/lat-N.md`, index `round(p/100*(n-1))` |
| Default run cost | USD 0 | 2026-10-17 | publish command above, template provider, cost cap 0 |

Re-running the suite can change the coverage by a point if tests are added. Quote the command and the date with any new number.

Simulated outputs (inputs [EST], not metrics of a business): base refund NPV USD 180,923.12, payback 17.08 months, pessimistic payback never. See `docs/results/refund_desk.json`. Bruma operating totals are in `docs/examples/bruma-freight-report.md`.

## What success would mean on a real case, later

These are not measured here. They are the questions a pilot would have to answer. Mark any future number the same way: measured, with a date and a command, or [EST].

| Metric | Why it would matter | Status here |
| --- | --- | --- |
| Absolute error of forecast net savings versus a shadow month | Tells you if the YAML was fantasy | Not measured. No shadow month exists |
| Share of case-file inputs replaced by a measurement | Discovery completeness | 0. The 23-case eval bill is recorded beside the case files and was not written into them |
| Review rate in the pilot versus the assumed rate | The pessimistic ROI case hinges on this | Not measured |
| Residual error rate on a labeled sample | Quality adjustment | Not measured. No model is called |
| Winner stability after the client's own scores replace the example | Tells you if the ranking was an artifact of the illustration | Not measured. The 67.86% is the committed Bruma file |
| Time from assumption change to a regenerated report | Operational hygiene | The publish and `decide report` commands above are the mechanism. A human still has to read them |
| Incidents where a simulated number was presented as actual savings | Governance failure | None recorded, because this repo has no audience beyond the file |

A green test suite is not a successful rollout.
