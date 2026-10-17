Illustrative numbers, replace with your own

# ROI report: Weekly report automation

- Generated: 2026-10-17T15:43:07.257642+00:00
- Command: `python -m roi_model.cli publish-docs`
- Package version: 0.1.0
- Git revision: 3a4cb87
- Data: 100% synthetic. Every input is illustrative [EST].
- Outputs: simulated.
- Company: Personal desk (fictional).

## Decision

This model does not approve an action, send a message, or spend money.
A person has to read the assumptions and decide.

## Result

| Metric | Value |
| --- | --- |
| Net monthly savings, steady state | USD 168.96 |
| Payback | 1.78 months |
| Break-even volume | 0.42 items/month (steady-state monthly volume where net monthly savings are zero) |
| 3-year NPV | USD 5,114.00 |
| Cost per completed item, with reviewer time | USD 13.36 |
| Quality-adjusted savings per item | USD 47.24 |
| Residual error cost per item | USD 0.40 |

## Unit economics [EST]

| Piece | Per item |
| --- | --- |
| Manual labor | USD 60.00 |
| Manual expected error | USD 1.00 |
| Agent run (tokens x price, or measured override) | USD 0.03 |
| Reviewer time | USD 13.33 |
| Residual error | USD 0.40 |

## Scenarios (simulated)

| Scenario | Net monthly | Payback | NPV |
| --- | --- | --- | --- |
| pessimistic | -USD 67.71 | never (steady-state net monthly savings are not positive; the case never pays back) | -USD 2,469.59 |
| base | USD 168.96 | 1.78 months | USD 5,114.00 |
| optimistic | USD 524.96 | 0.57 months | USD 16,521.42 |

## Monte Carlo (simulated)

Draws: 2000. Seed: 42.

|  | P10 | P50 | P90 |
| --- | --- | --- | --- |
| NPV | USD 1,715.69 | USD 5,415.23 | USD 11,340.30 |
| Net monthly | USD 73.54 | USD 191.11 | USD 376.52 |

## Which assumptions move the result most

Tornado (absolute swing of 3-year NPV):

| Parameter | Low NPV | High NPV | Swing (high minus low) |
| --- | --- | --- | --- |
| loaded_cost_per_hour | USD 1,375.61 | USD 11,095.42 | USD 9,719.81 |
| volume_per_month | USD 2,086.57 | USD 11,168.86 | USD 9,082.30 |
| manual_minutes_per_item | USD 1,268.80 | USD 10,240.93 | USD 8,972.13 |
| review_minutes | USD 6,395.73 | USD 1,696.04 | -USD 4,699.69 |
| monthly_run_cost | USD 5,754.87 | USD 3,191.40 | -USD 2,563.47 |
| implementation_cost | USD 5,414.00 | USD 3,414.00 | -USD 2,000.00 |
| discount_rate_annual | USD 5,513.46 | USD 4,639.48 | -USD 873.98 |
| review_rate | USD 5,968.49 | USD 5,114.00 | -USD 854.49 |

Rank correlation of each draw with NPV (Spearman):

- loaded_cost_per_hour: 0.553
- manual_minutes_per_item: 0.551
- volume_per_month: 0.494
- review_minutes: -0.191
- monthly_run_cost: -0.151
- implementation_cost: -0.089
- review_rate: -0.067
- manual_error_rate: 0.038

## Assumptions

| Parameter | Value | Label | Range | Why it is here |
| --- | --- | --- | --- | --- |
| volume_per_month | 4.0 items/month | illustrative [EST] | 2.0 to 8.0 | [EST] One report a week, counted as four a month. |
| manual_minutes_per_item | 90.0 minutes | illustrative [EST] | 45.0 to 150.0 | [EST] Time to gather numbers and write the report without an agent. |
| loaded_cost_per_hour | 40.0 USD/hour | illustrative [EST] | 15.0 to 80.0 | [EST] What you assume an hour of your own time is worth. Not a wage. |
| manual_error_rate | 0.05 fraction | illustrative [EST] | 0.01 to 0.15 | [EST] Share of hand-written reports you have to redo because a figure was wrong. |
| agent_error_rate | 0.02 fraction | illustrative [EST] | 0.005 to 0.08 | [EST] Residual mistakes you still expect after you read the draft. |
| cost_of_error | 20.0 USD/error | illustrative [EST] | 5.0 to 50.0 | [EST] Rework cost of one wrong report. Illustrative. |
| input_tokens | 8000.0 tokens | illustrative [EST] | 3000.0 to 20000.0 | [EST] Notes pasted into a prompt. Not a measured trace. |
| output_tokens | 2500.0 tokens | illustrative [EST] | 800.0 to 6000.0 | [EST] Length of a draft report. Not a measured completion. |
| input_price_per_million | 1.5 USD/1M tokens | illustrative [EST] | 0.5 to 5.0 | [EST] Illustrative blended price. Not a vendor price page. |
| output_price_per_million | 6.0 USD/1M tokens | illustrative [EST] | 2.0 to 15.0 | [EST] Illustrative blended price. Not a vendor price page. |
| review_minutes | 20.0 minutes | illustrative [EST] | 5.0 to 60.0 | [EST] You still read the draft. If this reaches 90, the labor savings disappear. |
| review_rate | 1.0 fraction | illustrative [EST] | 0.5 to 1.0 | [EST] In this personal example every report is reviewed. The low side is a sensitivity, not a policy. |
| implementation_cost | 300.0 USD | illustrative [EST] | 0.0 to 2000.0 | [EST] An evening of setup, priced at the same assumed hourly rate. Not an invoice. |
| monthly_run_cost | 20.0 USD/month | illustrative [EST] | 0.0 to 80.0 | [EST] A slice of a personal subscription. Not a real plan price. |
| adoption_ramp_months | 1.0 months | illustrative [EST] | 0.0 to 3.0 | [EST] You either use it next month or you do not. |
| discount_rate_annual | 0.08 fraction | illustrative [EST] | 0.03 to 0.15 | [EST] A personal discount rate for a 3-year sketch. Not a market rate. |

## Measured-cost slot

Measured data, separate from the invented inputs. These are bills for one 23-case eval run, not the cost of one production refund. They are not applied to the NPV on this page.

Source: agent-runtime-evals commit c1efdfd, measured 2026-10-17, provider xAI. Price page https://docs.x.ai/docs/models fetched 2026-10-17.

| Sample | Billed USD | Tokens | Label |
| --- | --- | --- | --- |
| non-reasoning | US$0.036-0.037 | about 66-70k input / 3-3.4k output tokens | measured |
| grok-4.3 | US$0.072 | 62.7k input / 14.5k output, including about 11.6k reasoning tokens | measured |

[EST] `per_production_item_usd = billed_eval_run_usd / 23`
One production refund costs the same as one case inside this 23-case eval run. The billed dollars, the token counts and the case count are measured. This equality is not. It is not applied to the invented case inputs in refund_desk.yaml or weekly_report.yaml.

[EST] non-reasoning: US$0.036-0.037 / 23 = US$0.001565 to US$0.001609 per case (display rounded to 6 decimal places).
[EST] grok-4.3: US$0.072 / 23 = US$0.003130 per case (display rounded to 6 decimal places).

Short-context list price times the token counts does not equal the billed sample. The measured figure is the billed total. The non-reasoning sample is recorded as non-reasoning; the list-price row used for that reconstruction is grok-4.20-0309-non-reasoning on the price page fetched the same day. This file does not claim a model id for that sample beyond non-reasoning.

List-price reconstruction for non-reasoning using grok-4.20-0309-non-reasoning at US$1.25 input and US$2.50 output per million tokens: US$0.09 to US$0.096. Billed sample: US$0.036-0.037. The reconstruction is not the measured bill.
List-price reconstruction for grok-4.3 using grok-4.3 at US$1.25 input and US$2.50 output per million tokens: US$0.114625. Billed sample: US$0.072. The reconstruction is not the measured bill.

Applied as the agent cost in this run: no.

[EST] Token prices in this file stay invented. The measured 23-case eval bill lives in assumptions/measured_eval_run_cost.yaml and is not a weekly report. The [EST] split of that bill by 23 is not applied here.

## Commentary

Planning sketch only. The report stays on disk. Prompt weekly-commentary did not approve an external action.
