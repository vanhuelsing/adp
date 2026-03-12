# ADP v0.2.0 — Authentication & Security Specification

**Version:** 0.2.0-draft  
**Spezifikation:** Auth & Security Layer für ADP  
**Basierend auf:** ADP v0.1.1  
**Status:** Draft  
**Autor:** Protocol Architect

---

## 1. Überblick

Dieses Dokument definiert Authentifizierungs- und Sicherheitsmechanismen für ADP v0.2.0. Es standardisiert, wie Agents sich gegenüber Providern authentifizieren und wie Provider ihre Identität nachweisen.

### Design-Prinzipien

| Prinzip | Umsetzung |
|---------|-----------|
| **Einfachheit zuerst** | API Keys für 80% der Use-Cases |
| **Standards nutzen** | OAuth 2.0 (RFC 6749), keine Eigenentwicklung |
| **Sicherheit** | Keys niemals im URL, immer im Header |
| **Erwartbarkeit** | Standard-HTTP-Status-Codes, Standard-Header |

---

## 2. Authentifizierungsmethoden

ADP v0.2.0 unterstützt drei Authentifizierungsmethoden:

| Methode | Priorität | Use-Case |
|---------|-----------|----------|
| API Key | P0 | Standard, alle Anbieter müssen unterstützen |
| OAuth 2.0 | P1 | Enterprise, SSO-Szenarien |
| Request Signing | P2 | Hohe Sicherheitsanforderungen (optional) |

### 2.1 API Key Authentication (P0)

**Format:**
```
Authorization: Bearer adp_<base64url-encoded-key>
```

**Key-Struktur:**
```
adp_<version>_<random>_<checksum>

Beispiel:
adp_v2_a1b2c3d4e5f6_x7y8z9
```

**Header-Beispiel:**
```http
POST /adp/offer HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_a1b2c3d4e5f6_x7y8z9
Content-Type: application/adp+json
X-ADP-Version: 0.2.0
```

**Regeln:**
- API Keys werden **immer** im `Authorization` Header übertragen
- **Niemals** im URL (Query-Parameter) oder Body
- Keys sollten mindestens 32 Byte Entropie haben
- Provider können ihre eigenen Key-Formate nutzen (mit `adp_` Präfix empfohlen)

### 2.2 OAuth 2.0 Client Credentials (P1)

**Ablauf:**
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
| Scope | Berechtigung |
|-------|--------------|
| `adp:read` | DealOffers abrufen |
| `adp:request` | DealRequests senden |
| `adp:intent` | DealIntents senden |
| `adp:admin` | Verwaltungsoperationen |

### Scope-Endpoint-Matrix

Die folgende Matrix zeigt, welche Scopes für den Zugriff auf einzelne ADP-Endpoints erforderlich sind:

| Scope | GET /.well-known/adp.json | GET /adp/health | POST /adp/offer | POST /adp/intent | Admin-Operationen |
|-------|---------------------------|-----------------|-----------------|-------------------|-------------------|
| `adp:read` | ✅ | ✅ | ❌ | ❌ | ❌ |
| `adp:request` | ✅ | ✅ | ✅ | ❌ | ❌ |
| `adp:intent` | ✅ | ✅ | ❌ | ✅ | ❌ |
| `adp:admin` | ✅ | ✅ | ✅ | ✅ | ✅ |

**Hinweise:**
- **Discovery und Health:** Diese sind öffentliche Endpoints — Scopes gelten dort nur wenn Auth optional aktiviert ist. Unauthentifizierte Requests sind auf diesen Endpoints immer erlaubt.
- **Scope-Hierarchie:** `adp:admin` ist ein Superset aller anderen Scopes. Ein Token mit `adp:admin` kann alle Operationen durchführen.
- **Future Scopes:** Admin-Operationen werden in zukünftigen Versionen definiert (Provider-Dashboard, API-Key-Management, Quota-Management, etc.).

**Discovery:**
Provider, die OAuth 2.0 unterstützen, müssen dies in `.well-known/adp.json` ankündigen:

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

Für Szenarien, die zusätzliche Integritätssicherheit benötigen.

**Mechanismus:** HMAC-SHA256 über Request-Body und kritische Header

**Header:**
```http
X-ADP-Signature: hmac-sha256=<base64-signature>
X-ADP-Signature-Timestamp: 1712345678
```

**Signatur-Input:**
```
<timestamp>.<method>.<path>.<content-hash>

Beispiel:
1712345678.POST./adp/offer.sha256=<body-hash>
```

**Implementierungs-Hinweis:**
Request Signing ist optional. Wenn ein Provider es unterstützt, muss dies in `.well-known/adp.json` angekündigt werden.

---

## 3. Rate Limiting

### 3.1 Rate Limit Headers

**Scope:** Rate Limit Headers sind **required on authenticated endpoints only** (POST /adp/offer, POST /adp/intent). They are **optional on unauthenticated endpoints** (GET /.well-known/adp.json, GET /adp/health).

Provider müssen diese Standard-Header auf authentifizierten Endpoints zurückgeben:

| Header | Beschreibung | Beispiel |
|--------|--------------|----------|
| `X-ADP-RateLimit-Limit` | Maximale Requests pro Zeitfenster | `1000` |
| `X-ADP-RateLimit-Remaining` | Verbleibende Requests | `999` |
| `X-ADP-RateLimit-Reset` | ISO 8601 UTC Zeitpunkt, wann das Rate Limit zurückgesetzt wird | `2026-03-12T10:00:00Z` |

**Beispiel-Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/adp+json
X-ADP-RateLimit-Limit: 1000
X-ADP-RateLimit-Remaining: 999
X-ADP-RateLimit-Reset: 2026-03-12T10:00:00Z

{ "adp": { "type": "DealOffer", ... } }
```

### 3.2 Rate Limit überschritten (429)

Wenn das Rate Limit überschritten wird:

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

## 4. Idempotenz

Für wiederholbare Requests ohne Nebeneffekte.

### 4.1 Idempotency Key Header

```http
X-ADP-Idempotency-Key: <uuid-v4>
```

**Semantik:**
- Der erste Request mit einem Key wird normal verarbeitet
- Wiederholte Requests mit demselben Key (innerhalb von 24h) liefern dieselbe Response
- Provider müssen Idempotency-Keys für 24h speichern

**Scope (UPDATED - v0.2.0 Clarification):**
Ein Idempotency Key ist **unique innerhalb des Tupels `(API Key, HTTP Method, Endpoint Path)`**. Derselbe UUID von verschiedenen API Keys wird als unabhängig behandelt. Provider MÜSSEN den Scope bei der Deduplizierung berücksichtigen.

**Beispiel:**
```
- Request 1: API-Key=key_abc, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → verarbeitet
- Request 2: API-Key=key_abc, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → Duplicate (cached response)
- Request 3: API-Key=key_xyz, Method=POST, Path=/adp/intent, Idempotency-Key=uuid-123 → Neu verarbeitet (anderer Key)
```

Dies verhindert Sicherheitsprobleme, bei denen ein Angreifer mit anderer Authentifizierung die Deduplizierung nutzen könnte.

**Beispiel:**
```http
POST /adp/intent HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_...
Content-Type: application/adp+json
X-ADP-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{ "adp": { "type": "DealIntent", ... } }
```

---

## 5. Fehler-Responses

### 5.1 Auth-Fehler

**401 Unauthorized - Kein/ungültiger Token:**
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

**403 Forbidden - Unzureichende Berechtigungen:**
```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient scope. Required: adp:intent",
    "retryable": false
  }
}
```

### 5.2 Fehler-Codes

For a complete and authoritative list of all error codes used in ADP v0.2.0, including error codes defined in this Auth spec and in other specs (Core v0.1.1, HTTP Binding), refer to the **central Error Code Registry** in the HTTP Binding Specification (Section 3: Error Code Registry).

The following error codes are specific to authentication and authorization scenarios, but are documented in the central registry:

| Code | HTTP Status | Bedeutung |
|------|-------------|-----------|
| `UNAUTHORIZED` | 401 | Kein/ungültiger Token |
| `FORBIDDEN` | 403 | Unzureichende Berechtigungen |
| `INVALID_SIGNATURE` | 401 | HMAC-Signatur ungültig (bei Request Signing) |
| `TOKEN_EXPIRED` | 401 | OAuth Token abgelaufen |

Additional error codes applicable to authentication (inherited from Core v0.1.1):
- `RATE_LIMITED` (429) — Rate Limit überschritten
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

## 7. Provider Discovery Erweiterung

Erweiterung von `.well-known/adp.json` um Auth-Informationen:

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

## 8. Beispiele

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

## 9. Sicherheits-Empfehlungen

### 9.1 Für Provider

1. **HTTPS enforced** — ADP Requests nur über TLS 1.2+
2. **Key Rotation** — Unterstützung für mehrere aktive Keys
3. **Audit Logging** — Alle Auth-Events loggen
4. **Rate Limiting pro Key** — Nicht nur global
5. **Key-Scopes** — Minimale Berechtigungen (Principle of Least Privilege)

### 9.2 Für Agents

1. **Keys sicher speichern** — Environment Variables, nie im Code
2. **Keine Wiederholung bei 401** — Key ist ungültig, Retry nicht sinnvoll
3. **Exponential Backoff bei 429** — Respektiere Rate Limits
4. **Token Refresh** — Bei OAuth vor Ablauf aktualisieren

---

## 10. Migration von v0.1.1

v0.1.1 hatte keinen definierten Auth-Layer. Migration:

| v0.1.1 | v0.2.0 |
|--------|--------|
| Kein Auth definiert | API Key oder OAuth 2.0 required |
| Keine Rate Limits | Standardisierte Rate Limit Header |
| Keine Idempotenz | Optional via Idempotency Key |

**Breaking Change:** Ja — Provider müssen Auth implementieren, die zuvor anonyme Requests akzeptiert haben.

---

## Appendix: Zusammenfassung

| Feature | Status | Implementierung |
|---------|--------|-----------------|
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
- Clarified in description: "Provider müssen diese Standard-Header auf authentifizierten Endpoints zurückgeben"
- Added reference to Section 3.1 scope note for clarity

**Fix 7: OAuth Scopes unvollständig — Scope-Endpoint-Matrix hinzugefügt**
- Added formal Scope-Endpoint-Matrix in Section 2.2 (nach OAuth 2.0 Scopes-Tabelle)
- Matrix zeigt genau welche Scopes auf welche Endpoints wirken
- Added explanatory notes zu öffentlichen Endpoints, Scope-Hierarchie und zukünftigen Admin-Operationen
- Beseitigt Ambiguität zwischen adp:read und adp:admin

**Fix 9: Idempotency Key Scope unklar — Klarstellung hinzugefügt**
- Updated Section 4.1 mit expliziter Scope-Definition: `(API Key, HTTP Method, Endpoint Path)`
- Added security rationale für unterschiedliche Scopes pro API-Key
- Added practical example mit drei Request-Szenarien
- Verhindert Deduplizierungs-Sicherheitsprobleme

**Fix 14: Zeitangaben auf ISO 8601 vereinheitlichen**
- Changed `X-ADP-RateLimit-Reset` from Unix Timestamp (integer) to ISO 8601 UTC (string) in Section 3.1
- Updated all examples in Section 3.1 and 3.2 with new timestamp format
- Updated JSON Schema (Section 6.2): Type changed from `integer` to `string` with `format: date-time`
- Migration note: Rate Limit Reset is now consistent with other ADP timestamp fields (ISO 8601 UTC)

**Consistency fixes:** Added Scope-Endpoint-Matrix, Idempotency-Scope-Klarstellung, Zeitformat-Vereinheitlichung

*Ende der Auth-Spezifikation v0.2.0*
