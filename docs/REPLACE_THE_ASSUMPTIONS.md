# Replace the assumptions

Illustrative numbers, replace with your own.

Every number in `assumptions/refund_desk.yaml` and `assumptions/weekly_report.yaml` is invented. Each parameter has `illustrative: true` and an `[EST]` rationale. The CSV export and the XLSX Inputs sheet repeat that with an `illustrative` column. The one-pagers repeat it in a table. None of those values is a measurement of a real desk.

The only measured money in this repository is the 23-case eval bill in `assumptions/measured_eval_run_cost.yaml`. That bill is not an input of either case. See the last section.

## Which file to edit

1. Copy the case you are adapting. Do not type a real client name into this portfolio repository.
2. Keep `fictional: true` until the file lives in a private place that is allowed to name the client.
3. Change one parameter at a time. This loader requires `illustrative: true` and an `[EST]` tag in the rationale, so leave both in place.
4. When the client has measured a number, put that value in `value`, narrow `low` and `high` to the range they will defend, and rewrite the rationale with the source and the date. Keep `[EST]` on any part that is still a guess. A fully measured input belongs in a note that names the command and the date; the sample files in this repo are not that note.
5. Scenario overrides are illustrative too. Update `pessimistic`, `base` and `optimistic` so they stay inside `low` and `high`.

Discovery questions for each input are in `docs/DISCOVERY.md`. The map below says where the answer comes from.

| Input | What to ask the client | Where the answer usually sits |
| --- | --- | --- |
| `volume_per_day` or `volume_per_month` | How many items arrived, per day or per month, over the last few months? | Ticket or order export, not a planning slide |
| `working_days_per_month` | Which days does this desk actually work? | The team's calendar |
| `manual_minutes_per_item` | How many minutes of touch time does one item take today, excluding wait time you would not save? | A time study or a sample of timestamps |
| `loaded_cost_per_hour` | What does one hour of that role cost fully loaded? | Finance, not the base wage alone |
| `manual_error_rate` | What share of current items is wrong enough to rework or refund? | Quality sample or rework queue |
| `agent_error_rate` | What residual error rate will you still accept after review? | A labeled pilot sample. If you have no sample, it stays `[EST]` |
| `cost_of_error` | What does one of those errors cost in money, including goodwill and rework? | Finance plus the process owner |
| `input_tokens`, `output_tokens` | What does one real run consume? | A provider usage export for one item, not a 23-case eval total |
| `input_price_per_million`, `output_price_per_million` | Which price will you actually pay? | The contract or the invoice. A public price page is a list price, not a measurement of your run |
| `review_minutes`, `review_rate` | What fraction of items does a person still open, and for how many minutes? | The review policy, then a week of observation |
| `implementation_cost` | What is the one-time cost to put this in, including change management? | A quote or an internal estimate. An estimate stays `[EST]` |
| `monthly_run_cost` | What fixed cost continues every month after launch? | Platform invoice plus on-call. It does not scale down during the ramp in this model |
| `adoption_ramp_months` | How many months until the desk uses it on every item? | The rollout plan |
| `discount_rate_annual` | What annual rate does finance use? | Finance. Horizon stays in `horizon_months` (36 in the samples) |

## How to rerun

From the repository root, after the YAML change:

```bash
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 python -m roi_model.cli publish-docs
```

That rewrites `docs/ONE_PAGER_EN.md`, `docs/ONE_PAGER_ES.md`, the weekly one-pagers, and `docs/results/`. Read the diff before you commit it. A shorter check of one case is:

```bash
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python -m roi_model.cli run --case assumptions/refund_desk.yaml
```

Outputs of that command are simulated. They are the arithmetic of the file you just edited. They are not a measured saving.

Then run the checks:

```bash
python -m ruff check . && python -m ruff format --check .
python -m mypy
python -m pytest
ROI_ENABLE_REAL_PROVIDER=0 python -m roi_model.evalkit
ROI_ENABLE_REAL_PROVIDER=0 python -m roi_model.evalkit.regression
```

The regression command must exit non-zero. That is the forced failure.

## Do not paste the eval bill into the case

`assumptions/measured_eval_run_cost.yaml` records a measured xAI bill for a 23-case eval run on 2026-10-17 (source repository `agent-runtime-evals`, commit `c1efdfd`). Passing that file to `--measured-cost` is refused.

If you want a per-item agent cost from that bill, the conversion is an assumption:

`[EST] per_production_item_usd = billed_eval_run_usd / 23`

That assumes one production item costs the same as one eval case. Write that assumption down if you use it. Build a separate override file with `status: measured` only when `agent_cost_per_run` itself was measured for one production item, with a command and a date. A price-page reconstruction is not that measurement: short-context list prices on `https://docs.x.ai/docs/models` (fetched 2026-10-17) times the sample token counts do not equal the billed totals.
