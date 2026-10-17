# Runbook

This is how to operate the calculator. There is no production service.

## Operate

1. Work from a git branch. Do not edit `main` in place.
2. Change numbers only in `assumptions/*.yaml`. Each rationale stays tagged `[EST]` until you truly have a measurement.
3. Regenerate, from the repo root:

```bash
ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template python -m roi_model.cli publish-docs
```

4. Read the diff of `docs/ONE_PAGER_EN.md`, `docs/ONE_PAGER_ES.md` and `docs/results/*.json` before you commit it.
5. If you have a measured per-run cost, put it in a file that is not the stub:

```yaml
status: measured
agent_cost_per_run: 0.01
source: "name the command, the date, and the repo. Do not call it a vendor price."
```

Then `python -m roi_model.cli run --measured-cost path/to/file.yaml`. A `status: stub` file is refused.

## Version assumptions

The YAML is versioned by git. A change to a number is a commit with a message that says which field moved and why. Do not keep a second "true" copy in a slide.

## Review

A person other than the editor should look at the diff when the number will be shown to someone else. The model does not record that approval. Say it in the commit message or the PR. There is no approve button.

## Monitor

There is no daemon. The signals you have are local:

- `python -m pytest` still passes.
- `python -m roi_model.evalkit` still exits 0.
- `python -m roi_model.evalkit.regression` still exits non-zero. If it starts exiting 0, the gate can no longer see a bad formula. Treat that as an incident.
- `python -m roi_model.secretscan` still prints `no findings`.

## Incidents

| Situation | What to do |
| --- | --- |
| A one-pager was shared and a number was wrong because the YAML was wrong | Correct the YAML, regenerate, and say in the commit that the previous figure was withdrawn. Do not leave both numbers unlabeled |
| A simulated NPV was described as money a company saved | Correct the description. Point at the `[EST]` tag and the command. This repo cannot have saved that money |
| `eval-regression` exits 0 | Stop. The wrong formula is no longer failing the identity check. Fix the gate before changing the model |
| A secret shows up in the scan | Remove it, rotate it outside this repo, and do not commit the value "to test the scanner" |
| Someone set `ROI_ENABLE_REAL_PROVIDER=1` | Nothing is spent: there is no HTTP client. Turn the flag back to 0 anyway |

## Rollback

`git revert` the commit that changed the assumptions or the formula. Regenerate the one-pagers so the files match the reverted code. There is no database migration.

## Ownership and handoff

| Piece | Role |
| --- | --- |
| Formula and tests | Whoever maintains this repository |
| Assumption file for a real case | The person who will defend the number. Not this repo |
| Discount rate | Finance, when a real case exists |
| Review rate and error cost | Process owner |
| Merging a regenerated one-pager | The reviewer on the pull request |

Handoff is the git history plus this runbook. There is no on-call rotation.

## What this runbook does not cover

Paging, a status page, customer communication, or rolling back a model that was never deployed.
