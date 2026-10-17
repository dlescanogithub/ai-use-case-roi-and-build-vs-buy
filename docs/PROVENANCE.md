# Provenance

## Shared portfolio utilities

One copy of each shared utility lives in this repository. The same files are maintained in parallel in other portfolio repositories and kept aligned. Nothing here is copied from employer or client work.

The shared pieces are:

- A cassette provider that replays a recorded file and does not call a network on the default path.
- Invariant checks. The ROI gate restates the savings identity. The decision-kit gate checks weights, the approved winner, cash direction, a zero cost cap, and the absence of an external action.
- A JSONL trace, one object per line (`src/roi_and_build_vs_buy/evalkit/trace.py`).
- Structured JSON logging (`src/roi_and_build_vs_buy/logging_setup.py`).
- Bounded retries (`src/roi_and_build_vs_buy/retry.py`).
- `src/roi_and_build_vs_buy/secretscan.py`, a vendored secret scanner.

`secretscan.py` is a vendored copy. Keep that file byte-identical across the repositories that share it. Recompute the digest with `make secretscan-hash`. The test `test_documented_sha256_matches_the_scanner_file` fails if this document and the file disagree, and this document must contain that digest as its only 64-character hex string.

sha256 of `src/roi_and_build_vs_buy/secretscan.py`:

`8e57bb9f0ad8f9d2a33baa9aa35ca062dee7f456aa4bb445c21b799db0d93136`

Patterns in that file are prefix shapes, including `xai-`, `sk-` (which also matches `sk-proj-`), `sk-ant-`, `sk_`, `ghp_`, `github_pat_`, `AKIA`, a `Bearer` token, and private-key headers. The list is a set of string shapes. It is not a customer list and it is not an audience.

## What this repository contains

Two modules share the assumption tag in `src/roi_and_build_vs_buy/assumptions.py`. An invented number is `[EST]`. A number that is not an estimate names a source and a date.

The ROI module (`src/roi_and_build_vs_buy/roi/`) is the monthly payback model: ranges, tornado, scenarios, Monte Carlo, CSV and formula XLSX. The decision-kit module (`src/roi_and_build_vs_buy/build_vs_buy/`) is the weighted matrix, the weight-stability search, and the three-year TCO. The dated quantity envelope used by the decision kit is the shared shape for a single sourced number. The ROI file adds a low/high range around the same `[EST]` tag.

The measured 23-case eval bill stays in `assumptions/measured_eval_run_cost.yaml`. It is not an input of either module. Splitting it by 23 is `[EST]`.

## Where the decision kit came from

The decision-kit module was brought in from commit `8763d93` of the build-vs-buy decision kit, package 0.1.1. The separate relation note was removed because the two modules now live here.
