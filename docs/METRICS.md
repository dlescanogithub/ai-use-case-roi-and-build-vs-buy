# Metrics

Two layers. Do not mix them.

## What this repository actually measures

| Metric | Measured value | Date | Command |
| --- | --- | --- | --- |
| Test coverage | 92.60% | 2026-10-17 | `python3 -m pytest` (Python 3.12.3, package 0.1.0) |
| Tests passed | 54 | 2026-10-17 | same |
| Eval gate | exit 0 | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_model.evalkit` |
| Forced regression | exit 1, savings identity and break-even failed on the wrong formula | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_model.evalkit.regression` |
| Secret scan | no findings | 2026-10-17 | `python3 -m roi_model.secretscan` |
| Publish wall time | 0.728 seconds | 2026-10-17 | `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_model.cli publish-docs` |
| Default run cost | USD 0 | 2026-10-17 | same command, template provider, cost cap 0 |

Re-running the suite can change the coverage by a point if tests are added. Quote the command and the date with any new number.

Simulated outputs (inputs [EST], not metrics of a business): base refund NPV USD 180,923.12, payback 17.08 months, pessimistic payback never. See `docs/results/refund_desk.json`.

## What success would mean on a real case, later

These are not measured here. They are the questions a pilot would have to answer. Mark any future number the same way: measured, with a date and a command, or [EST].

| Metric | Why it would matter | Status here |
| --- | --- | --- |
| Absolute error of forecast net savings versus a shadow month | Tells you if the YAML was fantasy | Not measured. No shadow month exists |
| Share of case-file inputs replaced by a measurement | Discovery completeness | 0. The 23-case eval bill is recorded beside the case files and was not written into them |
| Review rate in the pilot versus the assumed rate | The pessimistic case hinges on this | Not measured |
| Residual error rate on a labeled sample | Quality adjustment | Not measured. No model is called |
| Time from assumption change to a regenerated one-pager | Operational hygiene | The publish command above is the mechanism. A human still has to read it |
| Incidents where a simulated number was presented as actual savings | Governance failure | None recorded, because this repo has no audience beyond the file |

A green test suite is not a successful rollout.
