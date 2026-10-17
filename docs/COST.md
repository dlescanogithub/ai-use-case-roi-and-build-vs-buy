# Cost

Running this repository does not call a paid API. The token prices inside the assumption files are [EST] illustrations. They are not copied from a vendor price page. Do not quote them as list prices.

| Scenario | Model / provider | Tokens or units | Cost / run | p50 / p95 latency | Quality | Price date / source |
| --- | --- | --- | --- | --- | --- | --- |
| Publish both sample cases, 2000 Monte Carlo draws, seed 42 | none (template provider, local CPU) | 0 tokens sent | USD 0 | 0.728 s for the whole command. One sample, so p50 and p95 are not a distribution | n/a, it is arithmetic | Measured 2026-10-17, Python 3.12.3, package 0.1.0, command `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_model.cli publish-docs` |
| Eval gate | cassette + fake, no network | 0 | USD 0 (cap is 0; the cassette cost field is 0) | not separately timed | invariants passed | Measured 2026-10-17, `python -m roi_model.evalkit`, exit 0 |
| Refund desk, illustrative agent run | not a named vendor | 1800 input + 400 output [EST] | USD 0.0051 per item, simulated from [EST] prices of USD 1.5 and USD 6 per million | not measured; this repo does not call a model | not measured | [EST] 2026-10-17, `assumptions/refund_desk.yaml`. Not a price page |
| Weekly report, illustrative agent run | not a named vendor | 8000 input + 2500 output [EST] | USD 0.027 per item, simulated | not measured | not measured | [EST] 2026-10-17, `assumptions/weekly_report.yaml`. Not a price page |
| 23-case eval run, non-reasoning | xAI, sample recorded in agent-runtime-evals | about 66–70k input / 3–3.4k output | US$0.036–0.037 for the whole 23-case run | not measured here | not measured here | Measured 2026-10-17, commit `c1efdfd`. Not a per-refund cost |
| 23-case eval run, grok-4.3 | xAI, same sample | 62.7k input / 14.5k output, including about 11.6k reasoning | US$0.072 for the whole 23-case run | not measured here | not measured here | Measured 2026-10-17, commit `c1efdfd`. Not a per-refund cost |
| Real provider | not shipped | none | cannot spend | n/a | n/a | The flag exists and defaults off. There is no HTTP client |

The USD 0.0051 figure is tokens times the illustrative prices in the YAML. It is [EST]. It is not a measured bill and not a list price.

The two xAI rows are measured bills for one 23-case eval run. Source: `agent-runtime-evals` commit `c1efdfd`, 2026-10-17. List prices were read the same day from `https://docs.x.ai/docs/models` (short context, under 200k prompt tokens: US$1.25 input and US$2.50 output per million for grok-4.3 and for grok-4.20-0309-non-reasoning). Those list prices times the token counts do not equal the billed totals, so the measured figure is the bill. Record: `assumptions/measured_eval_run_cost.yaml`.

[EST] conversion, not applied to either case: `per_production_item_usd = billed_eval_run_usd / 23`. That assumes one production refund costs the same as one eval case. The dollars and the 23 are measured. The equality is not.

The stub file `assumptions/measured_per_run_cost.stub.yaml` is not applied. `--measured-cost` refuses the eval-run file.

CI does not download model weights and does not use a secret.
