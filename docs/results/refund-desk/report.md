# ROI report: Refund desk agent

- Generated: 2026-10-17T15:16:12.798911+00:00
- Command: `python -m roi_model.cli publish-docs`
- Package version: 0.1.0
- Git revision: 130b921
- Data: 100% synthetic. Every input is [EST] unless a measured-cost file was applied.
- Outputs: simulated.
- Company: Puerto Gris Parcel Co. (fictional).

## Decision

This model does not approve an action, send a message, or spend money.
A person has to read the assumptions and decide.

## Result

| Metric | Value |
| --- | --- |
| Net monthly savings, steady state | USD 12,775.15 |
| Payback | 17.08 months |
| Break-even volume | 412.43 items/month (steady-state monthly volume where net monthly savings are zero) |
| 3-year NPV | USD 180,923.12 |
| Cost per completed item, with reviewer time | USD 1.34 |
| Quality-adjusted savings per item | USD 6.06 |
| Residual error cost per item | USD 0.50 |

## Unit economics [EST]

| Piece | Per item |
| --- | --- |
| Manual labor | USD 6.40 |
| Manual expected error | USD 1.50 |
| Agent run (tokens x price, or measured override) | USD 0.01 |
| Reviewer time | USD 1.33 |
| Residual error | USD 0.50 |

## Scenarios (simulated)

| Scenario | Net monthly | Payback | NPV |
| --- | --- | --- | --- |
| pessimistic | -USD 1,700.00 | never (steady-state net monthly savings are not positive; the case never pays back) | -USD 350,556.83 |
| base | USD 12,775.15 | 17.08 months | USD 180,923.12 |
| optimistic | USD 31,982.79 | 3.85 months | USD 874,596.57 |

## Monte Carlo (simulated)

Draws: 2000. Seed: 42.

|  | P10 | P50 | P90 |
| --- | --- | --- | --- |
| NPV | -USD 5,178.08 | USD 167,292.34 | USD 380,101.33 |
| Net monthly | USD 7,382.58 | USD 12,884.66 | USD 20,553.62 |

## Which assumptions move the result most

Tornado (absolute swing of 3-year NPV):

| Parameter | Low NPV | High NPV | Swing (high minus low) |
| --- | --- | --- | --- |
| volume_per_day | -USD 1,947.41 | USD 400,367.75 | USD 402,315.16 |
| manual_minutes_per_item | USD 26,458.58 | USD 412,619.92 | USD 386,161.34 |
| loaded_cost_per_hour | USD 89,209.80 | USD 329,957.26 | USD 240,747.46 |
| implementation_cost | USD 280,923.12 | USD 60,923.12 | -USD 220,000.00 |
| manual_error_rate | USD 108,517.86 | USD 289,531.00 | USD 181,013.13 |
| monthly_run_cost | USD 233,940.10 | USD 71,770.51 | -USD 162,169.58 |
| review_minutes | USD 238,847.32 | USD 84,382.78 | -USD 154,464.54 |
| cost_of_error | USD 137,479.97 | USD 282,290.47 | USD 144,810.50 |

Rank correlation of each draw with NPV (Spearman):

- manual_minutes_per_item: 0.499
- volume_per_day: 0.489
- loaded_cost_per_hour: 0.318
- implementation_cost: -0.305
- manual_error_rate: 0.264
- review_rate: -0.208
- cost_of_error: 0.197
- monthly_run_cost: -0.192

## Assumptions

| Parameter | Value | Range | Why it is here |
| --- | --- | --- | --- |
| volume_per_day | 120.0 items/day | 70.0 to 180.0 | [EST] Planning volume for a mid-size fictional returns desk, not a count from a warehouse. |
| working_days_per_month | 21.0 days/month | 20.0 to 23.0 | [EST] A conventional business month. It is not this company's calendar. |
| manual_minutes_per_item | 12.0 minutes | 8.0 to 18.0 | [EST] Time to read a return, check policy and type a decision without an agent. |
| loaded_cost_per_hour | 32.0 USD/hour | 24.0 to 45.0 | [EST] Loaded desk cost, not a wage from a payroll system. |
| manual_error_rate | 0.06 fraction | 0.02 to 0.12 | [EST] Share of manual decisions that need rework or a goodwill payment. |
| agent_error_rate | 0.02 fraction | 0.005 to 0.06 | [EST] Residual errors after the review policy. Not a measured model score. |
| cost_of_error | 25.0 USD/error | 10.0 to 60.0 | [EST] Average cost of one bad refund decision, goodwill plus rework. |
| input_tokens | 1800.0 tokens | 800.0 to 4000.0 | [EST] Prompt size for one case file. Not a trace from a provider. |
| output_tokens | 400.0 tokens | 150.0 to 1200.0 | [EST] Draft length. Not a measured completion. |
| input_price_per_million | 1.5 USD/1M tokens | 0.5 to 5.0 | [EST] Illustrative blended price. Not copied from a vendor price page. |
| output_price_per_million | 6.0 USD/1M tokens | 2.0 to 15.0 | [EST] Illustrative blended price. Not copied from a vendor price page. |
| review_minutes | 5.0 minutes | 2.0 to 10.0 | [EST] Time a person spends when a case is routed to review. |
| review_rate | 0.5 fraction | 0.15 to 0.9 | [EST] Share of cases a person still opens. The rest are not auto-approved by this model. |
| implementation_cost | 180000.0 USD | 80000.0 to 300000.0 | [EST] One-time build, integration and change-management sketch. Not a quote. |
| monthly_run_cost | 2500.0 USD/month | 800.0 to 6000.0 | [EST] Fixed monthly platform and on-call cost. Charged in full during the ramp. |
| adoption_ramp_months | 6.0 months | 2.0 to 14.0 | [EST] Months until the desk uses the agent on every case. |
| discount_rate_annual | 0.1 fraction | 0.05 to 0.18 | [EST] Annual discount rate for a 3-year NPV. Not a treasury rate. |

## Measured-cost slot

Measured per-run cost slot: plug a figure from agent-runtime-evals (private) only through a file with status measured. Stub numbers are not vendor prices and are not applied unless that status is set.
Applied in this run: no.

Replace tokens times price with a measured per-run cost from agent-runtime-evals only when the file status is measured. Stub numbers are not vendor prices.

## Commentary

Planning sketch only. The report stays on disk. Prompt refund-commentary did not approve an external action.
