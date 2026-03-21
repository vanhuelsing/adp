"""Tests for ADP Pydantic models."""

import pytest
from pydantic import ValidationError

from adp_sdk.models import (
    Acknowledgment,
    Activation,
    ADPHeader,
    Budget,
    Compliance,
    Contact,
    DealError,
    DealErrorBody,
    DealIntent,
    DealIntentAck,
    DealIntentBody,
    DealOffer,
    DealOfferBody,
    DealRequest,
    DealRequestBody,
    FieldError,
    FreeTier,
    Model,
    Preferences,
    Pricing,
    PricingBase,
    PricingModifier,
    PricingSnapshot,
    PricingTier,
    Provider,
    Requester,
    Requirements,
    SLA,
    Volume,
    VolumeCommitment,
    WellKnownADP,
)

# ---------------------------------------------------------------------------
# Fixture data matching spec-v02/examples
# ---------------------------------------------------------------------------

DEAL_REQUEST_DATA = {
    "adp": {
        "version": "0.2.0",
        "type": "DealRequest",
        "id": "c768627a-3d18-49a4-9c75-5017d45fa0de",
        "timestamp": "2026-03-12T10:00:00Z",
        "correlation_id": None,
    },
    "request": {
        "requester": {
            "agent_id": "agent:mycompany:document-analyzer",
            "is_automated": True,
            "name": "MyCompany Document Analyzer",
            "contact": {"email": "deals@mycompany.com"},
        },
        "requirements": {
            "task_classes": ["reasoning", "multimodal"],
            "modalities": ["text", "image_input"],
        },
        "volume": {
            "estimated_monthly_input_tokens": 50_000_000,
            "estimated_monthly_output_tokens": 10_000_000,
            "pattern": "steady",
            "batch_eligible": True,
        },
        "budget": {
            "max_cost_per_mtok_input": 5.0,
            "max_cost_per_mtok_output": 15.0,
            "currency": "USD",
            "max_monthly_spend": 300.0,
        },
        "preferences": {
            "commitment": "none",
            "preferred_providers": ["openai", "anthropic"],
            "excluded_providers": [],
            "deal_type": "pay_as_you_go",
        },
        "valid_until": "2026-03-19T10:00:00Z",
        "request_ttl_hours": 168,
    },
}

DEAL_OFFER_DATA = {
    "adp": {
        "version": "0.2.0",
        "type": "DealOffer",
        "id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
        "timestamp": "2026-03-12T10:00:01Z",
        "correlation_id": "c768627a-3d18-49a4-9c75-5017d45fa0de",
    },
    "offer": {
        "provider": {
            "provider_id": "openai",
            "name": "OpenAI",
            "url": "https://openai.com",
            "contact": {"email": "api@openai.com", "support_url": "https://help.openai.com"},
        },
        "model": {
            "model_id": "gpt-4o",
            "name": "GPT-4o",
            "version": "2026-03",
            "task_classes": ["general", "reasoning", "coding", "multimodal"],
            "context_window": 128000,
            "max_output_tokens": 65536,
            "modalities": ["text", "image_input"],
            "capabilities": ["tool_use", "structured_output", "streaming"],
            "knowledge_cutoff": "2023-10-01",
        },
        "pricing": {
            "currency": "USD",
            "base": {"input_per_mtok": 2.50, "output_per_mtok": 10.00},
            "modifiers": [{"type": "cache_read", "input_per_mtok": 1.25, "conditions": "Cached"}],
        },
        "compliance": {
            "compliance_verified_by": "self-declared",
            "certifications": ["soc2"],
            "data_regions": ["US"],
            "gdpr_compliant": False,
            "training_on_data": True,
            "privacy_policy_url": "https://openai.com/privacy",
        },
        "sla": {"uptime_pct": 99.9, "ttft_p50_ms": 500, "ttft_p99_ms": 2000, "tps_median": 100},
        "valid_from": "2026-03-12T00:00:00Z",
        "valid_until": "2026-04-12T00:00:00Z",
        "terms_url": "https://openai.com/terms/service",
    },
}

DEAL_INTENT_DATA = {
    "adp": {
        "version": "0.2.0",
        "type": "DealIntent",
        "id": "7f52524e-744e-4d86-822f-535040047566",
        "timestamp": "2026-03-12T10:05:00Z",
        "correlation_id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
    },
    "intent": {
        "binding": False,
        "requires_human_confirmation": True,
        "party_type": "business",
        "requester": {
            "agent_id": "agent:mycompany:document-analyzer",
            "is_automated": True,
        },
        "accepted_offer_id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
        "accepted_pricing_snapshot": {
            "input_per_mtok": 2.50,
            "output_per_mtok": 10.00,
            "modifiers_applied": [],
        },
        "volume_commitment": {
            "estimated_monthly_input_tokens": 50_000_000,
            "commitment_type": "none",
        },
        "activation": {
            "type": "redirect",
            "redirect_url": "https://platform.openai.com/signup?ref=adp",
        },
    },
}

DEAL_INTENT_ACK_DATA = {
    "adp": {
        "version": "0.2.0",
        "type": "DealIntentAck",
        "id": "c2edebba-25f8-48eb-bcfe-1bb1be474e73",
        "timestamp": "2026-03-12T10:05:01Z",
        "correlation_id": "7f52524e-744e-4d86-822f-535040047566",
    },
    "acknowledgment": {
        "status": "received",
        "next_steps": "Please complete signup at https://platform.openai.com/signup",
        "reference_id": "REF-20260312-001",
        "expires_at": "2026-03-19T10:05:01Z",
    },
}

WELL_KNOWN_DATA = {
    "discovery_version": "0.2.0",
    "adp_supported": True,
    "adp_versions": ["0.1.1", "0.2.0"],
    "offer_endpoint": "https://api.provider.com/adp/offer",
    "intent_endpoint": "https://api.provider.com/adp/intent",
    "auth": {
        "methods": ["api_key", "oauth2"],
        "api_key": {"format": "adp_<version>_<key>_<checksum>"},
    },
    "rate_limiting": {"requests_per_minute": 1000},
    "contact": {"email": "api@provider.com"},
    "last_updated": "2026-03-12T10:00:00Z",
}


# ---------------------------------------------------------------------------
# ADPHeader
# ---------------------------------------------------------------------------


class TestADPHeader:
    def test_basic(self) -> None:
        h = ADPHeader(
            version="0.2.0",
            type="DealRequest",
            id="abc",
            timestamp="2026-01-01T00:00:00Z",
        )
        assert h.version == "0.2.0"
        assert h.correlation_id is None

    def test_correlation_id(self) -> None:
        h = ADPHeader(
            version="0.2.0",
            type="DealOffer",
            id="abc",
            timestamp="2026-01-01T00:00:00Z",
            correlation_id="def",
        )
        assert h.correlation_id == "def"

    def test_missing_required(self) -> None:
        with pytest.raises(ValidationError):
            ADPHeader(type="DealRequest", id="x", timestamp="2026-01-01T00:00:00Z")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# DealRequest
# ---------------------------------------------------------------------------


class TestDealRequest:
    def test_from_example(self) -> None:
        req = DealRequest.model_validate(DEAL_REQUEST_DATA)
        assert req.adp.type == "DealRequest"
        assert req.request.requester.agent_id == "agent:mycompany:document-analyzer"
        assert req.request.budget is not None
        assert req.request.budget.currency == "USD"
        assert req.request.volume is not None
        assert req.request.volume.pattern == "steady"

    def test_requirements_modalities(self) -> None:
        req = DealRequest.model_validate(DEAL_REQUEST_DATA)
        assert req.request.requirements is not None
        assert "image_input" in req.request.requirements.modalities  # type: ignore[operator]

    def test_minimal(self) -> None:
        data = {
            "adp": {
                "version": "0.2.0",
                "type": "DealRequest",
                "id": "abc",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            "request": {
                "requester": {"agent_id": "agent:x", "is_automated": False},
            },
        }
        req = DealRequest.model_validate(data)
        assert req.request.budget is None
        assert req.request.volume is None

    def test_missing_requester_raises(self) -> None:
        data = {
            "adp": {"version": "0.2.0", "type": "DealRequest", "id": "x", "timestamp": "t"},
            "request": {},
        }
        with pytest.raises(ValidationError):
            DealRequest.model_validate(data)

    def test_round_trip(self) -> None:
        req = DealRequest.model_validate(DEAL_REQUEST_DATA)
        dumped = req.model_dump(exclude_none=True)
        req2 = DealRequest.model_validate(dumped)
        assert req == req2


# ---------------------------------------------------------------------------
# DealOffer
# ---------------------------------------------------------------------------


class TestDealOffer:
    def test_from_example(self) -> None:
        offer = DealOffer.model_validate(DEAL_OFFER_DATA)
        assert offer.offer.provider.provider_id == "openai"
        assert offer.offer.model.context_window == 128000
        assert offer.offer.pricing.base.input_per_mtok == 2.50
        assert offer.offer.compliance.compliance_verified_by == "self-declared"

    def test_sla(self) -> None:
        offer = DealOffer.model_validate(DEAL_OFFER_DATA)
        assert offer.offer.sla is not None
        assert offer.offer.sla.uptime_pct == 99.9

    def test_pricing_modifier(self) -> None:
        offer = DealOffer.model_validate(DEAL_OFFER_DATA)
        assert offer.offer.pricing.modifiers is not None
        assert offer.offer.pricing.modifiers[0].type == "cache_read"

    def test_multimodal_pricing_extra_field(self) -> None:
        data = dict(DEAL_OFFER_DATA)
        data["offer"] = dict(DEAL_OFFER_DATA["offer"])
        data["offer"]["pricing"] = {
            **DEAL_OFFER_DATA["offer"]["pricing"],
            "modalities": {"text": {"input_per_mtok": 2.50}},
        }
        offer = DealOffer.model_validate(data)
        assert offer.offer.pricing.modalities is not None

    def test_missing_provider_raises(self) -> None:
        data = {k: v for k, v in DEAL_OFFER_DATA.items()}
        data["offer"] = {k: v for k, v in DEAL_OFFER_DATA["offer"].items()}
        del data["offer"]["provider"]  # type: ignore[attr-defined]
        with pytest.raises(ValidationError):
            DealOffer.model_validate(data)


# ---------------------------------------------------------------------------
# DealIntent
# ---------------------------------------------------------------------------


class TestDealIntent:
    def test_from_example(self) -> None:
        intent = DealIntent.model_validate(DEAL_INTENT_DATA)
        assert intent.intent.binding is False
        assert intent.intent.accepted_offer_id == "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b"
        assert intent.intent.activation.type == "redirect"

    def test_binding_must_be_false(self) -> None:
        data = dict(DEAL_INTENT_DATA)
        data["intent"] = {**DEAL_INTENT_DATA["intent"], "binding": True}
        with pytest.raises(ValidationError):
            DealIntent.model_validate(data)

    def test_pricing_snapshot(self) -> None:
        intent = DealIntent.model_validate(DEAL_INTENT_DATA)
        snap = intent.intent.accepted_pricing_snapshot
        assert snap.input_per_mtok == 2.50
        assert snap.output_per_mtok == 10.00


# ---------------------------------------------------------------------------
# DealIntentAck
# ---------------------------------------------------------------------------


class TestDealIntentAck:
    def test_from_example(self) -> None:
        ack = DealIntentAck.model_validate(DEAL_INTENT_ACK_DATA)
        assert ack.adp.type == "DealIntentAck"
        assert ack.acknowledgment.status == "received"
        assert ack.acknowledgment.reference_id == "REF-20260312-001"

    def test_invalid_status(self) -> None:
        data = {**DEAL_INTENT_ACK_DATA}
        data["acknowledgment"] = {**DEAL_INTENT_ACK_DATA["acknowledgment"], "status": "unknown"}
        with pytest.raises(ValidationError):
            DealIntentAck.model_validate(data)


# ---------------------------------------------------------------------------
# DealError
# ---------------------------------------------------------------------------


class TestDealError:
    def test_basic(self) -> None:
        data = {
            "adp": {
                "version": "0.2.0",
                "type": "DealError",
                "id": "err-1",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Missing required field: requester",
                "retryable": False,
            },
        }
        err = DealError.model_validate(data)
        assert err.error.code == "INVALID_REQUEST"
        assert err.error.retryable is False
        assert err.error.retry_after_ms is None

    def test_rate_limited_with_retry(self) -> None:
        data = {
            "adp": {
                "version": "0.2.0",
                "type": "DealError",
                "id": "err-2",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            "error": {
                "code": "RATE_LIMITED",
                "message": "Too many requests",
                "retryable": True,
                "retry_after_ms": 5000,
            },
        }
        err = DealError.model_validate(data)
        assert err.error.retry_after_ms == 5000

    def test_field_errors(self) -> None:
        data = {
            "adp": {
                "version": "0.2.0",
                "type": "DealError",
                "id": "err-3",
                "timestamp": "2026-01-01T00:00:00Z",
            },
            "error": {
                "code": "INVALID_REQUEST",
                "message": "Validation failed",
                "field_errors": [
                    {"field": "request.budget.currency", "code": "required", "message": "missing"}
                ],
                "retryable": False,
            },
        }
        err = DealError.model_validate(data)
        assert err.error.field_errors is not None
        assert err.error.field_errors[0].field == "request.budget.currency"

    def test_invalid_error_code(self) -> None:
        data = {
            "adp": {"version": "0.2.0", "type": "DealError", "id": "e", "timestamp": "t"},
            "error": {"code": "UNKNOWN_CODE", "message": "?", "retryable": False},
        }
        with pytest.raises(ValidationError):
            DealError.model_validate(data)


# ---------------------------------------------------------------------------
# WellKnownADP
# ---------------------------------------------------------------------------


class TestWellKnownADP:
    def test_from_example(self) -> None:
        doc = WellKnownADP.model_validate(WELL_KNOWN_DATA)
        assert doc.adp_supported is True
        assert "0.2.0" in doc.adp_versions
        assert doc.auth is not None
        assert doc.auth.methods is not None
        assert "api_key" in doc.auth.methods

    def test_minimal(self) -> None:
        doc = WellKnownADP.model_validate({"adp_supported": True, "adp_versions": ["0.2.0"]})
        assert doc.offer_endpoint is None

    def test_missing_required_raises(self) -> None:
        with pytest.raises(ValidationError):
            WellKnownADP.model_validate({"adp_supported": True})
