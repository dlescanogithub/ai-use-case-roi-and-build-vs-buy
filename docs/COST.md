# Cost

Two different costs show up in conversation. The first is the cost of running this repository. The second is the simulated cost inside a worked example. They are separate tables so a fictional seat price is not read as an invoice for the tool.

Running the default path does not call a paid API. The token prices inside the ROI assumption files are [EST] illustrations. They are not copied from a vendor price page. Do not quote them as list prices.

## Running the tools (measured)

| Scenario | Model / provider | Tokens or units | Cost / run | p50 / p95 latency | Quality | Price date / source |
| --- | --- | --- | --- | --- | --- | --- |
| Publish both ROI sample cases, 2000 Monte Carlo draws, seed 42 | none (template provider, local CPU) | 0 tokens sent | USD 0 | 0.751 s for the whole command. One sample, so p50 and p95 are not a distribution | n/a, it is arithmetic | Measured 2026-10-17, Python 3.12.3, package 0.2.0, command `ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python3 -m roi_and_build_vs_buy roi publish-docs` |
| `decide report` on Bruma Freight | None. No model and no vendor HTTP call | 0 tokens. One local process | 0 USD | p50 0.152 s / p95 0.158 s | Decision eval 2/2 cases passed; both forced regressions exited 1 | 2026-10-17, package 0.2.0, Python 3.12.3. Latency: 30 sequential runs of `python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out /tmp/lat-N.md`, percentile index `round(p/100*(n-1))` (indexes 14 and 28) |
| Both eval gates | cassette + template/fake, no network | 0 | USD 0 (caps are 0; cassette cost fields are 0) | not separately timed | invariants passed, exit 0 | Measured 2026-10-17, `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit` |

## Inside the worked examples (simulated, [EST])

| Scenario | Model / provider | Tokens or units | Cost / run | p50 / p95 latency | Quality | Price date / source |
| --- | --- | --- | --- | --- | --- | --- |
| Refund desk, illustrative agent run | not a named vendor | 1800 input + 400 output [EST] | USD 0.0051 per item, simulated from [EST] prices of USD 1.5 and USD 6 per million | not measured; this repo does not call a model | not measured | [EST] 2026-10-17, `assumptions/refund_desk.yaml` |
| Weekly report, illustrative agent run | not a named vendor | 8000 input + 2500 output [EST] | USD 0.027 per item, simulated | not measured | not measured | [EST] 2026-10-17, `assumptions/weekly_report.yaml` |
| Bruma Freight build, year-1 model run cost | Fictional price, not a named vendor model | 24,000 runs × 2,500 tokens | 0.01 USD per run (240.00 USD in year 1) | Not measured. The agent is not executed | Not measured. Scores are human inputs | 2026-10-17, `examples/bruma_freight/tco.yaml`, [EST], simulated |
| Bruma Freight Vendor A license | Vendor A, fictional product Harborline Desk | 12 seats | 4,200 USD per seat per year, simulated, before the 8% increase assumption | Not measured | Not measured | 2026-10-17, same file, [EST], simulated |
| Bruma Freight Vendor B license | Vendor B, fictional product Quayloop | 12 seats | 1,500 USD per seat per year, simulated, before the 12% increase assumption | Not measured | Not measured | 2026-10-17, same file, [EST], simulated |
| Cedro Records build, year-1 model run cost | Fictional price | 8,000 runs × 4,000 tokens | 0.008 USD per run (64.00 USD in year 1) at 0.002 USD / 1k tokens | Not measured | Not measured | 2026-10-17, `examples/cedro_records/tco.yaml`, [EST], simulated |

Full year-by-year curves are in [examples/bruma-freight-report.md](examples/bruma-freight-report.md) and [examples/cedro-records-report.md](examples/cedro-records-report.md).

The USD 0.0051 figure is tokens times the illustrative prices in the YAML. It is [EST]. It is not a measured bill and not a list price.

## A measured bill that is not a case input

| Scenario | Model / provider | Tokens or units | Cost / run | p50 / p95 latency | Quality | Price date / source |
| --- | --- | --- | --- | --- | --- | --- |
| 23-case eval run, non-reasoning | xAI, sample recorded in agent-runtime-evals | about 66–70k input / 3–3.4k output | US$0.036–0.037 for the whole 23-case run | not measured here | not measured here | Measured 2026-10-17, commit `c1efdfd`. Not a per-refund cost |
| 23-case eval run, grok-4.3 | xAI, same sample | 62.7k input / 14.5k output, including about 11.6k reasoning | US$0.072 for the whole 23-case run | not measured here | not measured here | Measured 2026-10-17, commit `c1efdfd`. Not a per-refund cost |

The two xAI rows are measured bills for one 23-case eval run. Source: `agent-runtime-evals` commit `c1efdfd`, 2026-10-17. List prices were read the same day from `https://docs.x.ai/docs/models` (short context, under 200k prompt tokens: US$1.25 input and US$2.50 output per million for grok-4.3 and for grok-4.20-0309-non-reasoning). Those list prices times the token counts do not equal the billed totals, so the measured figure is the bill. Record: `assumptions/measured_eval_run_cost.yaml`.

[EST] conversion, not applied to either case: `per_production_item_usd = billed_eval_run_usd / 23`. That assumes one production refund costs the same as one eval case. The dollars and the 23 are measured. The equality is not.

The stub file `assumptions/measured_per_run_cost.stub.yaml` is not applied. `--measured-cost` refuses the eval-run file.

`ROI_ENABLE_REAL_PROVIDER` and `DECIDE_REAL_PROVIDER` default to 0 and are unused in CI. The ROI flag has no HTTP client. The decision HTTP adapter was not called during the measurements above, so this repo does not publish a per-call price for it.

CI does not download model weights and does not use a secret.
