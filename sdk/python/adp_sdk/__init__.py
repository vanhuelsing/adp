"""adp-sdk — Python SDK for the Agent Deal Protocol (ADP) v0.2."""

from .client import ADPClient, AsyncADPClient
from .exceptions import ADPConnectionError, ADPError, ADPHTTPError, ADPValidationError
from .models import (
    # Scalar type aliases
    Capability,
    Certification,
    ComplianceTag,
    Modality,
    TaskClass,
    # Shared
    ADPHeader,
    Budget,
    Contact,
    MaxLatencyMs,
    Preferences,
    Requirements,
    Volume,
    # DealRequest
    DealRequest,
    DealRequestBody,
    Requester,
    # DealOffer
    Compliance,
    CommitmentDeal,
    DealOffer,
    DealOfferBody,
    FreeTier,
    Model,
    Pricing,
    PricingBase,
    PricingModifier,
    PricingTier,
    Provider,
    SLA,
    # DealIntent
    Activation,
    DealIntent,
    DealIntentBody,
    PricingSnapshot,
    VolumeCommitment,
    # DealIntentAck
    Acknowledgment,
    DealIntentAck,
    # DealError
    DealError,
    DealErrorBody,
    FieldError,
    # Discovery
    WellKnownADP,
    # Union
    ADPMessage,
)
from .validator import (
    ValidationResult,
    validate_deal_intent,
    validate_deal_intent_result,
    validate_deal_offer,
    validate_deal_offer_result,
    validate_deal_request,
    validate_deal_request_result,
)

__version__ = "0.2.0"

__all__ = [
    "__version__",
    # Clients
    "ADPClient",
    "AsyncADPClient",
    # Exceptions
    "ADPError",
    "ADPValidationError",
    "ADPConnectionError",
    "ADPHTTPError",
    # Scalar aliases
    "TaskClass",
    "Modality",
    "Capability",
    "ComplianceTag",
    "Certification",
    # Shared models
    "ADPHeader",
    "Contact",
    "Requester",
    "MaxLatencyMs",
    "Requirements",
    "Volume",
    "Budget",
    "Preferences",
    # DealRequest
    "DealRequestBody",
    "DealRequest",
    # DealOffer
    "Provider",
    "Model",
    "PricingBase",
    "PricingTier",
    "PricingModifier",
    "FreeTier",
    "CommitmentDeal",
    "Pricing",
    "Compliance",
    "SLA",
    "DealOfferBody",
    "DealOffer",
    # DealIntent
    "PricingSnapshot",
    "VolumeCommitment",
    "Activation",
    "DealIntentBody",
    "DealIntent",
    # DealIntentAck
    "Acknowledgment",
    "DealIntentAck",
    # DealError
    "FieldError",
    "DealErrorBody",
    "DealError",
    # Discovery
    "WellKnownADP",
    # Union
    "ADPMessage",
    # Validators
    "ValidationResult",
    "validate_deal_request",
    "validate_deal_offer",
    "validate_deal_intent",
    "validate_deal_request_result",
    "validate_deal_offer_result",
    "validate_deal_intent_result",
]
