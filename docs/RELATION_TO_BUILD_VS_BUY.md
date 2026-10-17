# Relation to the build-versus-buy decision kit

This note is a proposal. Nothing was merged and nothing was deleted. `dlescanogithub/build-vs-buy-agent-decision-kit` and this repository stay separate until the owner decides otherwise.

## What overlaps

Both repositories help a person decide what to do about an agent before money is spent. They do not make the decision.

This repository is the numeric sketch: one assumption file in, then payback, break-even, 3-year NPV, tornado, scenarios and a seeded Monte Carlo. Every case input here is illustrative `[EST]` until someone replaces it. A measured 23-case eval bill is recorded beside those inputs and is not substituted into them.

The build-versus-buy kit is the qualitative decision: whether to build, buy, or wait, who would own the system, and which risks block a pilot. That question is not a cashflow. A cheap token price can still be the wrong build, and a sound build can still fail the payback.

They meet in the discovery questions. Volume, touch time, loaded cost, error cost, review load, implementation cost and the monthly run cost show up in both conversations. A person should not answer them twice in two formats that can drift.

Shared plumbing, kept aligned on purpose and maintained in parallel, is the cassette provider, the invariant checks, the JSON trace, structured logging, and the secret scanner. See `docs/PROVENANCE.md`. The ROI formulas are not part of that shared set.

## A structure if they are later combined

The owner can do this later. This change does not do it.

```text
decision-kit/                      qualitative gates, scorecard, ownership
  assumptions/                     one YAML file, still the only numeric source
  roi/                             this calculator, called as a library
  docs/                            one discovery list, one risk list
  shared/                          cassette, invariants, trace, logging, secretscan
```

What stays where:

- Qualitative gates (build, buy, wait, and who can stop a pilot) stay in the decision kit. This model still has no approve command.
- The numeric engine stays the code in this repository: `unit_economics`, payback, break-even, NPV, tornado, scenarios, Monte Carlo, CSV and formula XLSX.
- One assumption file feeds both. The decision kit reads the same YAML the calculator loads. It does not keep a second copy of the cents.
- The measured eval-run bill stays a separate file, with the `[EST]` per-item conversion written out, so a 23-case invoice is not mistaken for a production refund.
- Design-only use cases stay named and unrunnable until their parameters exist. Combining the repos does not invent those parameters.
- Reports from the calculator remain simulated outputs of the assumption file. The scorecard can cite them only with the command, the date and the `[EST]` label.

## What this change did not do

- It did not copy or delete files from `dlescanogithub/build-vs-buy-agent-decision-kit`.
- It did not add a dependency, a submodule, or a shared package release.
- It did not change the headline refund or weekly results. Those still come from the invented inputs.
