"""Block outbound sockets for the whole suite."""

from __future__ import annotations

import socket
from collections.abc import Iterator

import pytest

_ORIGINAL_CONNECT = socket.socket.connect


def _blocked(self: socket.socket, address: object) -> None:
    raise RuntimeError(f"network is disabled in tests: {address}")


@pytest.fixture(autouse=True)
def _no_network() -> Iterator[None]:
    socket.socket.connect = _blocked  # type: ignore[method-assign]
    try:
        yield
    finally:
        socket.socket.connect = _ORIGINAL_CONNECT  # type: ignore[method-assign]
