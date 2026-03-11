# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.1-draft] — 2026-03-10

Initial public release after multi-role review.

### Breaking
- `DealAccept` renamed to `DealIntent` (legal safety)
- `expires_at` renamed to `valid_until` in DealRequest
- `task_class` (singular) → `task_classes[]` (array)

### Added
- `DealError` message type
- `compliance_verified_by` required field
- `is_automated` required field (EU AI Act compliance)
- `binding`, `requires_human_confirmation`, `party_type` in DealIntent
- `ai_act_risk_class`, `gpai_model_card_url`, `prohibited_uses` in model
- `request_ttl_hours` for GDPR Art. 17 compliance
- `/.well-known/adp.json` discovery convention
- Legal disclaimers for compliance tags

### Changed
- Dual licensing: CC-BY 4.0 (spec) + Apache 2.0 (code)

## [0.1.0-draft] — 2026-03-09

Initial internal draft.
