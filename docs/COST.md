# Cost

Running this repository does not call a paid API. The token prices inside the assumption files are [EST] illustrations. They are not copied from a vendor price page. Do not quote them as list prices.

| Scenario | Model / provider | Tokens or units | Cost / run | p50 / p95 latency | Quality | Price date / source |
| --- | --- | --- | --- | --- | --- | --- |
| Publish both sample cases, 2000 Monte Carlo draws, seed 42 | none (template provider, local CPU) | 0 tokens sent | USD 0 | 0.703 s for the whole command. One sample, so p50 and p95 are not a distribution | n/a, it is arithmetic | Measured 2026-10-17, Python 3.12.3, package 0.1.0, command `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python -m roi_model.cli publish-docs` |
| Eval gate | cassette + fake, no network | 0 | USD 0 (cap is 0; the cassette cost field is 0) | not separately timed | invariants passed | Measured 2026-10-17, `python -m roi_model.evalkit`, exit 0 |
| Refund desk, illustrative agent run | not a named vendor | 1800 input + 400 output [EST] | USD 0.0051 per item, simulated from [EST] prices of USD 1.5 and USD 6 per million | not measured; this repo does not call a model | not measured | [EST] 2026-10-17, `assumptions/refund_desk.yaml`. Not a price page |
| Weekly report, illustrative agent run | not a named vendor | 8000 input + 2500 output [EST] | USD 0.027 per item, simulated | not measured | not measured | [EST] 2026-10-17, `assumptions/weekly_report.yaml`. Not a price page |
| Real provider | not shipped | none | cannot spend | n/a | n/a | The flag exists and defaults off. There is no HTTP client |

The USD 0.0051 figure is tokens times the illustrative prices in the YAML. It is not a measured bill and not a list price. A measured per-run cost from another private repo can be passed later with `--measured-cost`. The stub file `assumptions/measured_per_run_cost.stub.yaml` is not applied.

CI does not download model weights and does not use a secret.
