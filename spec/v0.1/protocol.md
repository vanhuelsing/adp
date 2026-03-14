# ADP Specification v0.1.1

**Version:** 0.1.1-draft  
**Status:** Draft  
**Author/Publisher:** vanhuelsing (https://github.com/vanhuelsing)  
**Contact:** adp@apideals.ai  
**License:** CC-BY 4.0 (spec) / Apache 2.0 (code)  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Core Messages](#2-core-messages)
3. [Pricing Schema](#3-pricing-schema)
4. [Compliance & Capabilities](#4-compliance--capabilities)
5. [Provider Discovery](#5-provider-discovery)
6. [Versioning](#6-versioning)
7. [Design Decisions](#7-design-decisions)

---

## 1. Overview

ADP (apideals Deal Protocol) is a JSON-based message protocol enabling software agents to request, compare, and signal intent for LLM API deals without human interaction.

### Scope

**Included in v0.1:**
- Four message types: `DealRequest`, `DealOffer`, `DealIntent`, `DealError`
- Token-based pricing schema ($/MTok)
- Compliance and capability vocabularies
- Provider discovery via `/.well-known/adp.json`

**Not in v0.1 (addressed in later versions):**
- Transport layer (HTTP, WebSocket) — transport-agnostic → **[v0.2.0: HTTP Binding](../v0.2/http-binding.md)**
- Authentication/authorization → **[v0.2.0: Auth & Security](../v0.2/auth.md)**
- Multimodal pricing (images, audio, video) → **[v0.2.0: Multimodal Pricing](../v0.2/pricing-multimodal.md)**
- Payment/billing — v0.3

### Design Principles

| Principle | Description |
|-----------|-------------|
| **Simplicity** | Implement in an afternoon |
| **JSON-native** | No XML, no Protobuf |
| **Additive evolution** | New fields = OK; removed fields = breaking change |
| **Agent-readable** | Clear semantics, no free text for structured data |
| **Human-debuggable** | Readable JSON, inspectable in browser |

---

## 2. Core Messages

### 2.1 Common Header

Every ADP message starts with this header:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest | DealOffer | DealIntent | DealError",
    "id": "uuid-v4",
    "timestamp": "2026-03-10T12:00:00Z",
    "correlation_id": "uuid-v4 | null"
  }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | `string` | ✅ | Protocol version (semver) |
| `type` | `enum` | ✅ | Message type |
| `id` | `string` (UUID v4) | ✅ | Unique message ID |
| `timestamp` | `string` (ISO 8601 UTC) | ✅ | Creation time, always UTC |
| `correlation_id` | `string` (UUID v4) | ⚠️ | References triggering message. **Required** for `DealOffer`, `DealIntent`, `DealError`. Optional (null) for `DealRequest` only. |

### 2.2 DealRequest

Agent asks: *"I need an LLM API with these requirements."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-10T12:00:00Z",
    "correlation_id": null
  },
  "request": {
    "requester": {
      "agent_id": "agent:acme:bot",
      "is_automated": true,
      "name": "Acme Procurement Bot",
      "contact": { "email": "api@acme.com" }
    },
    "requirements": {
      "task_classes": ["reasoning", "coding"],
      "min_context_window": 200000,
      "min_output_tokens": 8000,
      "modalities": ["text"],
      "capabilities": ["tool_use", "structured_output"],
      "compliance": ["gdpr", "eu_hosting"],
      "max_latency_ms": { "ttft": 2000, "tps": 50 }
    },
    "volume": {
      "estimated_monthly_input_tokens": 50000000,
      "estimated_monthly_output_tokens": 10000000,
      "pattern": "steady",
      "batch_eligible": true
    },
    "budget": {
      "max_cost_per_mtok_input": 5.00,
      "max_cost_per_mtok_output": 15.00,
      "currency": "USD",
      "max_monthly_spend": 500.00
    },
    "preferences": {
      "commitment": "none",
      "preferred_providers": [],
      "excluded_providers": [],
      "deal_type": "pay_as_you_go"
    },
    "valid_until": "2026-03-17T12:00:00Z",
    "request_ttl_hours": 24
  }
}
```

**Field Reference:**

| Path | Type | Required | Description |
|------|------|----------|-------------|
| `requester.agent_id` | `string` | ✅ | Unique agent identifier (URN-style recommended) |
| `requester.is_automated` | `boolean` | ✅ | `true` for autonomous AI agents (EU AI Act Art. 50) |
| `requester.name` | `string` | ❌ | Human-readable name |
| `requester.contact.email` | `string` | ❌ | Contact email |
| `requirements.task_classes` | `array<enum>` | ❌ | `general`, `reasoning`, `coding`, `creative`, `classification`, `extraction`, `embedding`, `multimodal` |
| `requirements.compliance` | `array<enum>` | ❌ | See [Compliance](#4-compliance--capabilities) |
| `budget.currency` | `string` (ISO 4217) | ✅ | `USD`, `EUR`, etc. |
| `valid_until` | `string` (ISO 8601) | ❌ | Request expiration time |
| `request_ttl_hours` | `integer` | ❌ | Data retention limit (GDPR Art. 17), default 24 |

### 2.3 DealOffer

Provider responds: *"I offer these conditions."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "timestamp": "2026-03-10T12:00:05Z",
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  },
  "offer": {
    "provider": {
      "provider_id": "google",
      "name": "Google Cloud — Vertex AI",
      "url": "https://cloud.google.com/vertex-ai",
      "contact": { "email": "cloud-sales@google.com" }
    },
    "model": {
      "model_id": "gemini-pro",
      "name": "Gemini Pro",
      "task_classes": ["general", "reasoning", "coding"],
      "context_window": 1000000,
      "max_output_tokens": 8192,
      "modalities": ["text"],
      "capabilities": ["tool_use", "streaming"],
      "ai_act_risk_class": "minimal"
    },
    "pricing": { /* See Section 3 */ },
    "compliance": {
      "compliance_verified_by": "self-declared",
      "certifications": ["soc2", "iso27001"],
      "data_regions": ["US", "EU"],
      "gdpr_compliant": true,
      "dpa_available": true,
      "data_retention_days": 30,
      "training_on_data": false
    },
    "sla": {
      "uptime_pct": 99.9,
      "ttft_p50_ms": 400,
      "ttft_p99_ms": 2000,
      "tps_median": 120
    },
    "valid_from": "2026-03-10T00:00:00Z",
    "valid_until": "2026-04-10T00:00:00Z",
    "terms_url": "https://cloud.google.com/terms"
  }
}
```

**Required Fields:**

| Path | Description |
|------|-------------|
| `offer.provider.provider_id` | Unique provider ID (lowercase, slug) |
| `offer.provider.name` | Human-readable provider name |
| `offer.model.model_id` | Unique model ID |
| `offer.model.task_classes` | Supported task classes (array, non-empty) |
| `offer.model.context_window` | Max context in tokens |
| `offer.model.max_output_tokens` | Max output per request |
| `offer.model.modalities` | Supported modalities (array, non-empty) |
| `offer.model.capabilities` | Supported capabilities (array, may be empty) |
| `offer.pricing.currency` | ISO 4217 currency code |
| `offer.pricing.base.input_per_mtok` | Base price per 1M input tokens |
| `offer.pricing.base.output_per_mtok` | Base price per 1M output tokens |
| `offer.compliance.compliance_verified_by` | `self-declared`, `third-party`, or `apideals-verified` |
| `offer.valid_from` | Offer validity start |
| `offer.valid_until` | Offer validity end (must be after `valid_from`) |

### 2.4 DealIntent

> **Legal Note:** `DealIntent` is explicitly non-binding (`binding: false`). The actual contract is formed at the provider's signup flow. Consult legal counsel for your jurisdiction.

Agent signals: *"I intend to accept this offer."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealIntent",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-10T12:00:10Z",
    "correlation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  },
  "intent": {
    "binding": false,
    "requires_human_confirmation": true,
    "party_type": "business",
    "requester": { "agent_id": "agent:acme:bot", "is_automated": true },
    "accepted_offer_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "accepted_pricing_snapshot": {
      "input_per_mtok": 3.00,
      "output_per_mtok": 15.00,
      "modifiers_applied": ["batch"]
    },
    "volume_commitment": {
      "estimated_monthly_input_tokens": 50000000,
      "estimated_monthly_output_tokens": 10000000,
      "commitment_type": "soft"
    },
    "activation": {
      "type": "redirect",
      "redirect_url": "https://cloud.google.com/signup?deal=xyz"
    }
  }
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `intent.binding` | ✅ | Always `false` in v0.1 |
| `intent.requires_human_confirmation` | ❌ | Default: `true` |
| `intent.party_type` | ❌ | `business` or `consumer` |
| `intent.accepted_offer_id` | ✅ | UUID of the accepted DealOffer |
| `intent.activation.type` | ✅ | `redirect`, `api_provision` (v0.2+), or `manual` |
| `intent.activation.redirect_url` | ⚠️ | Required if `activation.type === "redirect"` |

### 2.5 DealError

Error response when a message cannot be processed.

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealError",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-10T12:00:01Z",
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  },
  "error": {
    "code": "INVALID_REQUEST",
    "message": "task_classes contains unknown value",
    "field_errors": [
      {
        "field": "requirements.task_classes[0]",
        "code": "INVALID_ENUM",
        "message": "Expected: general, reasoning, coding, ..."
      }
    ],
    "retryable": false,
    "retry_after_ms": null
  }
}
```

**Error Codes:**

| Code | Description | Retryable |
|------|-------------|-----------|
| `INVALID_REQUEST` | Malformed request | No |
| `VERSION_MISMATCH` | Unsupported protocol version | No |
| `EXPIRED` | Request or offer expired | No |
| `NOT_FOUND` | Referenced resource not found | No |
| `RATE_LIMITED` | Too many requests | Yes |
| `PROVIDER_UNAVAILABLE` | Provider temporarily down | Yes |

---

## 3. Pricing Schema

All prices in **$/MTok** (dollars per 1 million tokens).

### 3.1 Complete Pricing Object

```json
{
  "pricing": {
    "currency": "USD",
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 12.00
    },
    "tiers": [
      {
        "threshold_mtok_monthly": 100,
        "input_per_mtok": 1.80,
        "output_per_mtok": 10.80
      }
    ],
    "modifiers": [
      {
        "type": "batch",
        "discount_pct": 50,
        "conditions": "Async processing, 24h SLA"
      },
      {
        "type": "cache_read",
        "input_per_mtok": 0.50,
        "conditions": "Min 1024 token cache prefix"
      }
    ],
    "free_tier": {
      "monthly_input_tokens": 1000000,
      "monthly_output_tokens": 200000,
      "rate_limit_rpm": 10
    },
    "commitment_deals": [
      {
        "type": "annual_prepaid",
        "discount_pct": 20,
        "min_monthly_spend": 1000.00,
        "duration_months": 12
      }
    ]
  }
}
```

### 3.2 Pricing Fields

| Field | Type | Description |
|-------|------|-------------|
| `base.input_per_mtok` | `number` | Base price per 1M input tokens |
| `base.output_per_mtok` | `number` | Base price per 1M output tokens |
| `tiers[].threshold_mtok_monthly` | `number` | Volume threshold in MTok/month |
| `tiers[].input_per_mtok` | `number` | Tier price (flat-rate, not marginal) |
| `modifiers[].type` | `enum` | `batch`, `cache_read`, `cache_write`, `long_context`, `fine_tuned`, `custom` |
| `modifiers[].discount_pct` | `number` | Percentage discount (XOR with absolute price) |
| `modifiers[].input_per_mtok` | `number` | Absolute price override (XOR with discount) |

> **Flat-Rate Tier Logic:** When volume exceeds a tier threshold, the tier price applies to **all** tokens — not just those above the threshold. Example: 101 MTok at $1.80 = $181.80 (cheaper than 99 MTok at $2.00 = $198.00).

### 3.3 Price Calculation

```python
# Modifier types that affect only input price (not output)
INPUT_ONLY_MODIFIERS = {"cache_read", "cache_write"}

def calculate_cost(input_mtok, output_mtok, pricing):
    # Step 1: Determine tier (flat-rate).
    # When total volume exceeds a threshold, the tier price applies to ALL tokens.
    # Iterate sorted tiers — last matching tier wins (highest threshold exceeded).
    input_price = pricing["base"]["input_per_mtok"]
    output_price = pricing["base"]["output_per_mtok"]

    total_mtok = input_mtok + output_mtok
    for tier in sorted(pricing.get("tiers", []),
                       key=lambda t: t["threshold_mtok_monthly"]):
        if total_mtok > tier["threshold_mtok_monthly"]:
            input_price = tier["input_per_mtok"]
            output_price = tier.get("output_per_mtok", output_price)

    # Step 2: Apply modifiers in declaration order.
    # Modifiers of type cache_read / cache_write affect input_price only.
    for modifier in pricing.get("modifiers", []):
        modifier_type = modifier.get("type", "")
        input_only = modifier_type in INPUT_ONLY_MODIFIERS

        if "discount_pct" in modifier:
            factor = 1 - modifier["discount_pct"] / 100
            input_price *= factor
            if not input_only:
                output_price *= factor
        elif "input_per_mtok" in modifier:
            input_price = modifier["input_per_mtok"]
            if not input_only and "output_per_mtok" in modifier:
                output_price = modifier["output_per_mtok"]

    return (input_mtok * input_price) + (output_mtok * output_price)
```

---

## 4. Compliance & Capabilities

### 4.1 Compliance Tags

| Tag | Meaning |
|-----|---------|
| `gdpr` | GDPR-compliant with DPA available |
| `eu_hosting` | Data stored/processed in EU/EWR |
| `eu_company` | Provider incorporated in EU/EWR |
| `soc2` | SOC 2 Type II certified |
| `iso27001` | ISO 27001 certified |
| `hipaa` | HIPAA-compliant |
| `baa_available` | Business Associate Agreement available |
| `fedramp` | FedRAMP authorized |
| `no_training` | Customer data not used for training |
| `zero_retention` | No retention of prompts/responses |
| `on_premise` | On-premise deployment available |
| `data_residency_de` | Data stays in Germany |
| `data_residency_eu` | Data stays in EU/EWR |
| `pci_dss` | PCI DSS Level 1 compliant |

> ⚠️ **Self-Declared Compliance:** Tags with `compliance_verified_by: "self-declared"` are provider assertions. Verify independently for your use case.

### 4.2 Capabilities

| Capability | Description |
|------------|-------------|
| `tool_use` | Can call external tools/functions |
| `structured_output` | Outputs conform to JSON schema |
| `function_calling` | OpenAI-compatible function calling |
| `streaming` | Server-Sent Events streaming |
| `batch_api` | Async batch processing |
| `prompt_caching` | Prompt prefix caching |
| `fine_tuning` | Model fine-tuning available |
| `vision` | Image input processing |
| `audio_input` | Audio input processing |
| `audio_output` | Audio/speech generation |
| `web_search` | Built-in web search |
| `code_execution` | Sandboxed code execution |

---

## 5. Provider Discovery

Providers announce ADP support via a static JSON file:

```
https://<provider-domain>/.well-known/adp.json
```

### Minimal Format

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.provider.com/adp/offers"
}
```

### Full Format

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.provider.com/adp/offers",
  "models_endpoint": "https://api.provider.com/adp/models",
  "static_offers_url": "https://provider.com/adp/offers.json",
  "contact": {
    "email": "api@provider.com",
    "support_url": "https://provider.com/docs"
  },
  "provider_id": "provider",
  "provider_name": "Provider AI",
  "last_updated": "2026-03-10T00:00:00Z"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `adp_supported` | ✅ | Always `true` |
| `adp_versions` | ✅ | Supported ADP versions |
| `offer_endpoint` | ⚠️ | POST endpoint for DealRequests. **Required** unless `static_offers_url` is provided. |
| `models_endpoint` | ❌ | GET endpoint for all offers |
| `static_offers_url` | ⚠️ | Static JSON with all offers. May substitute `offer_endpoint` for read-only/price-list providers. |

> **Discovery Rule:** A valid ADP provider MUST expose at least one of `offer_endpoint` (for live requests) or `static_offers_url` (for static price lists). Providers that expose neither are non-conforming.

---

## 6. Versioning

ADP follows [Semantic Versioning 2.0](https://semver.org/):

| Change Type | Version Impact | Example |
|-------------|----------------|---------|
| Breaking (field removal, semantic change) | MAJOR | `0.x` → `1.0` |
| New optional fields, new enum values | MINOR | `0.1` → `0.2` |
| Clarifications, bug fixes | PATCH | `0.1.0` → `0.1.1` |

### Roadmap

| Version | Content | Status |
|---------|---------|--------|
| **v0.1.1** | Core Messages, Pricing, Discovery, Compliance | ✅ Released |
| **[v0.2.0](../v0.2/README.md)** | Auth, HTTP Binding, Multimodal Pricing, DealIntentAck | 📝 Draft |
| **v0.3.0** | Counter-Offers, DealConfirm, Usage-Reporting, Pagination | Planned |
| **v1.0.0** | Payment-Escrow, Community Governance, Formal JSON Schemas | Planned |

### Pre-1.0 Disclaimer

During `0.x`, breaking changes may occur between minor versions. The protocol is experimental. Post-1.0, semver rules apply strictly.

### Version Negotiation

Negotiation happens via the `adp.version` header:

1. Agent sends `DealRequest` with `version: "0.1.1"`
2. Provider responds with their supported version
3. Unknown fields are ignored (Postel's Law)
4. If major version mismatches, provider responds with `DealError` (`code: "VERSION_MISMATCH"`)

---

## 7. Design Decisions

### Why `DealIntent` instead of `DealAccept`?

`DealAccept` could be interpreted as a binding contract acceptance under German law (§§ 145–147 BGB). `DealIntent` with `binding: false` explicitly signals non-binding interest, directing the actual contract formation to the provider's signup flow.

### Why flat-rate tiers?

All major LLM providers use flat-rate (not marginal) tier pricing. When you exceed a tier threshold, the lower price applies to all tokens. Simpler to calculate and matches market reality.

### Why transport-agnostic?

ADP v0.1 defines message formats only. Providers can use HTTP, WebSocket, message queues, or even static files. **→ HTTP binding is now specified in [v0.2.0](../v0.2/http-binding.md).**

### Why $/MTok only?

The LLM API market has converged on $/MTok as the standard unit. Using one unit eliminates conversion errors. **→ Non-token pricing (images, audio, video) is now specified in [v0.2.0](../v0.2/pricing-multimodal.md).**

### Why dual licensing?

CC-BY 4.0 for specifications (better for standards/docs), Apache 2.0 for code/SDKs. Follows the pattern of W3C and IETF standards.

---

## 8. Security Considerations

ADP v0.1.1 ist bewusst transport-agnostisch und enthält keine integrierte Authentifizierung, Autorisierung oder kryptographische Signaturen. Diese Designentscheidung ermöglicht eine schnelle Implementierung, erfordert aber zusätzliche Sicherheitsmaßnahmen auf Transportschicht.

### Kritische Bedrohungen

Die wichtigsten Risiken in v0.1 sind **Provider Impersonation** (gefälschte Angebote mit Phishing-URLs), **Replay-Attacken** (Wiederverwendung gültiger Nachrichten) und **Man-in-the-Middle-Angriffe** bei unsicherem Transport. Ohne Signaturen können Angebotspreise, Redirect-URLs und Compliance-Behauptungen manipuliert werden.

### Empfohlene Gegenmaßnahmen

Bis v0.2 mit integrierten Sicherheitsmechanismen verfügbar ist, müssen Implementierer:

- **TLS 1.3** für alle Kommunikationswege erzwingen
- **API-Keys** außerhalb des ADP-JSON-Schemas implementieren (HTTP-Header)
- **Rate Limiting** auf Basis von `DealError` mit `code: "RATE_LIMITED"` etablieren
- **JSON-Schema-Validierung** mit strikten Payload-Limits (max. 250 KB für `DealOffer`)
- **URL-Validierung** (nur HTTPS, keine private IPs) für alle `redirect_url` und `terms_url`
- **Data Retention** gemäß `request_ttl_hours` für GDPR-Konformität implementieren

Ausführliche Sicherheitsrichtlinien, Threat Model und Empfehlungen für v0.2 (JWS-Signaturen, Nonces, Certificate Pinning) finden sich in [`docs/security-considerations.md`](../../docs/security-considerations.md).

---

*End of Specification v0.1.1*
