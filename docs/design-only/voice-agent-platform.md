# Voice-agent platform selection

Status: **design only**. There is no weights file, no TCO file, and no golden winner.

A voice platform adds criteria this kit's eight names only partly cover. If a case is implemented later, extend the matrix on purpose instead of stuffing telephony into "extensibility".

## Extra criteria to add before scoring

| Criterion | What a score would record | Gated effect that stays outside the kit |
| --- | --- | --- |
| Turn latency | The fictional case notes' claim about time to first audio | None, until a call is actually placed |
| Telephony ownership | Who owns the number and the recording | Buying a number, placing a call |
| Language coverage | Which languages the fictional case notes claim | None |
| Barge-in and handoff | Whether a person can take the call back | Transferring a live caller |
| Recording and retention | Where audio lives and for how long | Storing a recording |

## What a later implementation would reuse

The same weight-sum check, the same TCO shape (build hours versus seats, usage, exit), the same provenance rule, and a new golden winner. Live price scraping would still be out of scope. A person would type the price envelope.

## Approval

The decision owner would accept an ADR the same way as ADR 0002. This file is not that ADR.
