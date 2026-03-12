# Changelog

All notable changes to the ADP (apideals Deal Protocol) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-12

### Added
- **Authentication Layer** (`spec/v0.2/auth.md`)
  - API Key authentication (Bearer token format: `adp_v2_*`)
  - OAuth 2.0 Client Credentials flow with scopes (`adp:read`, `adp:request`, `adp:intent`, `adp:admin`)
  - Optional Request Signing (HMAC-SHA256)
  - Rate Limiting headers: `X-ADP-RateLimit-Limit`, `X-ADP-RateLimit-Remaining`, `X-ADP-RateLimit-Reset` (ISO 8601 UTC)
  - Idempotency Key support for deduplication (scope: API Key + Method + Path)
  
- **HTTP Binding Specification** (`spec/v0.2/http-binding.md`)
  - Standardized endpoints:
    - `GET /.well-known/adp.json` — Provider discovery
    - `POST /adp/offer` — DealRequest → DealOffer(s)
    - `POST /adp/intent` — DealIntent submission
    - `GET /adp/health` — Provider health check
  - HTTP status codes and error response format
  - Content-Type: `application/adp+json`
  - OpenAPI 3.1.0 specification
  - Central Error Code Registry (10 error codes with retryable semantics)
  
- **New Message Type: DealIntentAck** (`spec/v0.2/http-binding.md` Section 2.5)
  - Response to DealIntent (202 Accepted)
  - Acknowledgment status: received, processing, confirmed
  - Provider-side reference ID and expiration
  - Full JSON Schema definition
  
- **Multimodal Pricing** (`spec/v0.2/pricing-multimodal.md`)
  - Image Input: `$/Megapixel` with token equivalents
  - Image Output: `$/Image` with resolution tiers
  - Audio Input: `$/Minute` (Whisper-style)
  - Audio Output: `$/Character` (TTS-style, e.g., ElevenLabs)
  - Video Input: `$/Frame` or `$/Second` with FPS baseline
  - Bundle pricing for combined modalities
  - Calculation pipeline: Tiers → Bundles → Modifiers
  - Token equivalents for image-to-token conversion (GPT-4o Vision use case)
  
- **JSON Schemas** (JSON Schema 2020-12)
  - `auth-header.schema.json` — Auth header format validation
  - `rate-limit.schema.json` — Rate limit header schema
  - `deal-intent-ack.schema.json` — DealIntentAck message type
  - `discovery-v0.2.schema.json` — Enhanced .well-known discovery with `discovery_version` field
  - `pricing-multimodal.schema.json` — Complete multimodal pricing schema
  
- **Example Files** (all validated against schemas)
  - `deal-request-multimodal.json` — DealRequest with text + image modalities
  - `deal-offer-vision.json` — GPT-4o Vision pricing example
  - `deal-offer-tts.json` — ElevenLabs TTS pricing example
  - `deal-intent-with-auth.json` — DealIntent with auth headers and HMAC signature
  - `deal-intent-ack.json` — DealIntentAck response example
  - `deal-error-unauthorized.json` — 401 Unauthorized error
  - `deal-error-rate-limited.json` — 429 Rate Limited error with ISO 8601 reset
  - `well-known-adp-v0.2.json` — Discovery endpoint v0.2 with auth methods

### Changed
- **Rate Limit Reset Format**: Changed from Unix timestamp to ISO 8601 UTC (e.g., `2026-03-12T10:00:00Z`)
- **Timestamp Consistency**: All timestamps unified to ISO 8601 UTC across all specs
- **Discovery Versioning**: Added `discovery_version` field to distinguish v0.1.1 vs v0.2.0 format
- **Error Code Registry**: Centralized in HTTP Binding spec (Section 3) instead of scattered across specs

### Breaking Changes
- ⚠️ **Authentication Required**: All authenticated endpoints now require `Authorization` header (API Key or OAuth 2.0)
- ⚠️ **Rate Limit Headers**: Providers MUST return `X-ADP-RateLimit-*` headers on authenticated endpoints
- ⚠️ **Timestamp Format**: `X-ADP-RateLimit-Reset` changed from Unix integer to ISO 8601 string
- ⚠️ **DealIntentAck**: `/adp/intent` now returns 202 with `DealIntentAck` (new message type)
- ⚠️ **Error Code Standardization**: Errors must use codes from central registry (http-binding.md Section 3)

### Migration Guide (v0.1.1 → v0.2.0)
See `spec/v0.2/README.md` for detailed migration steps for agents and providers.

### Status
- **v0.2.0-draft** — Ready for community feedback before RC (Release Candidate)

## [0.1.1] - 2026-03-11

### Added
- **JSON Schemas** (Draft 2020-12) for all message types
  - `adp-header.schema.json`
  - `deal-request.schema.json`
  - `deal-offer.schema.json`
  - `deal-intent.schema.json`
  - `deal-error.schema.json`
  - `pricing.schema.json`
  - `compliance.schema.json`
  - `well-known-adp.schema.json`
- **TypeScript SDK** (`@adp/sdk`) with runtime validation
  - Type definitions for all message types
  - Validator functions using AJV
  - Full test suite with Vitest
- **Security documentation** (`docs/security-considerations.md`)
  - Threat model
  - Authentication roadmap
  - Data validation guidelines
  - GDPR compliance notes
- **CI/CD pipeline** (GitHub Actions)
  - Schema validation
  - Example file validation
  - TypeScript build and test

### Changed
- **Complete i18n**: All documentation now in English
- **Author attribution**: Changed to `vanhuelsing` throughout
- **README overhaul**: Hero section, installation instructions, badges
- **Protocol spec**: Added Section 8 "Security Considerations"

### Fixed
- Example `deal-offer-basic.json`: Changed `APAC` to `JP` (2-letter ISO code)
- Example `deal-error.json`: Fixed UUID v4 format (was v1)
- All examples now validate against schemas

### Security
- UUID v4 format strictly enforced in schemas
- ISO 8601 UTC timestamps strictly enforced
- String length limits added (name: 100, conditions: 500, notes: 1000)

## [0.1.0] - 2026-03-09

### Added
- Initial protocol specification
- Four core message types: DealRequest, DealOffer, DealIntent, DealError
- Pricing schema with tiers, modifiers, and commitment deals
- Compliance and capabilities vocabulary
- Provider discovery via `.well-known/adp.json`
- Dual licensing (CC-BY 4.0 for spec, Apache 2.0 for code)

[0.2.0]: https://github.com/vanhuelsing/adp/releases/tag/v0.2.0
[0.1.1]: https://github.com/vanhuelsing/adp/releases/tag/v0.1.1
[0.1.0]: https://github.com/vanhuelsing/adp/releases/tag/v0.1.0
