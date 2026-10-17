# Provenance

The calculator, the assumption files, the reports and the tests in this repository were written for this repository. Nothing here is copied from employer work or from a client engagement.

A few small utilities are shared across the portfolio repositories. They are maintained in parallel and kept aligned:

| Shared utility | Where it lives here |
| --- | --- |
| Cassette provider | `src/roi_model/evalkit/providers/cassette.py` |
| Invariant checks | `src/roi_model/evalkit/invariants.py` |
| JSON trace | `src/roi_model/trace.py` |
| Structured logging | `src/roi_model/logging_setup.py` |
| Secret scanner | `src/roi_model/secretscan.py` |

What was adapted here is the monthly ROI model: assumption loading, payback, break-even, NPV, tornado, scenarios, Monte Carlo, and the CSV / XLSX / one-pager exports. Those pieces are specific to this calculator.

## Vendored secret scanner

`src/roi_model/secretscan.py` is a vendored copy kept identical across the portfolio repositories. Recompute the hash after any edit and update the line below. `make secretscan-hash` and the unit tests both check it.

sha256: 0744539d5ac950acc3d7b4fc1fc869a38bee19c12a9f06fcd8574c1065e3ed2a
