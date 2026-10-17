"""Errors raised by the decision kit."""

from __future__ import annotations


class DecisionKitError(Exception):
    """Base error for configuration and runtime failures."""


class ValidationError(DecisionKitError):
    """Input failed a policy or schema check."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))
