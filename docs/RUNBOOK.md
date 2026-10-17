# Runbook

This is how to operate the calculator. There is no production service, no process to restart, and no dashboard to watch.

## Roles

| Role | Owns |
| --- | --- |
| Decision owner | Accepting or rejecting a build-vs-buy ADR. The tool leaves status at `proposed` |
| YAML owner | ROI parameters, weights, scores, rationales, and TCO envelopes, including source and date |
| Finance | The discount rate, and any figure that claims to be a real price |
| Process owner | Review rate, error cost, seats, and exit |
| Reviewer | The golden-file diff, the regenerated one-pagers, and the CI result |

One person can hold more than one role on a side project. The roles stay separate so a weight change and the approval are not the same gesture.

## Operate

1. Work from a git branch. Do not edit the default branch in place.
2. Change invented numbers only in the case YAML. Keep `[EST]` while a number is still a guess. Field-by-field steps are in [REPLACE_THE_ASSUMPTIONS.md](REPLACE_THE_ASSUMPTIONS.md).
3. Regenerate, from the repo root:

```bash
python3 -m roi_and_build_vs_buy decide report \
  --case examples/bruma_freight \
  --out docs/examples/bruma-freight-report.md \
  --adr-id 0002 \
  --adr-out docs/adr/bvb-0002-bruma-freight-support-agent.md

ROI_ENABLE_REAL_PROVIDER=0 ROI_PROVIDER=template ROI_MC_DRAWS=2000 ROI_SEED=42 \
  python3 -m roi_and_build_vs_buy roi publish-docs
```

4. Read the winner, the section "Where the matrix and the cash model meet", and the diff of `docs/ONE_PAGER_EN.md` before you commit.
5. If the decision winner changed, `evalkit` fails until `evals/golden/decisions.json` is updated in the same change, with a note in the ADR. That update is a decision, not a chore.
6. The file `assumptions/measured_eval_run_cost.yaml` is a 23-case eval bill. Do not pass it to `--measured-cost`. A per-item override is a different file:

```yaml
status: measured
agent_cost_per_run: 0.01
source: "name the command, the date, and the repo. Do not call it a vendor price."
```

Then `python3 -m roi_and_build_vs_buy roi run --measured-cost path/to/file.yaml`. A `status: stub` file is refused. The eval-run file is refused.

## Version assumptions

The YAML is versioned by git. A change to a number is a commit that says which field moved and why. Do not keep a second "true" copy in a slide.

## Review

A person other than the editor should look at the diff when the number will be shown to someone else. The tools do not record that approval. Say it in the commit message or the pull request. There is no approve button.

## Monitor

There is no daemon. The signals you have are local:

- `python3 -m pytest` still passes, coverage at least 80%.
- `ROI_ENABLE_REAL_PROVIDER=0 DECIDE_REAL_PROVIDER=0 python3 -m roi_and_build_vs_buy.evalkit` still exits 0.
- `python3 -m roi_and_build_vs_buy.evalkit.roi_regression` still exits non-zero. If it starts exiting 0, the gate can no longer see a bad formula. Treat that as an incident.
- `python3 -m roi_and_build_vs_buy.evalkit.decide_regression` still exits non-zero. If it starts exiting 0, the mis-weighted Bruma fixture no longer flips the winner.
- `python3 -m roi_and_build_vs_buy.secretscan .` still prints `{"ok": true, "findings": 0}`.

JSON logs on stderr include the winner for a decision report. They do not include API keys. A validation error exits 2.

## Incidents

| Situation | What to do |
| --- | --- |
| A one-pager or report was shared and a number was wrong because the YAML was wrong | Correct the YAML, regenerate, and say in the commit that the previous figure was withdrawn |
| A simulated NPV or a TCO total was described as money a company saved or will spend | Correct the description. Point at the `[EST]` tag and the command |
| `roi_regression` exits 0 | Stop. The wrong formula is no longer failing the identity check. Fix the gate before changing the model |
| `decide_regression` exits 0 | The mis-weighted fixture no longer flips Bruma Freight. Fix the fixture or the checker before merging |
| `evalkit` fails `golden_winner` | Scores or weights no longer match the approved winner. Restore the inputs or change the golden file in a reviewed diff |
| Exit 2, bare number or weights that do not sum to 1 | Put the envelope or the weights back. Do not patch the Markdown by hand |
| A secret shows up in the scan | Remove it, rotate it outside this repo, and do not commit the value to test the scanner |
| Someone set `ROI_ENABLE_REAL_PROVIDER=1` | Nothing is spent: there is no HTTP client. Turn the flag back to 0 |
| Someone set `DECIDE_REAL_PROVIDER=1` in CI | The eval path still uses the cassette. Turn the flag back to 0. Do not point CI at a quote feed |
| Report and ADR disagree with the YAML | Regenerate. `test_committed_reports_match_the_cli` fails if the committed copies drift |

## Rollback

`git revert` the commit that changed the assumptions or the formula. Regenerate the one-pagers, the report, and the ADR so the files match the reverted code. There is no database migration and no feature flag. If a bad report was already sent to someone, send the regenerated file and say which git revision it came from.

## Handoff

| Piece | Role |
| --- | --- |
| Formula and tests | Whoever maintains this repository |
| Assumption file for a real case | The person who will defend the number. Not this repo |
| Discount rate | Finance, when a real case exists |
| Review rate, error cost, seats, exit | Process owner |
| Merging a regenerated report | The reviewer on the pull request |

Handoff is the git history plus this runbook and [HOW_IT_WORKS.md](HOW_IT_WORKS.md). There is no on-call rotation.

## What this runbook does not cover

Paging, a status page, customer communication, or rolling back a model that was never deployed.
