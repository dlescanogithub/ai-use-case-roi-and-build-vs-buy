# Changelog

## Unreleased

- Secret scan matches the shared portfolio key shapes. `src/roi_model/secretscan.py` is the vendored copy; `docs/PROVENANCE.md` records its sha256.
- Provenance and NOTICE rewritten in publishable language. Shared utilities are named as cassette replay, invariant checks, JSON trace, structured logging and the secret scanner.
- Every case input carries `illustrative: true` and an `[EST]` rationale. README and one-pagers open with "Illustrative numbers, replace with your own". Added `docs/REPLACE_THE_ASSUMPTIONS.md`.
- Recorded the 2026-10-17 `agent-runtime-evals` 23-case bills (commit `c1efdfd`) separately from the invented inputs. The per-item split is `[EST]` and is not applied.
- Added `docs/RELATION_TO_BUILD_VS_BUY.md`. Neither repository was merged or deleted.

## 0.1.0 - 2026-10-17

- Initial portfolio model: monthly ROI, payback, break-even, 3-year NPV, tornado, scenarios, seeded Monte Carlo, CSV and formula XLSX, Markdown/HTML reports, EN/ES one-pagers.
- Invariant eval gate and a forced-regression check that is supposed to fail.
- All case numbers are assumptions tagged [EST], except outputs of a local run, which are simulated and labeled with the command that produced them.

This version has not been tagged or released.
