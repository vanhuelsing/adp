# ADP v0.2.0 — Authentication & Security Specification

**Version:** 0.2.0-draft  
**Specification:** Auth & Security Layer for ADP  
**Based on:** ADP v0.1.1  
**Status:** Draft  
**Author:** Protocol Architect

---

## 1. Overview

This document defines authentication and security mechanisms for ADP v0.2.0. It standardizes how agents authenticate against providers and how providers prove their identity.

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Simplicity first** | API Keys for 80% of use cases |
| **Use standards** | OAuth 2.0 (RFC 6749), no custom solutions |
| **Security** | Keys never in the URL, always in the header |
| **Predictability** | Standard HTTP status codes, standard headers |

---

## 2. Authentication Methods

ADP v0.2.0 supports three authentication methods:

| Method | Priority | Use Case |
|--------|----------|----------|
| API Key | P0 | Standard, all providers must support |
| OAuth 2.0 | P1 | Enterprise, SSO scenarios |
| Request Signing | P2 | High security requirements (optional) |

### 2.1 API Key Authentication (P0)

**Format:**
```
Authorization: Bearer adp_<base64url-encoded-key>
```

**Key Structure:**
```
adp_<version>_<random>_<checksum>

Example:
adp_v2_a1b2c3d4e5f6_x7y8z9
```

**Header Example:**
```http
POST /adp/offer HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_a1b2c3d4e5f6_x7y8z9
Content-Type: application/adp+json
X-ADP-Version: 0.2.0
```

**Rules:**
- API Keys are **always** transmitted in the `Authorization` header
- **Never** in the URL (query parameters) or body
- Keys should have at least 32 bytes of entropy
- Providers may use their own key formats (the `adp_` prefix is recommended)

### 2.2 OAuth 2.0 Client Credentials (P1)

**Flow:**
```
┌─────────┐                                    ┌──────────┐
│  Agent  │ ──(1) Token Request─────────────▶ │ Provider │
│         │    grant_type=client_credentials   │   Auth   │
│         │                                    │  Server  │
│         │ ◀────────(2) Access Token───────── │          │
│         │    { "access_token": "...",        │          │
│         │      "token_type": "Bearer",       │          │
│         │      "expires_in": 3600 }          │          │
│         │                                    │          │
│         │ ──(3) ADP Request + Access Token──▶│  ADP     │
│         │    Authorization: Bearer <token>   │  API     │
└─────────┘                                    └──────────┘
```

**Token Endpoint:**
```
POST /.well-known/adp/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=CLIENT_ID&
client_secret=CLIENT_SECRET&
scope=adp:request adp:intent
```

**Scopes:**
| Scope | Permission |
|-------|-----------|
| `adp:read` | Retrieve DealOffers |
| `adp:request` | Send DealRequests |
| `adp:intent` | Send DealIntents |
| `adp:admin` | Administrative operations |

### Scope-Endpoint Matrix

The following matrix shows which scopes are required to access individual ADP endpoints:

| Scope | GET /.well-known/adp.json | GET /adp/health | POST /adp/offer | POST /adp/intent | Admin Operations |
|-------|---------------------------|-----------------|-----------------|-------------------|-----------------|
| `adp:read` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `adp:request` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `adp:intent` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `adp:admin` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Notes:**
- **Discovery and Health:** These are public endpoints — scopes only apply when auth is optionally enabled. Unauthenticated requests are always permitted on these endpoints.
- **Scope Hierarchy:** `adp:admin` is a superset of all other scopes. A token with `adp:admin` may perform all operations.
- **Future Scopes:** Admin operations will be defined in future versions (provider dashboard, API key management, quota management, etc.).

**Discovery:**
Providers supporting OAuth 2.0 must announce this in `.well-known/adp.json`:

```json
{
  "adp_supported": true,
  "auth_methods": ["api_key", "oauth2"],
  "oauth2": {
    "token_endpoint": "https://auth.provider.com/oauth/token",
    "scopes_supported": ["adp:read", "adp:request", "adp:intent"]
  }
}
```

### 2.3 Request Signing (P2, Optional)

For scenarios that require additional integrity assurance.

**Mechanism:** HMAC-SHA256 over the request body and critical headers

**Headers:**
```http
X-ADP-Signature: hmac-sha256=<base64-signature>
X-ADP-Signature-Timestamp: 1712345678
```

**Signature Input:**
```
<timestamp>.<method>.<path>.<content-hash>

Example:
1712345678.POST./adp/offer.sha256=<body-hash>
```

**Implementation Note:**
Request Signing is optional. If a provider supports it, this must be announced in `.well-known/adp.json`.

---

## 3. Rate Limiting

### 3.1 Rate Limit Headers

**Scope:** Rate Limit Headers are **required on authenticated endpoints only** (POST /adp/offer, POST /adp/intent). They are **optional on unauthenticated endpoints** (GET /.well-known/adp.json, GET /adp/health).

Providers must return these standard headers on authenticated endpoints:

| Header | Description | Example |
|--------|-------------|---------|
| `X-ADP-RateLimit-Limit` | Maximum requests per time window | `1000` |
| `X-ADP-RateLimit-Remaining` | Remaining requests | `999` |
| `X-ADP-RateLimit-Reset` | ISO 8601 UTC timestamp when the rate limit resets | `2026-03-12T10:00:00Z` |

**Example Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/adp+json
X-ADP-RateLimit-Limit: 1000
X-ADP-RateLimit-Remaining: 999
X-ADP-RateLimit-Reset: 2026-03-12T10:00:00Z

{ "adp": { "type": "DealOffer", ... } }
```

### 3.2 Rate Limit Exceeded (429)

When the rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/adp+json
Retry-After: 60
X-ADP-RateLimit-Limit: 1000
X-ADP-RateLimit-Remaining: 0
X-ADP-RateLimit-Reset: 2026-03-12T10:01:00Z

{
  "adp": {
    "version": "0.2.0",
    "type": "DealError",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-12T10:00:00Z",
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again after 60 seconds.",
    "retryable": true,
    "retry_after_ms": 60000
  }
}
```

---

## 4. Idempotency

For repeatable requests without side effects.

### 4.1 Idempotency Key Header

```http
X-ADP-Idempotency-Key: <uuid-v4>
```

**Semantics:**
- The first request with a key is processed normally
- Repeated requests with the same key (within 24 hours) return the same response
- Providers must store idempotency keys for 24 hours

**Scope (UPDATED - v0.2.0 Clarification):**
An idempotency key is **unique within the tuple `(API Key, HTTP Method, Endpoint Path)`**. The same UUID from different API keys is treated as independent. Providers MUST consider the scope when deduplicating.

**Example:**
```
- Request 1: API-Key=key_abc, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → processed
- Request 2: API-Key=key_abc, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → Duplicate (cached response)
- Request 3: API-Key=key_xyz, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → Newly processed (different key)
```

This prevents security issues where an attacker with different authentication could exploit deduplication.

**Example:**
```http
POST /adp/intent HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_...
Content-Type: application/adp+json
X-ADP-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{ "adp": { "type": "DealIntent", ... } }
```

---

## 5. Error Responses

### 5.1 Auth Errors

**401 Unauthorized — Missing/invalid token:**
```json
{
  "adp": {
    "version": "0.2.0",
    "type": "DealError",
    "id": "...",
    "timestamp": "2026-03-12T10:00:00Z",
    "correlation_id": "..."
  },
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token",
    "retryable": false
  }
}
```

**403 Forbidden — Insufficient permissions:**
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient scope. Required: adp:intent",
    "retryable": false
  }
}
```

### 5.2 Error Codes

For a complete and authoritative list of all error codes used in ADP v0.2.0, including error codes defined in this Auth spec and in other specs (Core v0.1.1, HTTP Binding), refer to the **central Error Code Registry** in the HTTP Binding Specification (Section 3: Error Code Registry).

The following error codes are specific to authentication and authorization scenarios, but are documented in the central registry:

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing/invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `INVALID_SIGNATURE` | 401 | HMAC signature invalid (with Request Signing) |
| `TOKEN_EXPIRED` | 401 | OAuth token expired |

Additional error codes applicable to authentication (inherited from Core v0.1.1):
- `RATE_LIMITED` (429) — Rate limit exceeded
- `VERSION_MISMATCH` (400) — Unsupported ADP version

**Reference:** See http-binding.md Section 3 for the complete registry.

---

## 6. JSON Schema

### 6.1 Auth Header Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://apideals.ai/schemas/auth-header.schema.json",
  "title": "ADP Auth Header",
  "description": "Authentication header formats for ADP",
  "type": "object",
  "properties": {
    "Authorization": {
      "type": "string",
      "pattern": "^Bearer (adp_[a-zA-Z0-9_-]+|eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]+)$",
      "description": "Bearer token - either ADP API Key or JWT/OAuth token"
    },
    "X-ADP-Version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "ADP Protocol version"
    },
    "X-ADP-Idempotency-Key": {
      "type": "string",
      "format": "uuid",
      "description": "Idempotency key for request deduplication"
    },
    "X-ADP-Signature": {
      "type": "string",
      "pattern": "^hmac-sha256=[A-Za-z0-9+/=]+$",
      "description": "HMAC-SHA256 signature (optional)"
    },
    "X-ADP-Signature-Timestamp": {
      "type": "string",
      "pattern": "^\\d{10}$",
      "description": "Unix timestamp for signature"
    }
  },
  "required": ["Authorization", "X-ADP-Version"]
}
```

### 6.2 Rate Limit Response Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://apideals.ai/schemas/rate-limit.schema.json",
  "title": "ADP Rate Limit Headers",
  "type": "object",
  "properties": {
    "X-ADP-RateLimit-Limit": {
      "type": "integer",
      "minimum": 1,
      "description": "Maximum requests allowed per window"
    },
    "X-ADP-RateLimit-Remaining": {
      "type": "integer",
      "minimum": 0,
      "description": "Remaining requests in current window"
    },
    "X-ADP-RateLimit-Reset": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 UTC timestamp when the limit resets"
    }
  },
  "required": ["X-ADP-RateLimit-Limit", "X-ADP-RateLimit-Remaining", "X-ADP-RateLimit-Reset"]
}
```

---

## 7. Provider Discovery Extension

Extension of `.well-known/adp.json` with authentication information:

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1", "0.2.0"],
  "offer_endpoint": "https://api.provider.com/adp/offer",
  
  "auth": {
    "methods": ["api_key", "oauth2"],
    "api_key": {
      "format": "adp_<version>_<key>_<checksum>",
      "header": "Authorization: Bearer <token>"
    },
    "oauth2": {
      "token_endpoint": "https://auth.provider.com/oauth/token",
      "authorization_endpoint": "https://auth.provider.com/oauth/authorize",
      "scopes_supported": ["adp:read", "adp:request", "adp:intent"],
      "grant_types_supported": ["client_credentials", "authorization_code"]
    },
    "request_signing": {
      "supported": true,
      "algorithm": "hmac-sha256"
    }
  },
  
  "rate_limiting": {
    "requests_per_minute": 1000,
    "burst_allowance": 100
  }
}
```

---

## 8. Examples

### 8.1 API Key (cURL)

```bash
curl -X POST https://api.provider.com/adp/offer \
  -H "Authorization: Bearer adp_v2_a1b2c3d4e5f6_x7y8z9" \
  -H "Content-Type: application/adp+json" \
  -H "X-ADP-Version: 0.2.0" \
  -d '{
    "adp": {
      "version": "0.2.0",
      "type": "DealRequest",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-03-12T10:00:00Z"
    },
    "request": { ... }
  }'
```

### 8.2 OAuth 2.0 Token Request (Python)

```python
import requests

# Step 1: Get Access Token
token_response = requests.post(
    "https://auth.provider.com/oauth/token",
    data={
        "grant_type": "client_credentials",
        "client_id": "CLIENT_ID",
        "client_secret": "CLIENT_SECRET",
        "scope": "adp:request adp:intent"
    }
)
access_token = token_response.json()["access_token"]

# Step 2: Use ADP API
deal_response = requests.post(
    "https://api.provider.com/adp/offer",
    headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/adp+json",
        "X-ADP-Version": "0.2.0"
    },
    json={
        "adp": {
            "version": "0.2.0",
            "type": "DealRequest",
            ...
        }
    }
)
```

### 8.3 Request Signing (Go)

```go
package main

import (
    "crypto/hmac"
    "crypto/sha256"
    "encoding/base64"
    "fmt"
    "time"
)

func signRequest(method, path, bodyHash string, secret []byte) (string, string) {
    timestamp := fmt.Sprintf("%d", time.Now().Unix())
    
    input := fmt.Sprintf("%s.%s.%s.%s", timestamp, method, path, bodyHash)
    
    mac := hmac.New(sha256.New, secret)
    mac.Write([]byte(input))
    signature := base64.StdEncoding.EncodeToString(mac.Sum(nil))
    
    return timestamp, signature
}
```

---

## 9. Security Recommendations

### 9.1 For Providers

1. **HTTPS enforced** — ADP requests over TLS 1.2+ only
2. **Key Rotation** — Support for multiple active keys
3. **Audit Logging** — Log all auth events
4. **Rate Limiting per Key** — Not only globally
5. **Key Scopes** — Minimum permissions (Principle of Least Privilege)

### 9.2 For Agents

1. **Store keys securely** — Environment variables, never in code
2. **No retry on 401** — Key is invalid; retrying is not useful
3. **Exponential backoff on 429** — Respect rate limits
4. **Token Refresh** — Renew OAuth tokens before expiry

---

## 10. Migration from v0.1.1

v0.1.1 had no defined auth layer. Migration:

| v0.1.1 | v0.2.0 |
|--------|--------|
| No auth defined | API Key or OAuth 2.0 required |
| No rate limits | Standardized rate limit headers |
| No idempotency | Optional via idempotency key |

**Breaking Change:** Yes — providers that previously accepted anonymous requests must implement auth.

---

## Appendix: Summary

| Feature | Status | Implementation |
|---------|--------|----------------|
| API Key Auth | Required | `Authorization: Bearer adp_...` |
| OAuth 2.0 | Optional | Client Credentials Flow |
| Request Signing | Optional | HMAC-SHA256 |
| Rate Limit Headers | Required | `X-ADP-RateLimit-*` |
| Idempotency | Optional | `X-ADP-Idempotency-Key` |

---

## Changelog

### 2026-03-12 — Critical fixes

**Fix 3: Central Error Code Registry (Reference)**
- Updated error codes section (5.2) to reference central registry in http-binding.md Section 3
- Removed duplicate error code definitions
- Added note directing readers to http-binding.md for complete and authoritative error code list

**Fix 4: Rate Limit Headers Scope Clarification**
- Added scope note to Section 3.1: Rate Limit headers are required on authenticated endpoints only
- Clarified in description: "Providers must return these standard headers on authenticated endpoints"
- Added reference to Section 3.1 scope note for clarity

**Fix 7: OAuth Scopes incomplete — Scope-Endpoint Matrix added**
- Added formal Scope-Endpoint Matrix in Section 2.2 (after OAuth 2.0 Scopes table)
- Matrix shows exactly which scopes apply to which endpoints
- Added explanatory notes on public endpoints, scope hierarchy, and future admin operations
- Eliminates ambiguity between adp:read and adp:admin

**Fix 9: Idempotency Key scope unclear — clarification added**
- Updated Section 4.1 with explicit scope definition: `(API Key, HTTP Method, Endpoint Path)`
- Added security rationale for different scopes per API key
- Added practical example with three request scenarios
- Prevents deduplication security issues

**Fix 14: Unify timestamps to ISO 8601**
- Changed `X-ADP-RateLimit-Reset` from Unix Timestamp (integer) to ISO 8601 UTC (string) in Section 3.1
- Updated all examples in Section 3.1 and 3.2 with new timestamp format
- Updated JSON Schema (Section 6.2): Type changed from `integer` to `string` with `format: date-time`
- Migration note: Rate Limit Reset is now consistent with other ADP timestamp fields (ISO 8601 UTC)

**Consistency fixes:** Added Scope-Endpoint Matrix, Idempotency-Scope clarification, timestamp format unification

*End of Auth Specification v0.2.0*
