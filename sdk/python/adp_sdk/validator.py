"""Validation helpers for ADP messages.

Each ``validate_*`` function accepts arbitrary data (dict, object, etc.) and
returns ``True`` when the data conforms to the corresponding ADP schema, or
``False`` otherwise.

For richer feedback (field-level errors) use the ``*_result`` variants that
return a :class:`ValidationResult`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import ValidationError

from .models import DealIntent, DealOffer, DealRequest


@dataclass
class ValidationResult:
    """Outcome of an ADP message validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helper
# ---------------------------------------------------------------------------


def _validate(model_cls: Any, data: Any) -> ValidationResult:
    try:
        model_cls.model_validate(data)
        return ValidationResult(valid=True)
    except ValidationError as exc:
        errors = [f"{'.'.join(str(l) for l in e['loc'])}: {e['msg']}" for e in exc.errors()]
        return ValidationResult(valid=False, errors=errors)
    except Exception as exc:  # noqa: BLE001
        return ValidationResult(valid=False, errors=[str(exc)])


# ---------------------------------------------------------------------------
# Public API — bool shortcuts
# ---------------------------------------------------------------------------


def validate_deal_request(data: Any) -> bool:
    """Return ``True`` if *data* is a valid :class:`~adp_sdk.models.DealRequest`."""
    return _validate(DealRequest, data).valid


def validate_deal_offer(data: Any) -> bool:
    """Return ``True`` if *data* is a valid :class:`~adp_sdk.models.DealOffer`."""
    return _validate(DealOffer, data).valid


def validate_deal_intent(data: Any) -> bool:
    """Return ``True`` if *data* is a valid :class:`~adp_sdk.models.DealIntent`."""
    return _validate(DealIntent, data).valid


# ---------------------------------------------------------------------------
# Public API — detailed results
# ---------------------------------------------------------------------------


def validate_deal_request_result(data: Any) -> ValidationResult:
    """Validate *data* as a DealRequest and return a :class:`ValidationResult`."""
    return _validate(DealRequest, data)


def validate_deal_offer_result(data: Any) -> ValidationResult:
    """Validate *data* as a DealOffer and return a :class:`ValidationResult`."""
    return _validate(DealOffer, data)


def validate_deal_intent_result(data: Any) -> ValidationResult:
    """Validate *data* as a DealIntent and return a :class:`ValidationResult`."""
    return _validate(DealIntent, data)


__all__ = [
    "ValidationResult",
    "validate_deal_request",
    "validate_deal_offer",
    "validate_deal_intent",
    "validate_deal_request_result",
    "validate_deal_offer_result",
    "validate_deal_intent_result",
]


def validate_deal_error(data: Any) -> bool:
    """Validate a DealError message."""
    return validate_deal_error_result(data).valid


def validate_deal_error_result(data: Any) -> ValidationResult:
    """Validate a DealError message with detailed results."""
    base = _validate_base(data)
    if not base.valid:
        return base
    if not isinstance(data.get("error"), dict):
        return ValidationResult(valid=False, errors=['Missing or invalid "error" field'])
    error = data["error"]
    if "code" not in error or "message" not in error:
        return ValidationResult(valid=False, errors=['DealError.error must have "code" and "message"'])
    return ValidationResult(valid=True, errors=[])


def validate_deal_intent_ack(data: Any) -> bool:
    """Validate a DealIntentAck message."""
    return validate_deal_intent_ack_result(data).valid


def validate_deal_intent_ack_result(data: Any) -> ValidationResult:
    """Validate a DealIntentAck message with detailed results."""
    base = _validate_base(data)
    if not base.valid:
        return base
    if not isinstance(data.get("ack"), dict):
        return ValidationResult(valid=False, errors=['Missing or invalid "ack" field'])
    return ValidationResult(valid=True, errors=[])
