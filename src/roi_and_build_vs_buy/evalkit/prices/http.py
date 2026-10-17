"""Optional HTTP quote adapter. Off unless DECIDE_REAL_PROVIDER=1. Not used by evals."""

from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal

from roi_and_build_vs_buy.build_vs_buy.errors import DecisionKitError
from roi_and_build_vs_buy.evalkit.prices.base import Quote
from roi_and_build_vs_buy.retry import retry_call

Transport = Callable[[str, dict[str, str]], dict[str, object]]


class HttpPriceProvider:
    """Call a quote URL through an injected transport, with bounded retries.

    The kit does not open a socket here. The caller supplies `transport`.
    The factory refuses to build this class unless the real-provider flag is on.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        *,
        transport: Transport,
        max_attempts: int,
        backoff_cap: float,
        sleep: Callable[[float], None] | None = None,
    ) -> None:
        if not base_url or not api_key:
            raise DecisionKitError("HTTP provider requires a base URL and an API key")
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._transport = transport
        self._max_attempts = max_attempts
        self._backoff_cap = backoff_cap
        self._sleep = sleep

    def quote(self, vendor_id: str) -> Quote:
        def attempt() -> Quote:
            payload = self._transport(
                f"{self._base_url}/quotes/{vendor_id}",
                {"Authorization": f"Bearer {self._api_key}"},
            )
            amount = payload.get("usd_per_seat_year")
            if isinstance(amount, bool) or not isinstance(amount, (int, float, str)):
                raise DecisionKitError("quote payload missing usd_per_seat_year")
            return Quote(
                vendor_id=vendor_id,
                usd_per_seat_year=Decimal(str(amount)),
                source="real provider response",
                simulated=False,
                cost_usd=Decimal(0),
            )

        if self._sleep is None:
            return retry_call(
                attempt,
                max_attempts=self._max_attempts,
                backoff_cap=self._backoff_cap,
            )
        return retry_call(
            attempt,
            max_attempts=self._max_attempts,
            backoff_cap=self._backoff_cap,
            sleep=self._sleep,
        )
