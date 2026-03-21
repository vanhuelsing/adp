"""ADP HTTP clients — synchronous and asynchronous.

Both :class:`ADPClient` and :class:`AsyncADPClient` implement the same four
operations defined by the ADP v0.2 HTTP binding:

* :meth:`discover`      — ``GET  /.well-known/adp.json``
* :meth:`request_deal`  — ``POST /adp/offer``
* :meth:`send_intent`   — ``POST /adp/intent``
* :meth:`get_health`    — ``GET  /health``

Usage (sync)::

    from adp_sdk import ADPClient, DealRequest

    with ADPClient("https://api.provider.com", api_key="sk-...") as client:
        discovery = client.discover()
        offer = client.request_deal(deal_request)
        ack = client.send_intent(deal_intent)

Usage (async)::

    from adp_sdk import AsyncADPClient

    async with AsyncADPClient("https://api.provider.com", api_key="sk-...") as client:
        discovery = await client.discover()
        offer = await client.request_deal(deal_request)
        ack = await client.send_intent(deal_intent)
"""

from __future__ import annotations

from typing import Any

import httpx

from .exceptions import ADPConnectionError, ADPHTTPError, ADPValidationError
from .models import DealIntent, DealIntentAck, DealOffer, DealRequest, WellKnownADP

_ADP_VERSION = "0.2.0"
_DEFAULT_TIMEOUT = 30.0


def _build_headers(api_key: str | None) -> dict[str, str]:
    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-ADP-Version": _ADP_VERSION,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _raise_for_status(response: httpx.Response) -> None:
    if response.is_success:
        return
    try:
        body = response.text
    except Exception:  # noqa: BLE001
        body = ""
    raise ADPHTTPError(
        f"HTTP {response.status_code} from {response.url}",
        status_code=response.status_code,
        response_body=body,
    )


# ---------------------------------------------------------------------------
# Synchronous client
# ---------------------------------------------------------------------------


class ADPClient:
    """Synchronous ADP client backed by :mod:`httpx`.

    Can be used as a context manager to manage the underlying HTTP connection
    pool, or instantiated without ``with`` for one-shot requests.

    Args:
        base_url: Root URL of the ADP-compatible provider (no trailing slash).
        api_key: Optional API key sent as ``Authorization: Bearer <key>``.
        timeout: HTTP request timeout in seconds (default: 30).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._client: httpx.Client | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> ADPClient:
        self._client = httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(self._api_key),
            timeout=self._timeout,
        )
        return self

    def __exit__(self, *_: Any) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.Client:
        if self._client is not None:
            return self._client
        # One-shot client (not using context manager)
        return httpx.Client(
            base_url=self._base_url,
            headers=_build_headers(self._api_key),
            timeout=self._timeout,
        )

    def _get(self, path: str) -> httpx.Response:
        client = self._get_client()
        owned = self._client is None
        try:
            try:
                response = client.get(path)
            except httpx.ConnectError as exc:
                raise ADPConnectionError(str(exc)) from exc
            except httpx.TimeoutException as exc:
                raise ADPConnectionError(f"Request timed out: {exc}") from exc
            _raise_for_status(response)
            return response
        finally:
            if owned:
                client.close()

    def _post(self, path: str, payload: dict[str, Any]) -> httpx.Response:
        client = self._get_client()
        owned = self._client is None
        try:
            try:
                response = client.post(path, json=payload)
            except httpx.ConnectError as exc:
                raise ADPConnectionError(str(exc)) from exc
            except httpx.TimeoutException as exc:
                raise ADPConnectionError(f"Request timed out: {exc}") from exc
            _raise_for_status(response)
            return response
        finally:
            if owned:
                client.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def discover(self) -> WellKnownADP:
        """Fetch the ADP discovery document.

        ``GET /.well-known/adp.json``
        """
        response = self._get("/.well-known/adp.json")
        try:
            return WellKnownADP.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid discovery response: {exc}") from exc

    def request_deal(self, deal_request: DealRequest) -> DealOffer:
        """Request a deal offer from the provider.

        ``POST /adp/offer``

        Args:
            deal_request: The :class:`~adp_sdk.models.DealRequest` to send.

        Returns:
            A :class:`~adp_sdk.models.DealOffer` from the provider.
        """
        payload = deal_request.model_dump(exclude_none=True)
        response = self._post("/adp/offer", payload)
        try:
            return DealOffer.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid DealOffer response: {exc}") from exc

    def send_intent(self, deal_intent: DealIntent) -> DealIntentAck:
        """Signal intent to accept an offer.

        ``POST /adp/intent``

        Args:
            deal_intent: The :class:`~adp_sdk.models.DealIntent` to send.

        Returns:
            A :class:`~adp_sdk.models.DealIntentAck` acknowledgment.
        """
        payload = deal_intent.model_dump(exclude_none=True)
        response = self._post("/adp/intent", payload)
        try:
            return DealIntentAck.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid DealIntentAck response: {exc}") from exc

    def get_health(self) -> dict[str, Any]:
        """Check the provider's health endpoint.

        ``GET /health``
        """
        response = self._get("/health")
        return response.json()  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Asynchronous client
# ---------------------------------------------------------------------------


class AsyncADPClient:
    """Asynchronous ADP client backed by :mod:`httpx`.

    Can be used as an async context manager or instantiated for one-shot
    requests (though context manager usage is recommended for connection
    reuse).

    Args:
        base_url: Root URL of the ADP-compatible provider (no trailing slash).
        api_key: Optional API key sent as ``Authorization: Bearer <key>``.
        timeout: HTTP request timeout in seconds (default: 30).
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> AsyncADPClient:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(self._api_key),
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(
            base_url=self._base_url,
            headers=_build_headers(self._api_key),
            timeout=self._timeout,
        )

    async def _get(self, path: str) -> httpx.Response:
        client = self._get_client()
        owned = self._client is None
        try:
            try:
                response = await client.get(path)
            except httpx.ConnectError as exc:
                raise ADPConnectionError(str(exc)) from exc
            except httpx.TimeoutException as exc:
                raise ADPConnectionError(f"Request timed out: {exc}") from exc
            _raise_for_status(response)
            return response
        finally:
            if owned:
                await client.aclose()

    async def _post(self, path: str, payload: dict[str, Any]) -> httpx.Response:
        client = self._get_client()
        owned = self._client is None
        try:
            try:
                response = await client.post(path, json=payload)
            except httpx.ConnectError as exc:
                raise ADPConnectionError(str(exc)) from exc
            except httpx.TimeoutException as exc:
                raise ADPConnectionError(f"Request timed out: {exc}") from exc
            _raise_for_status(response)
            return response
        finally:
            if owned:
                await client.aclose()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def discover(self) -> WellKnownADP:
        """Fetch the ADP discovery document.

        ``GET /.well-known/adp.json``
        """
        response = await self._get("/.well-known/adp.json")
        try:
            return WellKnownADP.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid discovery response: {exc}") from exc

    async def request_deal(self, deal_request: DealRequest) -> DealOffer:
        """Request a deal offer from the provider.

        ``POST /adp/offer``
        """
        payload = deal_request.model_dump(exclude_none=True)
        response = await self._post("/adp/offer", payload)
        try:
            return DealOffer.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid DealOffer response: {exc}") from exc

    async def send_intent(self, deal_intent: DealIntent) -> DealIntentAck:
        """Signal intent to accept an offer.

        ``POST /adp/intent``
        """
        payload = deal_intent.model_dump(exclude_none=True)
        response = await self._post("/adp/intent", payload)
        try:
            return DealIntentAck.model_validate(response.json())
        except Exception as exc:  # noqa: BLE001
            raise ADPValidationError(f"Invalid DealIntentAck response: {exc}") from exc

    async def get_health(self) -> dict[str, Any]:
        """Check the provider's health endpoint.

        ``GET /health``
        """
        response = await self._get("/health")
        return response.json()  # type: ignore[no-any-return]


__all__ = ["ADPClient", "AsyncADPClient"]
