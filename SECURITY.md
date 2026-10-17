# Security

This repository is a local calculator. The default path does not call a network and does not take an external action.

## Reporting

If you find a secret, a dependency issue, or a way the tool writes outside the output directory you asked for, open a private security advisory on this private repository. Do not open a public issue and do not include keys, traces from a real client, or personal data.

## Secrets

- Configuration is environment variables. `.env.example` has empty placeholders.
- Do not commit `.env`.
- CI runs `python -m roi_model.secretscan`.
- The real-provider flag defaults to off. This repo does not ship a vendor HTTP client, so the flag cannot spend money.

## Data

Cases are fictional. Do not paste client data, employer names, or production figures into assumption files that you commit.

## What this file does not promise

There is no production deployment, no authentication layer, and no claim that the model is safe to use as an automatic approval for refunds or spend.
