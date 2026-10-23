# Replace the assumptions

Illustrative numbers, replace with your own.

This repository has two assumption shapes that share the `[EST]` tag in `src/roi_and_build_vs_buy/assumptions.py`. They are not one YAML schema. Edit the file that matches the question you are answering.

- ROI cases: `assumptions/refund_desk.yaml` and `assumptions/weekly_report.yaml`. Each parameter has `illustrative: true`, a low/high range, and an `[EST]` rationale.
- Decision cases: `examples/bruma_freight/` and `examples/cedro_records/`. Weights, scores, and TCO quantities. Every committed cell is an estimate.

The organisations are fictional. None of those numbers is a measurement of a running desk.

The only measured money in this repository is the 23-case eval bill in `assumptions/measured_eval_run_cost.yaml`. That bill is not an input of either module. See the last section.

Winner stability is calculated from the decision inputs. On the committed Bruma Freight scores it is 67.86% (19 of 28). Change a score or a weight and that percentage changes.

## ROI inputs

1. Copy the case you are adapting. Do not type a real client name into this repository.
2. Keep `fictional: true` until the file lives in a private place that is allowed to name the client.
3. Change one parameter at a time. This loader requires `illustrative: true` and an `[EST]` tag in the rationale, so leave both in place.
4. When a number has been measured, put that value in `value`, narrow `low` and `high` to the range they will defend, and rewrite the rationale with the source and the date. Keep `[EST]` on any part that is still a guess.
5. Scenario overrides are illustrative too. Update `pessimistic`, `base` and `optimistic` so they stay inside `low` and `high`.

| Input | What to ask | Where the answer usually sits |
| --- | --- | --- |
| `volume_per_day` or `volume_per_month` | How many items arrived over the last few months? | Ticket or order export, not a planning slide |
| `working_days_per_month` | Which days does this desk actually work? | The team's calendar |
| `manual_minutes_per_item` | How many minutes of touch time does one item take, excluding wait you would not save? | A time study |
| `loaded_cost_per_hour` | What does one hour of that role cost fully loaded? | Finance |
| `manual_error_rate` | What share of current items is wrong enough to rework? | Quality sample |
| `agent_error_rate` | What residual error rate will you still accept after review? | A labeled pilot sample. If you have none, it stays `[EST]` |
| `cost_of_error` | What does one of those errors cost? | Finance plus the process owner |
| `input_tokens`, `output_tokens` | What does one real run consume? | A usage export for one item, not a 23-case eval total |
| `input_price_per_million`, `output_price_per_million` | Which price will you actually pay? | The contract or the invoice. A public price page is a list price, not a measurement of your run |
| `review_minutes`, `review_rate` | What fraction of items does a person still open, and for how many minutes? | The review policy, then a week of observation |
| `implementation_cost` | What is the one-time cost to put this in? | A quote or an internal estimate. An estimate stays `[EST]` |
| `monthly_run_cost` | What fixed cost continues every month? | Platform invoice plus on-call |
| `adoption_ramp_months` | How many months until the desk uses it on every item? | The rollout plan |
| `discount_rate_annual` | What annual rate does finance use? | Finance |

## Decision inputs

### Weights (`weights.yaml`)

Eight weights that must sum to 1: `control`, `time_to_value`, `tco_3y`, `vendor_risk`, `security_compliance`, `maintainability`, `extensibility`, `exit_cost`. Each weight is a judgment. The file marks them illustrative.

### Scores (`scores.yaml`)

Every cell, for every option: an integer from 1 to 5 (higher is better, including cost and risk), a rationale, and `estimate: true` until you have a source you will stand behind.

### Cash drivers (`tco.yaml`)

Every quantity is an envelope: `value`, `unit`, `source`, `date`, `estimate`. Replace build hours and rate, infrastructure, runs, tokens, eval and review hours, maintenance percent, volume growth, seats, license, usage tiers, integration hours, annual price increase, and exit cost.

If a number comes from an official public price page, set `estimate: false`, put the `https://` URL in `source`, and the access date in `date`. The loader rejects a bare number and rejects a USD amount that claims to be real without that URL. The examples do not use any official public price. Leave `estimate: true` and the `[EST]` marker until you have one.

Keep `fictional: true` on exercises in this repository. A real engagement follows [ADAPT_TO_A_REAL_CLIENT.md](ADAPT_TO_A_REAL_CLIENT.md).

Discovery questions for both modules are in [DISCOVERY.md](DISCOVERY.md).

## How to rerun

From the repository root:

```bash
python3 -m roi_and_build_vs_buy decide report --case examples/bruma_freight --out out/bruma-freight-report.md
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 \
  python3 -m roi_and_build_vs_buy roi publish-docs
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template \
  python3 -m roi_and_build_vs_buy roi run --case assumptions/refund_desk.yaml
```

Outputs of the ROI commands are simulated. They are the arithmetic of the file you just edited.

Then run the checks:

```bash
python3 -m ruff check . && python3 -m ruff format --check .
python3 -m mypy
python3 -m pytest
ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit
ROI_ENABLE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.roi_regression
DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit.decide_regression
```

Both regression commands must exit non-zero. `decide_regression` loads a copy of the Bruma Freight scores and cash with the weights changed on purpose. That is the regression fixture, not your new case.

`python3 -m roi_and_build_vs_buy.evalkit` checks that the calculator still returns the winner stored in `evals/golden/decisions.json`, and that winner stability stays at or above the floor stored next to it. It does not score an assistant. If your new scores change the winner, updating the golden file is a decision. Record it in the ADR.

## Do not paste the eval bill into the case

`assumptions/measured_eval_run_cost.yaml` records a measured xAI bill for a 23-case eval run on 2026-10-17 (source repository `agent-runtime-evals`, commit `c1efdfd`). Passing that file to `--measured-cost` is refused.

If you want a per-item agent cost from that bill, the conversion is an assumption:

`[EST] per_production_item_usd = billed_eval_run_usd / 23`

That assumes one production item costs the same as one eval case. Write that assumption down if you use it. Build a separate override file with `status: measured` only when `agent_cost_per_run` itself was measured for one production item, with a command and a date. A price-page reconstruction is not that measurement: short-context list prices on `https://docs.x.ai/docs/models` (fetched 2026-10-17) times the sample token counts do not equal the billed totals.
