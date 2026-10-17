# Refund desk agent

Generated 2026-10-17T15:16:12.798911+00:00 by `python -m roi_model.cli publish-docs` (package 0.1.0, git 130b921).
Simulated. Every input is [EST]. This page is not a measured business result.

Puerto Gris Parcel Co. is a fictional carrier. A back-office agent would draft refund decisions for returned parcels. A person still approves the ones the policy sends to review. None of these figures are measurements.

## What the model says

- Steady-state net monthly savings: USD 12,775.15.
- Payback: 17.08 months.
- Break-even volume: 412.43 items/month. steady-state monthly volume where net monthly savings are zero.
- 3-year NPV: USD 180,923.12.
- Cost per completed item, including reviewer time: USD 1.34.
- Quality-adjusted savings per item (after residual errors): USD 6.06.
- Assumptions that move NPV the most: volume_per_day, manual_minutes_per_item, loaded_cost_per_hour.

## What a person still has to do

The model does not approve a purchase, a vendor, or a rollout.
Replace [EST] inputs with measurements before anyone treats the NPV as a plan.

## Link to measured data

Measured per-run cost slot: plug a figure from agent-runtime-evals (private) only through a file with status measured. Stub numbers are not vendor prices and are not applied unless that status is set.
Applied in this run: no.
