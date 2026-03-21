"""Pydantic v2 models for the Agent Deal Protocol (ADP) v0.2."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Optional, Union

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Scalar type aliases
# ---------------------------------------------------------------------------

TaskClass = Literal[
    "general",
    "reasoning",
    "coding",
    "creative",
    "classification",
    "extraction",
    "embedding",
    "multimodal",
]

Modality = Literal[
    "text",
    "image_input",
    "image_output",
    "audio_input",
    "audio_output",
    "video_input",
]

Capability = Literal[
    "tool_use",
    "structured_output",
    "function_calling",
    "streaming",
    "batch_api",
    "prompt_caching",
    "fine_tuning",
    "vision",
    "audio_input",
    "audio_output",
    "web_search",
    "code_execution",
]

ComplianceTag = Literal[
    "gdpr",
    "eu_hosting",
    "eu_company",
    "soc2",
    "iso27001",
    "hipaa",
    "baa_available",
    "fedramp",
    "no_training",
    "zero_retention",
    "on_premise",
    "data_residency_de",
    "data_residency_eu",
    "pci_dss",
]

Certification = Literal["soc2", "iso27001", "hipaa", "fedramp"]

ADPMessageType = Literal[
    "DealRequest", "DealOffer", "DealIntent", "DealError", "DealIntentAck"
]

# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class ADPHeader(BaseModel):
    """Protocol envelope present in every ADP message."""

    version: str
    type: str  # broad str to accommodate DealIntentAck and future types
    id: str
    timestamp: str
    correlation_id: Optional[str] = None


class Contact(BaseModel):
    """Contact information for a requester or provider."""

    email: Optional[str] = None
    webhook_url: Optional[str] = None
    support_url: Optional[str] = None


class Requester(BaseModel):
    """Identifies the requesting agent."""

    agent_id: str
    is_automated: bool
    name: Optional[str] = None
    contact: Optional[Contact] = None


class MaxLatencyMs(BaseModel):
    """Per-metric latency budget."""

    ttft: Optional[int] = None  # time-to-first-token, ms
    tps: Optional[int] = None   # tokens-per-second threshold


class Requirements(BaseModel):
    """Model capability requirements expressed by the requester."""

    task_classes: Optional[list[TaskClass]] = None
    min_context_window: Optional[int] = None
    min_output_tokens: Optional[int] = None
    modalities: Optional[list[Modality]] = None
    capabilities: Optional[list[Capability]] = None
    compliance: Optional[list[ComplianceTag]] = None
    max_latency_ms: Optional[MaxLatencyMs] = None


class Volume(BaseModel):
    """Estimated usage volume from the requester."""

    estimated_monthly_input_tokens: Optional[int] = None
    estimated_monthly_output_tokens: Optional[int] = None
    pattern: Optional[Literal["steady", "bursty", "batch"]] = None
    batch_eligible: Optional[bool] = None


class Budget(BaseModel):
    """Price ceiling from the requester's perspective."""

    max_cost_per_mtok_input: Optional[float] = None
    max_cost_per_mtok_output: Optional[float] = None
    currency: str
    max_monthly_spend: Optional[float] = None


class Preferences(BaseModel):
    """Requester preferences for the deal."""

    commitment: Optional[Literal["none", "soft", "hard"]] = None
    preferred_providers: Optional[list[str]] = None
    excluded_providers: Optional[list[str]] = None
    deal_type: Optional[Literal["pay_as_you_go", "commitment", "batch_only"]] = None


# ---------------------------------------------------------------------------
# DealRequest
# ---------------------------------------------------------------------------


class DealRequestBody(BaseModel):
    """The payload of a DealRequest message."""

    requester: Requester
    requirements: Optional[Requirements] = None
    volume: Optional[Volume] = None
    budget: Optional[Budget] = None
    preferences: Optional[Preferences] = None
    valid_until: Optional[str] = None
    request_ttl_hours: Optional[int] = None


class DealRequest(BaseModel):
    """An ADP DealRequest — sent by agents to solicit offers from providers."""

    adp: ADPHeader
    request: DealRequestBody


# ---------------------------------------------------------------------------
# DealOffer
# ---------------------------------------------------------------------------


class Provider(BaseModel):
    """Identifies an LLM provider."""

    provider_id: str
    name: str
    url: Optional[str] = None
    contact: Optional[Contact] = None


class Model(BaseModel):
    """Describes an LLM model offered by a provider."""

    model_id: str
    name: str
    version: Optional[str] = None
    task_classes: list[TaskClass]
    context_window: int
    max_output_tokens: int
    modalities: list[Modality]
    capabilities: list[Capability]
    knowledge_cutoff: Optional[str] = None
    ai_act_risk_class: Optional[Literal["minimal", "limited", "high", "unacceptable"]] = None
    gpai_model_card_url: Optional[str] = None
    prohibited_uses: Optional[list[str]] = None


class PricingBase(BaseModel):
    """Base per-token pricing."""

    input_per_mtok: float
    output_per_mtok: float


class PricingTier(BaseModel):
    """Volume-based pricing tier."""

    threshold_mtok_monthly: float
    input_per_mtok: float
    output_per_mtok: float


class PricingModifier(BaseModel):
    """Discount or surcharge modifier applied on top of base pricing."""

    type: Literal["batch", "cache_read", "cache_write", "long_context", "fine_tuned", "custom"]
    discount_pct: Optional[float] = None
    input_per_mtok: Optional[float] = None
    output_per_mtok: Optional[float] = None
    threshold_tokens: Optional[int] = None
    conditions: Optional[str] = None


class FreeTier(BaseModel):
    """Free-tier allowance for a model."""

    monthly_input_tokens: Optional[int] = None
    monthly_output_tokens: Optional[int] = None
    rate_limit_rpm: Optional[int] = None
    valid_until: Optional[str] = None
    notes: Optional[str] = None


class CommitmentDeal(BaseModel):
    """Discount offered in exchange for a volume or time commitment."""

    type: Literal["annual_prepaid", "monthly_commitment", "sustained_use"]
    discount_pct: float
    min_monthly_spend: Optional[float] = None
    duration_months: Optional[int] = None
    conditions: Optional[str] = None


class Pricing(BaseModel):
    """Full pricing structure for a model, including tiers and modifiers.

    The ``modalities`` field carries per-modality pricing defined by the
    ADP multimodal pricing extension (spec-v02/pricing-multimodal.md).
    """

    model_config = ConfigDict(extra="allow")

    currency: str
    base: PricingBase
    tiers: Optional[list[PricingTier]] = None
    modifiers: Optional[list[PricingModifier]] = None
    free_tier: Optional[FreeTier] = None
    commitment_deals: Optional[list[CommitmentDeal]] = None
    # Multimodal extension: per-modality pricing details
    modalities: Optional[dict[str, Any]] = None


class Compliance(BaseModel):
    """Data governance and compliance information for a provider."""

    compliance_verified_by: Literal["self-declared", "third-party", "apideals-verified"]
    certifications: Optional[list[Certification]] = None
    data_regions: Optional[list[str]] = None
    gdpr_compliant: Optional[bool] = None
    dpa_available: Optional[bool] = None
    data_retention_days: Optional[int] = None
    training_on_data: Optional[bool] = None
    privacy_policy_url: Optional[str] = None
    subprocessors_url: Optional[str] = None


class SLA(BaseModel):
    """Service-level agreement metrics."""

    uptime_pct: Optional[float] = None
    ttft_p50_ms: Optional[int] = None
    ttft_p99_ms: Optional[int] = None
    tps_median: Optional[float] = None


class DealOfferBody(BaseModel):
    """The payload of a DealOffer message."""

    provider: Provider
    model: Model
    pricing: Pricing
    compliance: Compliance
    sla: Optional[SLA] = None
    valid_from: str
    valid_until: str
    terms_url: Optional[str] = None


class DealOffer(BaseModel):
    """An ADP DealOffer — returned by a provider in response to a DealRequest."""

    adp: ADPHeader
    offer: DealOfferBody


# ---------------------------------------------------------------------------
# DealIntent
# ---------------------------------------------------------------------------


class PricingSnapshot(BaseModel):
    """A locked snapshot of accepted pricing."""

    input_per_mtok: float
    output_per_mtok: float
    modifiers_applied: Optional[list[str]] = None


class VolumeCommitment(BaseModel):
    """Volume commitment signalled by the requester."""

    estimated_monthly_input_tokens: Optional[int] = None
    estimated_monthly_output_tokens: Optional[int] = None
    commitment_type: Optional[Literal["none", "soft", "hard"]] = None
    commitment_duration_months: Optional[int] = None


class Activation(BaseModel):
    """How the deal should be activated."""

    type: Literal["redirect", "api_provision", "manual"]
    redirect_url: Optional[str] = None


class DealIntentBody(BaseModel):
    """The payload of a DealIntent message.

    Per the ADP v0.2 spec, all intents are non-binding (``binding=False``).
    """

    binding: Literal[False]
    requires_human_confirmation: Optional[bool] = None
    party_type: Optional[Literal["business", "consumer"]] = None
    requester: Requester
    accepted_offer_id: str
    accepted_pricing_snapshot: PricingSnapshot
    volume_commitment: Optional[VolumeCommitment] = None
    activation: Activation
    notes: Optional[str] = None


class DealIntent(BaseModel):
    """An ADP DealIntent — signals the requester's intent to accept an offer."""

    adp: ADPHeader
    intent: DealIntentBody


# ---------------------------------------------------------------------------
# DealIntentAck
# ---------------------------------------------------------------------------


class Acknowledgment(BaseModel):
    """Acknowledgment details returned by the provider."""

    status: Literal["received", "processing", "confirmed"]
    next_steps: Optional[str] = None
    reference_id: Optional[str] = None
    expires_at: Optional[str] = None


class DealIntentAck(BaseModel):
    """An ADP DealIntentAck — provider acknowledgment of a received DealIntent."""

    adp: ADPHeader
    acknowledgment: Acknowledgment


# ---------------------------------------------------------------------------
# DealError
# ---------------------------------------------------------------------------


class FieldError(BaseModel):
    """Validation error for a specific request field."""

    field: str
    code: str
    message: str


class DealErrorBody(BaseModel):
    """The payload of a DealError message."""

    code: Literal[
        "INVALID_REQUEST",
        "PROVIDER_UNAVAILABLE",
        "EXPIRED",
        "VERSION_MISMATCH",
        "RATE_LIMITED",
        "NOT_FOUND",
    ]
    message: str
    field_errors: Optional[list[FieldError]] = None
    retryable: bool
    retry_after_ms: Optional[int] = None


class DealError(BaseModel):
    """An ADP DealError — returned by a provider when the request cannot be fulfilled."""

    adp: ADPHeader
    error: DealErrorBody


# ---------------------------------------------------------------------------
# Discovery (/.well-known/adp.json)
# ---------------------------------------------------------------------------


class ApiKeyAuth(BaseModel):
    """API key authentication configuration."""

    format: Optional[str] = None
    header: Optional[str] = None


class OAuth2Scopes(BaseModel):
    """OAuth 2.0 authentication configuration."""

    token_endpoint: Optional[str] = None
    authorization_endpoint: Optional[str] = None
    scopes_supported: Optional[list[str]] = None
    grant_types_supported: Optional[list[str]] = None


class RequestSigning(BaseModel):
    """HMAC request-signing configuration."""

    supported: Optional[bool] = None
    algorithm: Optional[str] = None


class DiscoveryAuth(BaseModel):
    """Authentication methods advertised in the discovery document."""

    methods: Optional[list[Literal["api_key", "oauth2", "request_signing"]]] = None
    api_key: Optional[ApiKeyAuth] = None
    oauth2: Optional[OAuth2Scopes] = None
    request_signing: Optional[RequestSigning] = None


class RateLimiting(BaseModel):
    """Rate-limit configuration in the discovery document."""

    requests_per_minute: Optional[int] = None
    burst_allowance: Optional[int] = None


class DiscoveryContact(BaseModel):
    """Contact information in the discovery document."""

    email: Optional[str] = None


class WellKnownADP(BaseModel):
    """Response body of ``GET /.well-known/adp.json``."""

    adp_supported: bool
    adp_versions: list[str]
    discovery_version: Optional[str] = None
    offer_endpoint: Optional[str] = None
    intent_endpoint: Optional[str] = None
    models_endpoint: Optional[str] = None
    static_offers_url: Optional[str] = None
    auth: Optional[DiscoveryAuth] = None
    rate_limiting: Optional[RateLimiting] = None
    contact: Optional[DiscoveryContact] = None
    last_updated: Optional[str] = None


# ---------------------------------------------------------------------------
# Union type
# ---------------------------------------------------------------------------

ADPMessage = Union[DealRequest, DealOffer, DealIntent, DealError, DealIntentAck]

__all__ = [
    # Scalar aliases
    "ADPMessageType",
    "TaskClass",
    "Modality",
    "Capability",
    "ComplianceTag",
    "Certification",
    # Shared
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
    "ApiKeyAuth",
    "OAuth2Scopes",
    "RequestSigning",
    "DiscoveryAuth",
    "RateLimiting",
    "DiscoveryContact",
    "WellKnownADP",
    # Union
    "ADPMessage",
]
