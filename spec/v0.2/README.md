# ADP v0.2.0 Specification

**Version:** 0.2.0-draft  
**Release Date:** 2026-03-12  
**Status:** Draft

## Overview

ADP v0.2.0 introduces a complete HTTP binding and authentication layer, along with multimodal pricing support for images, audio, and video. This release standardizes how agents interact with providers over HTTP/HTTPS and secures those interactions.

### What's New in v0.2.0

| Feature | Status | Documentation |
|---------|--------|---|
| **Authentication Layer** | ✅ New | `auth.md` |
| **HTTP Binding** | ✅ New | `http-binding.md` |
| **Multimodal Pricing** | ✅ New | `pricing-multimodal.md` |
| **DealIntentAck** | ✅ New | `http-binding.md` (Section 2.5) |
| **Error Code Registry** | ✅ New | `http-binding.md` (Section 3) |
| **Rate Limiting** | ✅ New | `auth.md` (Section 3) |
| **Idempotency** | ✅ New | `auth.md` (Section 4) |

## File Index

### Specifications

- **`auth.md`** — Authentication & Security
  - API Key, OAuth 2.0, Request Signing
  - Rate Limiting Headers
  - Idempotency Key
  - Provider Discovery Extensions

- **`http-binding.md`** — HTTP Transport Layer
  - Endpoints: Discovery, Offer, Intent, Health
  - Standard Headers and Content-Type
  - Error Response Format
  - OpenAPI 3.1 Specification
  - Central Error Code Registry

- **`pricing-multimodal.md`** — Pricing for Multimodal Models
  - Image Input/Output Pricing
  - Audio Input/Output Pricing
  - Video Input Pricing
  - Token Equivalents
  - Bundle Pricing
  - Calculation Pipeline

### Schemas (JSON Schema 2020-12)

- `auth-header.schema.json` — Authentication header formats
- `rate-limit.schema.json` — Rate limit response headers
- `pricing-multimodal.schema.json` — Multimodal pricing schema
- `deal-intent-ack.schema.json` — DealIntentAck message format
- `discovery-v0.2.schema.json` — Discovery endpoint schema (v0.2 extended)

### Examples (Valid JSON)

- `deal-request-multimodal.json` — DealRequest with text + images
- `deal-offer-vision.json` — DealOffer with GPT-4o Vision pricing
- `deal-offer-tts.json` — DealOffer with ElevenLabs TTS pricing
- `deal-intent-with-auth.json` — DealIntent with auth headers
- `deal-intent-ack.json` — DealIntentAck response
- `deal-error-unauthorized.json` — 401 Unauthorized error
- `deal-error-rate-limited.json` — 429 Rate Limited error
- `well-known-adp-v0.2.json` — Discovery endpoint response (v0.2)

## Migration from v0.1.1 → v0.2.0

### Breaking Changes

| Area | v0.1.1 | v0.2.0 | Impact |
|------|--------|--------|--------|
| **Authentication** | None defined | API Key / OAuth 2.0 required | All providers must implement auth |
| **HTTP Binding** | Not standardized | Complete HTTP spec | Follow Section 2 (Endpoints) |
| **Rate Limiting** | No standard | Standard headers required | Implement `X-ADP-RateLimit-*` headers |
| **Timestamps** | Various formats | ISO 8601 UTC only | Standardize all timestamps |
| **Error Codes** | Scattered | Central registry | Use codes from http-binding.md Section 3 |
| **DealIntentAck** | Not defined | New message type | Return `DealIntentAck` from `/adp/intent` |

### For Agent Developers

1. **Add Auth:** Use API Key or OAuth 2.0 token in `Authorization` header
2. **Update Endpoints:** Use standardized paths from `http-binding.md` Section 2
3. **Implement Retry Logic:** Honor `Retry-After` and `X-ADP-RateLimit-Reset` headers
4. **Error Handling:** Use error codes from `http-binding.md` Section 3
5. **Version Negotiation:** Check `discovery_version` in `.well-known/adp.json`

### For Provider Developers

1. **Implement Auth:** Support API Key and optionally OAuth 2.0
2. **Add HTTP Headers:** Return rate limit headers on authenticated endpoints
3. **Discovery Update:** Extend `.well-known/adp.json` with auth methods
4. **DealIntentAck:** Return `202 Accepted` with `DealIntentAck` from `/adp/intent`
5. **Timestamp Format:** Use ISO 8601 UTC for all timestamps
6. **Multimodal Pricing:** Add pricing schemas for any supported input/output modalities

## Schema Validation

All JSON files in the `schemas/` directory are valid JSON Schema 2020-12 documents. Validate DealRequest/DealOffer/DealIntent messages against the schemas before processing.

```bash
# Validate example using a JSON Schema validator
json-schema-validate schemas/pricing-multimodal.schema.json examples/deal-offer-vision.json
```

## Examples

All example JSON files in `examples/` are:

- ✅ Valid JSON (test with `python3 -m json.tool`)
- ✅ Using UUID v4 for IDs
- ✅ Using ISO 8601 UTC for timestamps
- ✅ Consistent with the specifications

Use these examples as templates for implementing v0.2.0.

## OpenAPI Specification

The complete OpenAPI 3.1.0 specification for the HTTP API is available in `http-binding.md` Section 8.

## Backwards Compatibility

v0.2.0 can coexist with v0.1.1:

- Providers may support both versions (check `discovery_version`)
- Use `X-ADP-Version` header to specify requested version
- v0.2.0 adds new fields; v0.1.1 fields remain valid

## Status

**Draft** — v0.2.0 is currently in draft status. Feedback is welcome. The specification will move to Release Candidate (RC) after community review.

## Questions?

Refer to the specifications:

- **Authentication?** → Read `auth.md`
- **HTTP Endpoints?** → Read `http-binding.md` Section 2
- **Pricing?** → Read `pricing-multimodal.md`
- **Errors?** → Read `http-binding.md` Section 3 (Error Code Registry)
- **Examples?** → Check `examples/` directory

---

**ADP Protocol** — Making AI procurement transparent and fair.
