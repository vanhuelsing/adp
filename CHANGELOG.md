# Changelog

All notable changes to the ADP specification are documented here.

## [0.1.1-draft] — 2026-03-10

Initial public release after multi-role review (Legal, Strategy, Backend, QA).

### Breaking Changes
- `DealAccept` renamed to `DealIntent` — legal safety (§§ 145–147 BGB risk)
- `expires_at` in DealRequest renamed to `valid_until` (consistency with DealOffer)
- `task_class` (singular) → `task_classes[]` (array, OR-logic) in DealRequest

### Added
- `DealError` as 4th core message type
- `compliance_verified_by` required field in DealOffer.compliance
- `is_automated` required field in requester (EU AI Act Art. 50)
- `binding`, `requires_human_confirmation`, `party_type` in DealIntent
- `ai_act_risk_class`, `gpai_model_card_url`, `prohibited_uses` in DealOffer.model
- `privacy_policy_url` in DealOffer.compliance
- `request_ttl_hours` in DealRequest (GDPR Art. 17)
- `/.well-known/adp.json` provider discovery convention (Section 10)
- Legal disclaimer for compliance tags
- Legal notice for DealIntent (non-binding)

### Fixed
- All example IDs updated to valid UUID v4
- `activation.redirect_url` documented as conditional required field
- `valid_from > valid_until` validation rule added
- `data_regions` standardized: ISO 3166-1 Alpha-2 + aggregates (EU, US, APAC)
- `contact` structured as object (email, webhook_url, support_url)
- `correlation_id` semantics documented per message type
- `free_tier: null` → field omitted = no free tier (consistent)
- preferred/excluded providers conflict rule: excluded always wins
- Modifier combination order documented with pseudocode
- Flat-Rate tier edge case warning with numeric example

### Changed
- License: Apache 2.0 → CC-BY 4.0 (spec) + Apache 2.0 (code)
- Roadmap updated with realistic timelines
- `effective_price_example` standardized with structured fields

## [0.1.0-draft] — 2026-03-09

Initial internal draft by Protocol Architect.
