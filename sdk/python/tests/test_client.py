"""Tests for ADPClient and AsyncADPClient using mocked httpx via respx."""

import json

import httpx
import pytest
import respx

from adp_sdk import (
    ADPClient,
    ADPConnectionError,
    ADPHTTPError,
    ADPValidationError,
    AsyncADPClient,
    DealIntentAck,
    DealOffer,
    WellKnownADP,
)
from adp_sdk.models import (
    Acknowledgment,
    Activation,
    ADPHeader,
    DealIntent,
    DealIntentBody,
    DealOfferBody,
    DealRequest,
    DealRequestBody,
    Model,
    Pricing,
    PricingBase,
    PricingSnapshot,
    Provider,
    Requester,
    Compliance,
)

BASE_URL = "https://api.testprovider.com"

# ---------------------------------------------------------------------------
# Shared response fixtures
# ---------------------------------------------------------------------------

WELL_KNOWN_RESPONSE = {
    "adp_supported": True,
    "adp_versions": ["0.2.0"],
    "offer_endpoint": f"{BASE_URL}/adp/offer",
    "intent_endpoint": f"{BASE_URL}/adp/intent",
}

DEAL_OFFER_RESPONSE = {
    "adp": {
        "version": "0.2.0",
        "type": "DealOffer",
        "id": "offer-123",
        "timestamp": "2026-03-12T10:00:01Z",
        "correlation_id": "req-123",
    },
    "offer": {
        "provider": {"provider_id": "testprovider", "name": "Test Provider"},
        "model": {
            "model_id": "test-model",
            "name": "Test Model",
            "task_classes": ["general"],
            "context_window": 8192,
            "max_output_tokens": 4096,
            "modalities": ["text"],
            "capabilities": ["streaming"],
        },
        "pricing": {
            "currency": "USD",
            "base": {"input_per_mtok": 1.00, "output_per_mtok": 3.00},
        },
        "compliance": {"compliance_verified_by": "self-declared"},
        "valid_from": "2026-03-12T00:00:00Z",
        "valid_until": "2026-04-12T00:00:00Z",
    },
}

DEAL_INTENT_ACK_RESPONSE = {
    "adp": {
        "version": "0.2.0",
        "type": "DealIntentAck",
        "id": "ack-456",
        "timestamp": "2026-03-12T10:05:01Z",
        "correlation_id": "intent-789",
    },
    "acknowledgment": {
        "status": "received",
        "reference_id": "REF-001",
    },
}

HEALTH_RESPONSE = {"status": "ok", "version": "0.2.0"}


def _make_deal_request() -> DealRequest:
    return DealRequest(
        adp=ADPHeader(
            version="0.2.0",
            type="DealRequest",
            id="req-123",
            timestamp="2026-03-12T10:00:00Z",
        ),
        request=DealRequestBody(
            requester=Requester(agent_id="agent:test:bot", is_automated=True),
        ),
    )


def _make_deal_intent() -> DealIntent:
    return DealIntent(
        adp=ADPHeader(
            version="0.2.0",
            type="DealIntent",
            id="intent-789",
            timestamp="2026-03-12T10:05:00Z",
            correlation_id="offer-123",
        ),
        intent=DealIntentBody(
            binding=False,
            requester=Requester(agent_id="agent:test:bot", is_automated=True),
            accepted_offer_id="offer-123",
            accepted_pricing_snapshot=PricingSnapshot(
                input_per_mtok=1.00,
                output_per_mtok=3.00,
            ),
            activation=Activation(type="redirect"),
        ),
    )


# ---------------------------------------------------------------------------
# Sync client tests
# ---------------------------------------------------------------------------


class TestADPClientDiscover:
    @respx.mock
    def test_discover_returns_well_known(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(200, json=WELL_KNOWN_RESPONSE)
        )
        with ADPClient(BASE_URL) as client:
            doc = client.discover()
        assert isinstance(doc, WellKnownADP)
        assert doc.adp_supported is True
        assert "0.2.0" in doc.adp_versions

    @respx.mock
    def test_discover_sets_auth_header(self) -> None:
        route = respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(200, json=WELL_KNOWN_RESPONSE)
        )
        with ADPClient(BASE_URL, api_key="sk-test") as client:
            client.discover()
        request = route.calls.last.request
        assert request.headers["authorization"] == "Bearer sk-test"

    @respx.mock
    def test_discover_http_error_raises(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(503, text="Service Unavailable")
        )
        with ADPClient(BASE_URL) as client:
            with pytest.raises(ADPHTTPError) as exc_info:
                client.discover()
        assert exc_info.value.status_code == 503

    @respx.mock
    def test_discover_invalid_json_raises(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(200, json={"not_adp": True})
        )
        with ADPClient(BASE_URL) as client:
            with pytest.raises(ADPValidationError):
                client.discover()


class TestADPClientRequestDeal:
    @respx.mock
    def test_request_deal_returns_offer(self) -> None:
        respx.post(f"{BASE_URL}/adp/offer").mock(
            return_value=httpx.Response(200, json=DEAL_OFFER_RESPONSE)
        )
        deal_request = _make_deal_request()
        with ADPClient(BASE_URL) as client:
            offer = client.request_deal(deal_request)
        assert isinstance(offer, DealOffer)
        assert offer.offer.provider.provider_id == "testprovider"
        assert offer.offer.pricing.base.input_per_mtok == 1.00

    @respx.mock
    def test_request_deal_sends_json_body(self) -> None:
        route = respx.post(f"{BASE_URL}/adp/offer").mock(
            return_value=httpx.Response(200, json=DEAL_OFFER_RESPONSE)
        )
        deal_request = _make_deal_request()
        with ADPClient(BASE_URL) as client:
            client.request_deal(deal_request)
        body = json.loads(route.calls.last.request.content)
        assert body["adp"]["type"] == "DealRequest"
        assert body["request"]["requester"]["agent_id"] == "agent:test:bot"

    @respx.mock
    def test_request_deal_400_raises_http_error(self) -> None:
        respx.post(f"{BASE_URL}/adp/offer").mock(
            return_value=httpx.Response(400, json={"error": "bad request"})
        )
        with ADPClient(BASE_URL) as client:
            with pytest.raises(ADPHTTPError) as exc_info:
                client.request_deal(_make_deal_request())
        assert exc_info.value.status_code == 400


class TestADPClientSendIntent:
    @respx.mock
    def test_send_intent_returns_ack(self) -> None:
        respx.post(f"{BASE_URL}/adp/intent").mock(
            return_value=httpx.Response(200, json=DEAL_INTENT_ACK_RESPONSE)
        )
        with ADPClient(BASE_URL) as client:
            ack = client.send_intent(_make_deal_intent())
        assert isinstance(ack, DealIntentAck)
        assert ack.acknowledgment.status == "received"
        assert ack.acknowledgment.reference_id == "REF-001"

    @respx.mock
    def test_send_intent_sends_json_body(self) -> None:
        route = respx.post(f"{BASE_URL}/adp/intent").mock(
            return_value=httpx.Response(200, json=DEAL_INTENT_ACK_RESPONSE)
        )
        with ADPClient(BASE_URL) as client:
            client.send_intent(_make_deal_intent())
        body = json.loads(route.calls.last.request.content)
        assert body["adp"]["type"] == "DealIntent"
        assert body["intent"]["binding"] is False


class TestADPClientGetHealth:
    @respx.mock
    def test_get_health_returns_dict(self) -> None:
        respx.get(f"{BASE_URL}/health").mock(
            return_value=httpx.Response(200, json=HEALTH_RESPONSE)
        )
        with ADPClient(BASE_URL) as client:
            health = client.get_health()
        assert health["status"] == "ok"

    @respx.mock
    def test_get_health_503_raises(self) -> None:
        respx.get(f"{BASE_URL}/health").mock(return_value=httpx.Response(503))
        with ADPClient(BASE_URL) as client:
            with pytest.raises(ADPHTTPError):
                client.get_health()


class TestADPClientConnectionError:
    @respx.mock
    def test_connect_error_raises_adp_connection_error(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        with ADPClient(BASE_URL) as client:
            with pytest.raises(ADPConnectionError):
                client.discover()


# ---------------------------------------------------------------------------
# Async client tests
# ---------------------------------------------------------------------------


class TestAsyncADPClientDiscover:
    @pytest.mark.asyncio
    @respx.mock
    async def test_discover_returns_well_known(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(200, json=WELL_KNOWN_RESPONSE)
        )
        async with AsyncADPClient(BASE_URL) as client:
            doc = await client.discover()
        assert isinstance(doc, WellKnownADP)
        assert doc.adp_supported is True

    @pytest.mark.asyncio
    @respx.mock
    async def test_discover_http_error_raises(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            return_value=httpx.Response(404, text="Not Found")
        )
        async with AsyncADPClient(BASE_URL) as client:
            with pytest.raises(ADPHTTPError) as exc_info:
                await client.discover()
        assert exc_info.value.status_code == 404


class TestAsyncADPClientRequestDeal:
    @pytest.mark.asyncio
    @respx.mock
    async def test_request_deal_returns_offer(self) -> None:
        respx.post(f"{BASE_URL}/adp/offer").mock(
            return_value=httpx.Response(200, json=DEAL_OFFER_RESPONSE)
        )
        async with AsyncADPClient(BASE_URL) as client:
            offer = await client.request_deal(_make_deal_request())
        assert isinstance(offer, DealOffer)
        assert offer.offer.model.model_id == "test-model"

    @pytest.mark.asyncio
    @respx.mock
    async def test_request_deal_sends_correct_headers(self) -> None:
        route = respx.post(f"{BASE_URL}/adp/offer").mock(
            return_value=httpx.Response(200, json=DEAL_OFFER_RESPONSE)
        )
        async with AsyncADPClient(BASE_URL, api_key="async-key") as client:
            await client.request_deal(_make_deal_request())
        request = route.calls.last.request
        assert request.headers["x-adp-version"] == "0.2.0"
        assert request.headers["authorization"] == "Bearer async-key"


class TestAsyncADPClientSendIntent:
    @pytest.mark.asyncio
    @respx.mock
    async def test_send_intent_returns_ack(self) -> None:
        respx.post(f"{BASE_URL}/adp/intent").mock(
            return_value=httpx.Response(200, json=DEAL_INTENT_ACK_RESPONSE)
        )
        async with AsyncADPClient(BASE_URL) as client:
            ack = await client.send_intent(_make_deal_intent())
        assert isinstance(ack, DealIntentAck)
        assert ack.acknowledgment.status == "received"


class TestAsyncADPClientGetHealth:
    @pytest.mark.asyncio
    @respx.mock
    async def test_get_health_returns_dict(self) -> None:
        respx.get(f"{BASE_URL}/health").mock(
            return_value=httpx.Response(200, json=HEALTH_RESPONSE)
        )
        async with AsyncADPClient(BASE_URL) as client:
            health = await client.get_health()
        assert health["status"] == "ok"


class TestAsyncADPClientConnectionError:
    @pytest.mark.asyncio
    @respx.mock
    async def test_connect_error_raises(self) -> None:
        respx.get(f"{BASE_URL}/.well-known/adp.json").mock(
            side_effect=httpx.ConnectError("refused")
        )
        async with AsyncADPClient(BASE_URL) as client:
            with pytest.raises(ADPConnectionError):
                await client.discover()
