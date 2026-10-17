# Architecture

Two modules, one package, one command. `decide` scores a build-versus-buy case. `roi` turns an assumption file into a monthly result. They share the `[EST]` tag, the logger, retries, the trace, and the secret scanner. They do not share one YAML schema.

## Layout

| Path | Role |
| --- | --- |
| `src/roi_and_build_vs_buy/cli.py` | Dispatches `roi` and `decide` |
| `src/roi_and_build_vs_buy/assumptions.py` | Shared `[EST]` tag and the marker used by a decision quantity |
| `src/roi_and_build_vs_buy/roi/` | Monthly model, tornado, Monte Carlo, CSV, formula XLSX, one-pagers |
| `src/roi_and_build_vs_buy/build_vs_buy/` | Matrix, sensitivity, 3-year TCO, decision reports, ADRs |
| `src/roi_and_build_vs_buy/evalkit/` | Both gates, both forced regressions, commentary cassettes, price cassettes |
| `src/roi_and_build_vs_buy/logging_setup.py` | JSON logs. One logger name, `roi_and_build_vs_buy` |
| `src/roi_and_build_vs_buy/retry.py` | `retry` for the ROI path, `retry_call` for the decision path |
| `src/roi_and_build_vs_buy/evalkit/trace.py` | JSONL. ROI events and decision traces |
| `src/roi_and_build_vs_buy/secretscan.py` | One vendored scanner. Hash in [PROVENANCE.md](PROVENANCE.md) |

## Flow

1. `decide` loads weights, scores, and a TCO file. Weights must sum to 1. Scores are integers 1–5. Every TCO quantity is an envelope.
2. The matrix ranks options. Sensitivity shifts one weight at a time. The TCO projects three years and keeps exit cost out of the operating total.
3. The report states when the weighted winner and the cheapest operating total are different options. The ADR stays `proposed`.
4. `roi` loads a case with `fictional: true`, `illustrative: true`, and `[EST]` in each rationale.
5. `build_result` is the only place that turns ROI assumptions into NPV. The CLI does not pass `savings_override`. The ROI regression does, on purpose.
6. Tornado and Monte Carlo call `build_result` again. Writers do not open sockets.
7. `python -m roi_and_build_vs_buy.evalkit` runs the ROI gate and then the decision gate. Exit 0 only when both pass.

## Boundaries

- No database.
- No background worker.
- No network on the default path. Tests block `socket.socket.connect` and `socket.create_connection`.
- Configuration: environment variables in `.env.example`. `ROI_*` for the monthly model, `DECIDE_*` for the decision kit. Assumption files are data, not configuration.
- Logging: one JSON object per line. Fields named like secrets are dropped.

## Formula map

ROI formulas live in `src/roi_and_build_vs_buy/roi/model.py` and in ADR 0002 and ADR 0003. The spreadsheet mirrors the same definitions with named ranges. CI checks that formula cells start with `=`. It does not calculate them.

Decision cash formulas live in `src/roi_and_build_vs_buy/build_vs_buy/tco.py`. The generated reports in `docs/examples/` are compared to a fresh CLI run.

## What is intentionally missing

Live connectors, a dashboard, and a production quote feed. They are named in [SCOPE.md](SCOPE.md) so they are not mistaken for features.
