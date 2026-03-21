"""Tests for ADP validator functions."""

import pytest

from adp_sdk.validator import (
    ValidationResult,
    validate_deal_intent,
    validate_deal_intent_result,
    validate_deal_offer,
    validate_deal_offer_result,
    validate_deal_request,
    validate_deal_request_result,
)

# ---------------------------------------------------------------------------
# Valid fixtures (reuse same data as test_models)
# ---------------------------------------------------------------------------

VALID_DEAL_REQUEST = {
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
        },
        "budget": {"currency": "USD"},
    },
}

VALID_DEAL_OFFER = {
    "adp": {
        "version": "0.2.0",
        "type": "DealOffer",
        "id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
        "timestamp": "2026-03-12T10:00:01Z",
        "correlation_id": "c768627a-3d18-49a4-9c75-5017d45fa0de",
    },
    "offer": {
        "provider": {"provider_id": "openai", "name": "OpenAI"},
        "model": {
            "model_id": "gpt-4o",
            "name": "GPT-4o",
            "task_classes": ["general"],
            "context_window": 128000,
            "max_output_tokens": 16384,
            "modalities": ["text"],
            "capabilities": ["streaming"],
        },
        "pricing": {
            "currency": "USD",
            "base": {"input_per_mtok": 2.50, "output_per_mtok": 10.00},
        },
        "compliance": {"compliance_verified_by": "self-declared"},
        "valid_from": "2026-03-12T00:00:00Z",
        "valid_until": "2026-04-12T00:00:00Z",
    },
}

VALID_DEAL_INTENT = {
    "adp": {
        "version": "0.2.0",
        "type": "DealIntent",
        "id": "7f52524e-744e-4d86-822f-535040047566",
        "timestamp": "2026-03-12T10:05:00Z",
        "correlation_id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
    },
    "intent": {
        "binding": False,
        "requester": {"agent_id": "agent:x", "is_automated": True},
        "accepted_offer_id": "6e14ea4e-4af0-4c38-8c1e-9ea63c422a6b",
        "accepted_pricing_snapshot": {"input_per_mtok": 2.50, "output_per_mtok": 10.00},
        "activation": {"type": "redirect"},
    },
}


# ---------------------------------------------------------------------------
# validate_deal_request
# ---------------------------------------------------------------------------


class TestValidateDealRequest:
    def test_valid_returns_true(self) -> None:
        assert validate_deal_request(VALID_DEAL_REQUEST) is True

    def test_missing_adp_returns_false(self) -> None:
        data = {"request": VALID_DEAL_REQUEST["request"]}
        assert validate_deal_request(data) is False

    def test_missing_requester_returns_false(self) -> None:
        data = {
            "adp": VALID_DEAL_REQUEST["adp"],
            "request": {"budget": {"currency": "USD"}},
        }
        assert validate_deal_request(data) is False

    def test_non_dict_returns_false(self) -> None:
        assert validate_deal_request("not a dict") is False
        assert validate_deal_request(None) is False
        assert validate_deal_request(42) is False

    def test_empty_dict_returns_false(self) -> None:
        assert validate_deal_request({}) is False


# ---------------------------------------------------------------------------
# validate_deal_offer
# ---------------------------------------------------------------------------


class TestValidateDealOffer:
    def test_valid_returns_true(self) -> None:
        assert validate_deal_offer(VALID_DEAL_OFFER) is True

    def test_missing_pricing_returns_false(self) -> None:
        data = {
            "adp": VALID_DEAL_OFFER["adp"],
            "offer": {k: v for k, v in VALID_DEAL_OFFER["offer"].items() if k != "pricing"},
        }
        assert validate_deal_offer(data) is False

    def test_invalid_compliance_value_returns_false(self) -> None:
        import copy

        data = copy.deepcopy(VALID_DEAL_OFFER)
        data["offer"]["compliance"]["compliance_verified_by"] = "alien-verified"  # type: ignore[index]
        assert validate_deal_offer(data) is False

    def test_non_dict_returns_false(self) -> None:
        assert validate_deal_offer([]) is False


# ---------------------------------------------------------------------------
# validate_deal_intent
# ---------------------------------------------------------------------------


class TestValidateDealIntent:
    def test_valid_returns_true(self) -> None:
        assert validate_deal_intent(VALID_DEAL_INTENT) is True

    def test_binding_true_returns_false(self) -> None:
        import copy

        data = copy.deepcopy(VALID_DEAL_INTENT)
        data["intent"]["binding"] = True  # type: ignore[index]
        assert validate_deal_intent(data) is False

    def test_missing_activation_returns_false(self) -> None:
        import copy

        data = copy.deepcopy(VALID_DEAL_INTENT)
        del data["intent"]["activation"]  # type: ignore[attr-defined]
        assert validate_deal_intent(data) is False

    def test_non_dict_returns_false(self) -> None:
        assert validate_deal_intent(None) is False


# ---------------------------------------------------------------------------
# Detailed result variants
# ---------------------------------------------------------------------------


class TestValidationResult:
    def test_valid_result_has_no_errors(self) -> None:
        result = validate_deal_request_result(VALID_DEAL_REQUEST)
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.errors == []

    def test_invalid_result_has_errors(self) -> None:
        result = validate_deal_request_result({})
        assert result.valid is False
        assert len(result.errors) > 0

    def test_offer_valid_result(self) -> None:
        result = validate_deal_offer_result(VALID_DEAL_OFFER)
        assert result.valid is True

    def test_offer_invalid_result_contains_path(self) -> None:
        import copy

        data = copy.deepcopy(VALID_DEAL_OFFER)
        del data["offer"]["provider"]  # type: ignore[attr-defined]
        result = validate_deal_offer_result(data)
        assert result.valid is False
        assert any("provider" in e for e in result.errors)

    def test_intent_valid_result(self) -> None:
        result = validate_deal_intent_result(VALID_DEAL_INTENT)
        assert result.valid is True

    def test_intent_invalid_result(self) -> None:
        result = validate_deal_intent_result({"garbage": True})
        assert result.valid is False
        assert result.errors
