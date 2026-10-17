Illustrative numbers, replace with your own

# Weekly report automation

Generated 2026-10-17T15:43:07.257642+00:00 by `python -m roi_model.cli publish-docs` (package 0.1.0, git 3a4cb87).
Simulated. Every input is illustrative [EST]. This page is not a measured business result.

Personal example only. Four reports a month, written by hand today. You still read every draft. The hourly rate is what you assume your time is worth. It is not a salary and not an employer figure.

| Input | Value | Label |
| --- | --- | --- |
| volume_per_month | 4.0 items/month | illustrative [EST] |
| manual_minutes_per_item | 90.0 minutes | illustrative [EST] |
| loaded_cost_per_hour | 40.0 USD/hour | illustrative [EST] |
| manual_error_rate | 0.05 fraction | illustrative [EST] |
| agent_error_rate | 0.02 fraction | illustrative [EST] |
| cost_of_error | 20.0 USD/error | illustrative [EST] |
| input_tokens | 8000.0 tokens | illustrative [EST] |
| output_tokens | 2500.0 tokens | illustrative [EST] |
| input_price_per_million | 1.5 USD/1M tokens | illustrative [EST] |
| output_price_per_million | 6.0 USD/1M tokens | illustrative [EST] |
| review_minutes | 20.0 minutes | illustrative [EST] |
| review_rate | 1.0 fraction | illustrative [EST] |
| implementation_cost | 300.0 USD | illustrative [EST] |
| monthly_run_cost | 20.0 USD/month | illustrative [EST] |
| adoption_ramp_months | 1.0 months | illustrative [EST] |
| discount_rate_annual | 0.08 fraction | illustrative [EST] |

## What the model says

- Steady-state net monthly savings: USD 168.96.
- Payback: 1.78 months.
- Break-even volume: 0.42 items/month. steady-state monthly volume where net monthly savings are zero.
- 3-year NPV: USD 5,114.00.
- Cost per completed item, including reviewer time: USD 13.36.
- Quality-adjusted savings per item (after residual errors): USD 47.24.
- Assumptions that move NPV the most: loaded_cost_per_hour, volume_per_month, manual_minutes_per_item.

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
