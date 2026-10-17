Illustrative numbers, replace with your own

# Refund desk agent

Generated 2026-10-17T15:43:07.257642+00:00 by `python -m roi_model.cli publish-docs` (package 0.1.0, git 3a4cb87).
Simulated. Every input is illustrative [EST]. This page is not a measured business result.

Puerto Gris Parcel Co. is a fictional carrier. A back-office agent would draft refund decisions for returned parcels. A person still approves the ones the policy sends to review. None of these figures are measurements.

| Input | Value | Label |
| --- | --- | --- |
| volume_per_day | 120.0 items/day | illustrative [EST] |
| working_days_per_month | 21.0 days/month | illustrative [EST] |
| manual_minutes_per_item | 12.0 minutes | illustrative [EST] |
| loaded_cost_per_hour | 32.0 USD/hour | illustrative [EST] |
| manual_error_rate | 0.06 fraction | illustrative [EST] |
| agent_error_rate | 0.02 fraction | illustrative [EST] |
| cost_of_error | 25.0 USD/error | illustrative [EST] |
| input_tokens | 1800.0 tokens | illustrative [EST] |
| output_tokens | 400.0 tokens | illustrative [EST] |
| input_price_per_million | 1.5 USD/1M tokens | illustrative [EST] |
| output_price_per_million | 6.0 USD/1M tokens | illustrative [EST] |
| review_minutes | 5.0 minutes | illustrative [EST] |
| review_rate | 0.5 fraction | illustrative [EST] |
| implementation_cost | 180000.0 USD | illustrative [EST] |
| monthly_run_cost | 2500.0 USD/month | illustrative [EST] |
| adoption_ramp_months | 6.0 months | illustrative [EST] |
| discount_rate_annual | 0.1 fraction | illustrative [EST] |

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
