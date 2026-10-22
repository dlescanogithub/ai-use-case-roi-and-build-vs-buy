# Changelog

## Unreleased

- Documentation only. Package version stays 0.2.0.
- README in English: Start here, Quickstart, Business value, Proof, and What this does NOT prove.
- Added `docs/BUSINESS_VALUE.md`. It restates the business case, the cost note, and the metrics. It does not add a volume or an ROI percentage.
- Pytest remeasured on 2026-10-22, Python 3.12.3, pytest 9.1.1: 80 passed, total coverage 90.98% on a clean tree. A second run with a trace file already present printed 91.02%. Both eval gates exited 0. Both forced regressions exited 1. Secret scan findings were 0. mypy 2.4.0 reported no issues in 55 source files. Publish wall time was not re-timed.

## 0.2.0 - 2026-10-17

- One package, `roi_and_build_vs_buy`, distribution name `ai-use-case-roi-and-build-vs-buy`. Subcommands: `roi` and `decide`.
- The build-versus-buy decision kit (weighted scoring, 3-year TCO, winner stability, Bruma Freight, Cedro Records, forced regression) now lives beside the monthly ROI model.
- Shared utilities are one copy each: secretscan, JSON logging, retries, JSONL trace, and the `[EST]` tag. The secretscan sha256 is in `docs/PROVENANCE.md`.
- Docs are one set. The separate relation notes were removed because the modules live in this repository.
- Both eval gates run from `python -m roi_and_build_vs_buy.evalkit`. Both forced regressions must exit non-zero, and CI asserts that.

## 0.1.0 - 2026-10-17

- Initial portfolio model: monthly ROI, payback, break-even, 3-year NPV, tornado, scenarios, seeded Monte Carlo, CSV and formula XLSX, Markdown/HTML reports, EN/ES one-pagers.
- Invariant eval gate and a forced-regression check that is supposed to fail.
- Case numbers are assumptions tagged [EST]. A measured 23-case eval bill is recorded beside those inputs and is not applied.

This version has not been tagged or released.
