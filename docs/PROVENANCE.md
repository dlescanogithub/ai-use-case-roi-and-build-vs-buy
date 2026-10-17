# Provenance

The brief asked for a documented copy of the eval helpers in `dlescanogithub/agent-runtime-evals` at commit `55cfd4183fb2489d77fc9c8552e008274dc78f77` (draft PR, branch `cursor/agent-runtime-evals-mvp-7e58`).

That copy did not happen. On 2026-10-17 the GitHub token available to this agent could list only `dlescanogithub/ai-use-case-roi-model`. Requests for the other private repository returned 404. No file from that commit was read.

What is in this repo instead is original code that follows the patterns the brief named:

| Pattern the brief named | Where it lives here |
| --- | --- |
| Cassette provider | `src/roi_model/evalkit/providers/cassette.py` |
| Fake provider | `src/roi_model/evalkit/providers/fake.py` |
| JSONL trace | `src/roi_model/trace.py` |
| JSON logging | `src/roi_model/logging_setup.py` |
| Secret scan | `src/roi_model/secretscan.py` |
| Invariant checks, not tool-call trajectories | `src/roi_model/evalkit/invariants.py` |

Do not treat those files as a fork of the other repository. If the other tree becomes readable later, a follow-up can diff them and record what would change.
