# Architecture

The package is a pure function from an assumption file to a result, plus writers.

## Pieces

| Module | Role |
| --- | --- |
| `assumptions.py` | YAML load, validation, measured-cost override. File reads retry with a capped backoff |
| `model.py` | Unit economics, adoption, cash flows, payback, NPV, break-even |
| `sensitivity.py` | One-at-a-time tornado and pessimistic / base / optimistic |
| `montecarlo.py` | Seeded triangular and PERT draws, percentiles, Spearman drivers |
| `svgchart.py` | Inline SVG. No PNG |
| `export_tabular.py` | CSV values and an XLSX whose outputs are Excel formulas |
| `report.py` | Markdown, HTML, EN/ES one-pagers |
| `publish.py` / `cli.py` | Write a bundle. Settings come from the environment |
| `evalkit/` | Invariants, cassette, fake provider, disabled real provider, forced regression |
| `trace.py` | JSONL |
| `logging_setup.py` | JSON logs on stderr |
| `secretscan.py` | Pattern scan for CI |

## Flow

1. `load_case` checks schema version 1, `fictional: true`, the parameter set (daily or monthly), and each scenario.
2. `build_result` is the only place that turns assumptions into NPV. The CLI does not pass `savings_override`. The regression command does, on purpose.
3. Tornado and Monte Carlo call `build_result` again. A measured per-run override is held fixed, so token-price swings go to zero when it is set.
4. Writers do not open sockets. The template provider returns a fixed sentence. The cassette provider replays `evals/cassettes/commentary.json` and errors if the id is missing.
5. The eval gate re-derives quality-adjusted savings from the inputs. It does not call `unit_economics`. That is why a wrong override fails.

## Boundaries

- No database.
- No background worker.
- No network on the default path.
- Configuration: environment variables listed in `.env.example`. Assumption files are data, not configuration.
- Logging: one JSON object per line.

## Formula map

See `src/roi_model/model.py` and ADR 0002 and ADR 0003. The spreadsheet mirrors the same definitions with named ranges. CI checks that formula cells start with `=`. It does not calculate them.

## What is intentionally missing

Live connectors and a dashboard. They are named in `docs/SCOPE.md` so they are not mistaken for features.
