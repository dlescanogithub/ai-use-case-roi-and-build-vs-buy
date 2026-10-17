# Changelog

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
