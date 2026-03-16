# Security Considerations

**Version:** 0.1.1-draft
**Status:** Draft
**Last Updated:** 2026-03-11

---

## 1. Threat Model

ADP v0.1.1 enables machine-to-machine communication between agents and API providers. The protocol currently lacks built-in authentication, message signing, and replay protection. Implementations MUST address the following threats at the transport or application layer.

### 1.1 Agent Spoofing

An attacker may impersonate a legitimate agent to submit fabricated volume or budget claims, harvest counter-offers, or gather competitive intelligence.

**Risk:** Medium | **Impact:** Distorted market data, resource exhaustion

### 1.2 Provider Impersonation

A malicious actor may pose as a legitimate provider to deliver fraudulent offers, inject phishing URLs via `activation.redirect_url`, or make false compliance assertions (e.g., `gdpr_compliant: true`).

**Risk:** High | **Impact:** Data loss, regulatory violations, financial damage

### 1.3 Replay Attacks

ADP messages carry no replay protection. Valid `DealIntent` or `DealRequest` messages could be captured and re-submitted, potentially creating unintended contractual obligations or causing resource exhaustion.

**Risk:** Medium | **Impact:** Unintended bindings, service degradation

### 1.4 Denial of Service

Attackers may flood endpoints with `DealRequest` messages, send oversized payloads, or craft deeply nested pricing tiers to exhaust CPU and memory.

**Risk:** Medium | **Impact:** Service disruption, increased operational cost

### 1.5 Man-in-the-Middle

Because v0.1 is transport-agnostic, insecure transport channels expose offer prices, redirect URLs, and compliance data to interception and modification.

**Risk:** High (on insecure transports) | **Impact:** Financial fraud, data exfiltration

---

## 2. Authentication and Authorization

### 2.1 Status in v0.1

ADP v0.1 intentionally excludes authentication and authorization from the protocol schema. There are no API keys, signatures, identity-provider integrations, or mutual TLS requirements at the protocol level. The specification defines message formats only; security is delegated to the transport and application layers.

### 2.2 Implementation Guidance

Until the protocol provides native authentication, implementers SHOULD apply the following measures:

| Mechanism | Scope | Notes |
|-----------|-------|-------|
| TLS 1.3 | All transports | Connection encryption is mandatory |
| API keys | Provider endpoints | Transmitted in HTTP headers, never in the JSON body |
| IP allowlisting | B2B scenarios | Static allowlists for known partners |
| Rate limiting | Both sides | See Section 4 |

---

## 3. Message Integrity

### 3.1 Absence of Signatures

The protocol does not include cryptographic signatures. No field in the ADP envelope provides integrity verification. This means:

- **Price manipulation:** A MitM attacker can alter offer prices in transit.
- **Terms manipulation:** Fields such as `terms_url` or `valid_until` can be modified.
- **Identity spoofing:** Any party can construct messages with arbitrary `agent_id` or `provider_id` values.

### 3.2 Validation Requirements

Implementations SHOULD perform the following checks on all received messages:

```python
def validate_offer(offer):
    assert offer.pricing.base.input_per_mtok > 0
    assert offer.pricing.base.output_per_mtok > 0

    assert offer.valid_until > offer.valid_from
    assert offer.valid_until > now()

    assert offer.terms_url.startswith("https://")
    assert offer.provider.url.startswith("https://")
```

Additionally, implementers SHOULD enforce TLS 1.3 on all transports and validate the domain identity of the remote endpoint.

---

## 4. Rate Limiting

### 4.1 Protocol-Level Error

ADP defines a standardized rate-limit error:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealError"
  },
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded.",
    "retryable": true,
    "retry_after_ms": 60000
  }
}
```

### 4.2 Recommended Limits

Providers SHOULD enforce per-endpoint rate limits:

| Endpoint | Suggested Limit | Keyed By |
|----------|----------------|----------|
| `/.well-known/adp.json` | 100 req/min | IP address |
| DealRequest endpoint | 60 req/min | API key |
| DealIntent endpoint | 10 req/min | API key |

Agents MUST respect `retry_after_ms` when present. When no value is provided, agents SHOULD implement exponential backoff starting at 1 second, capped at 60 seconds.

### 4.3 HTTP Headers

When using HTTP transport, providers SHOULD include standard rate-limit headers:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1647000000
```

---

## 5. Data Validation

### 5.1 Schema Validation

All ADP messages MUST be validated against the published JSON Schema before processing. At minimum, the `adp` envelope must contain valid `version`, `type`, `id`, and `timestamp` fields.

### 5.2 Input Constraints

**String fields:**
- `agent_id`: Maximum 256 characters, permitted characters: `a-z0-9:._-`
- `provider_id`: Maximum 64 characters, permitted characters: `a-z0-9-`
- `email`: RFC 5322 compliant

**Numeric fields:**
- Prices: Non-negative, maximum 6 decimal places
- Token counts: Positive integers, maximum 10^15
- Percentages: 0.0 to 100.0

**URLs:**
- HTTPS only
- No loopback addresses (127.0.0.1, localhost)
- No private IP ranges (10.0.0.0/8, 192.168.0.0/16)

### 5.3 Payload Size Limits

Implementations SHOULD enforce maximum payload sizes per message type:

| Message Type | Maximum Size |
|-------------|-------------|
| DealRequest | 100 KB |
| DealOffer | 250 KB |
| DealIntent | 50 KB |
| DealError | 10 KB |

Payloads exceeding these limits SHOULD be rejected before parsing. JSON nesting depth SHOULD be limited to 20 levels to prevent resource exhaustion.

---

## 6. GDPR and Data Protection

### 6.1 Data Retention

The `request_ttl_hours` field in `DealRequest` supports GDPR Article 17 (right to erasure). Providers MUST delete all personally identifiable data associated with a request after the specified TTL expires. Only aggregated or anonymized data may be retained beyond the TTL for statistical purposes.

### 6.2 Personally Identifiable Information

Production messages MUST NOT contain real personal names, personal email addresses, phone numbers, end-user IP addresses, or credentials. All specification examples use fictitious identifiers (e.g., `agent:acme:bot`, `api@example.com`).

### 6.3 Self-Declared Compliance

Compliance claims in ADP are self-declared by default (`compliance_verified_by: "self-declared"`). Agents SHOULD treat self-declared claims as unverified assertions and perform independent due diligence. Third-party or registry-verified claims (`"third-party"`, `"apideals-verified"`) carry higher assurance but remain outside the protocol's trust boundary.

### 6.4 Data Processing Agreements

When `dpa_available: true` is indicated in an offer's compliance block, agents SHOULD ensure a Data Processing Agreement is signed before issuing a `DealIntent`. Setting `requires_human_confirmation: true` on the intent is RECOMMENDED for any deal involving personal data.

---

*End of Security Considerations v0.1.1*
