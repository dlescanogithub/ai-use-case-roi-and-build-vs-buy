# Security

This repository is a local calculator with two modules. The default path does not call a network and does not take an external action.

## Reporting

If you find a secret, a dependency issue, or a way the tool writes outside the output directory you asked for, open a private security advisory on this private repository. Do not open a public issue and do not include keys, traces from a real client, or personal data.

## Secrets

- Configuration is environment variables. `.env.example` has empty placeholders for `ROI_*` and `DECIDE_*`.
- Do not commit `.env`.
- CI runs `python -m roi_and_build_vs_buy.secretscan .`. The same command is the pre-commit hook.
- `ROI_ENABLE_REAL_PROVIDER` defaults to off. This repo does not ship an ROI vendor HTTP client, so that flag cannot spend money.
- `DECIDE_REAL_PROVIDER` defaults to off. The decision eval path ignores it and uses a cassette. Tests block sockets.

## Data

Cases are fictional. Do not paste client data, employer names, or production figures into assumption files that you commit.

## Labels

Numbers in the README and in `docs/BUSINESS_VALUE.md` are tagged MEASURED, [EST], SIMULATED, or UNVERIFIED. A simulated NPV is not a saving this repository observed. Do not commit a key, a client name, an employer name, or a trace from a real desk.

## What this file does not promise

There is no deployed service, no authentication layer, and no claim that either module is safe to use as an automatic approval for refunds, spend, or a vendor contract.
