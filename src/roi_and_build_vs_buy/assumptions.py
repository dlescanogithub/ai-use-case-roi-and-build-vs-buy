"""Shared assumption contract for the ROI model and the decision kit.

Both modules label an invented number with ``[EST]``. A number that is not an
estimate names a source and a date. The decision kit stores that envelope as a
``Quantity``. The ROI model stores ranges around the same tag.
"""

from __future__ import annotations

EST_TAG = "[EST]"


def marker(*, estimate: bool) -> str:
    """Report label for one input."""

    return EST_TAG if estimate else "sourced"


def rationale_is_illustrative(rationale: str) -> bool:
    """True when a free-text rationale still carries the shared estimate tag."""

    return EST_TAG in rationale
