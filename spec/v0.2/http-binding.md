# ADP v0.2.0 — HTTP Binding Specification

**Version:** 0.2.0-draft  
**Spezifikation:** Transport-Layer für ADP über HTTP/HTTPS  
**Basierend auf:** ADP v0.1.1  
**Status:** Draft  
**Autor:** Protocol Architect

---

## 1. Überblick

Dieses Dokument definiert, wie ADP-Nachrichten über HTTP/HTTPS transportiert werden. Es standardisiert Endpoints, Methoden, Header, Status-Codes und Error-Handling.

### Design-Prinzipien

| Prinzip | Umsetzung |
|---------|-----------|
| **RESTful** | Standard-HTTP-Methoden (POST, GET) |
| **JSON-native** | Content-Type: application/adp+json |
| **Versioniert** | X-ADP-Version Header |
| **Idempotent** | X-ADP-Idempotency-Key für wiederholbare Requests |

---

## 2. Endpoints

### 2.1 Übersicht

| Endpoint | Methode | Zweck | Auth Required |
|----------|---------|-------|---------------|
| `/.well-known/adp.json` | GET | Discovery | Nein |
| `/adp/offer` | POST | DealRequest senden, DealOffers empfangen | Ja |
| `/adp/intent` | POST | DealIntent senden | Ja |
| `/adp/health` | GET | Provider Health-Check | Nein |

### 2.2 Discovery (GET /.well-known/adp.json)

**Beschreibung:** Maschinell lesbare Provider-Informationen

**Request:**
```http
GET /.well-known/adp.json HTTP/1.1
Host: provider.com
Accept: application/json
```

**Response (200 OK):**
```json
{
  "discovery_version": "0.2.0",
  "adp_supported": true,
  "adp_versions": ["0.1.1", "0.2.0"],
  "offer_endpoint": "https://api.provider.com/adp/offer",
  "intent_endpoint": "https://api.provider.com/adp/intent",
  "models_endpoint": "https://api.provider.com/adp/models",
  "static_offers_url": "https://provider.com/adp/offers.json",
  "auth": {
    "methods": ["api_key", "oauth2"]
  },
  "contact": {
    "email": "api@provider.com"
  },
  "last_updated": "2026-03-12T00:00:00Z"
}
```

**Notes:**
1. **Unauthenticated Endpoint:** Discovery is **not authenticated** (no Authorization header required). Rate Limit headers are **optional** on this endpoint.
2. **Backwards Compatibility (Migration from v0.1.1):** v0.1.1 used plural endpoints (`/adp/offers`, `/adp/models`) and optional fields `models_endpoint` and `static_offers_url`. v0.2.0 standardizes on singular endpoints (`/adp/offer`, `/adp/intent`). For backwards compatibility, v0.2.0 continues to support optional `models_endpoint` and `static_offers_url` fields in the discovery response.
3. **Discovery Version Field:** The `discovery_version` field (string, semver, OPTIONAL) indicates the version of the Discovery document format. If omitted, v0.1.1 format is assumed (backwards compatibility). Agents SHOULD use this field to determine the correct parsing logic for the Discovery response.

### 2.3 DealRequest → DealOffer(s) (POST /adp/offer)

**Beschreibung:** Ein Agent sendet einen DealRequest und erhält DealOffers zurück.

**Request:**
```http
POST /adp/offer HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_...
Content-Type: application/adp+json
X-ADP-Version: 0.2.0
X-ADP-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

{
  "adp": {
    "version": "0.2.0",
    "type": "DealRequest",
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-12T10:00:00Z",
    "correlation_id": null
  },
  "request": {
    "requester": {
      "agent_id": "agent:mycompany:procurement-bot",
      "is_automated": true
    },
    "requirements": {
      "task_classes": ["reasoning"],
      "modalities": ["text", "image_input"]
    },
    "budget": {
      "max_cost_per_mtok_input": 5.00,
      "currency": "USD"
    }
  }
}
```

**Success Response (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: application/adp+json
X-ADP-Version: 0.2.0
X-ADP-RateLimit-Limit: 1000
X-ADP-RateLimit-Remaining: 999
X-ADP-RateLimit-Reset: 2026-03-12T10:00:00Z

{
  "adp": {
    "version": "0.2.0",
    "type": "DealOffer",
    "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "timestamp": "2026-03-12T10:00:01Z",
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "offer": {
    "provider": { ... },
    "model": { ... },
    "pricing": { ... }
  }
}
```

**Notes:**
- Response kann ein einzelnes DealOffer oder ein Array von DealOffers sein
- Bei leerem Ergebnis: `200 OK` mit leerem Array `[]` oder einzelnes `DealError`

### 2.4 DealIntent (POST /adp/intent) & DealIntentAck Response

#### DealIntent Request

**Beschreibung:** Ein Agent signalisiert Interesse an einem DealOffer.

**Request:**
```http
POST /adp/intent HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_...
Content-Type: application/adp+json
X-ADP-Version: 0.2.0
X-ADP-Idempotency-Key: 660f9511-f3ac-52e5-c827-557766551111

{
  "adp": {
    "version": "0.2.0",
    "type": "DealIntent",
    "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "timestamp": "2026-03-12T10:05:00Z",
    "correlation_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012"
  },
  "intent": {
    "binding": false,
    "accepted_offer_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "activation": {
      "type": "redirect",
      "redirect_url": "https://provider.com/signup?deal=..."
    }
  }
}
```

**Success Response (202 Accepted):**
```http
HTTP/1.1 202 Accepted
Content-Type: application/adp+json
X-ADP-Version: 0.2.0

{
  "adp": {
    "version": "0.2.0",
    "type": "DealIntentAck",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-12T10:05:01Z",
    "correlation_id": "c3d4e5f6-a7b8-9012-cdef-345678901234"
  },
  "acknowledgment": {
    "status": "received",
    "next_steps": "Please complete signup at the provided redirect_url",
    "reference_id": "REF-12345"
  }
}
```

**Notes:**
- `202 Accepted` — Die Intent wurde empfangen, aber die Verarbeitung ist asynchron
- Provider MÜSSEN `DealIntentAck` als Bestätigung zurückgeben

### 2.5 DealIntentAck — Formal Specification

**Semantik:** Der Provider bestätigt den Empfang eines DealIntent. Dies ist eine neue, formale Nachrichtentype in v0.2.0 und war in v0.1.1 nicht vorhanden.

**Field Reference Table:**

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `adp.version` | `string` | ✅ | Protocol-Version (immer `"0.2.0"` oder höher) |
| `adp.type` | `enum` | ✅ | Nachrichtentyp: `"DealIntentAck"` |
| `adp.id` | `string` (UUID v4) | ✅ | Eindeutige Nachrichten-ID |
| `adp.timestamp` | `string` (ISO 8601 UTC) | ✅ | Erstellungszeitpunkt |
| `adp.correlation_id` | `string` (UUID v4) | ✅ | Referenz auf den akzeptierten `DealIntent` |
| `acknowledgment.status` | `enum` | ✅ | `"received"`, `"processing"`, `"confirmed"` |
| `acknowledgment.next_steps` | `string` | ❌ | Menschenlesbarer nächster Schritt |
| `acknowledgment.reference_id` | `string` | ❌ | Anbieter-seitige Referenz-ID |
| `acknowledgment.expires_at` | `string` (ISO 8601 UTC) | ❌ | Wann läuft die Bestätigung ab? |

**JSON Schema Example:**
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://apideals.ai/schemas/deal-intent-ack.schema.json",
  "title": "DealIntentAck",
  "type": "object",
  "properties": {
    "adp": {
      "type": "object",
      "properties": {
        "version": { "type": "string", "pattern": "^0\\.2\\." },
        "type": { "const": "DealIntentAck" },
        "id": { "type": "string", "format": "uuid" },
        "timestamp": { "type": "string", "format": "date-time" },
        "correlation_id": { "type": "string", "format": "uuid" }
      },
      "required": ["version", "type", "id", "timestamp", "correlation_id"]
    },
    "acknowledgment": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "enum": ["received", "processing", "confirmed"]
        },
        "next_steps": { "type": "string" },
        "reference_id": { "type": "string" },
        "expires_at": { "type": "string", "format": "date-time" }
      },
      "required": ["status"]
    }
  },
  "required": ["adp", "acknowledgment"]
}
```

**Example DealIntentAck Response:**
```json
{
  "adp": {
    "version": "0.2.0",
    "type": "DealIntentAck",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-12T10:05:01Z",
    "correlation_id": "c3d4e5f6-a7b8-9012-cdef-345678901234"
  },
  "acknowledgment": {
    "status": "received",
    "next_steps": "Please complete signup at the provided redirect_url",
    "reference_id": "REF-12345",
    "expires_at": "2026-03-19T10:05:01Z"
  }
}
```

**Note on New Message Type:**
`DealIntentAck` is a new message type introduced in ADP v0.2.0 and was not defined in v0.1.1. The `adp.type` enum for Core Message Types is extended to include `"DealIntentAck"` alongside the existing types: `"DealRequest"`, `"DealOffer"`, `"DealIntent"`, `"DealError"`.

### 2.6 Pagination

> **Status:** Deferred to v0.3

Pagination für große Result-Sets (z.B. Provider mit 500+ Modellen) ist für v0.3 geplant. Der vorgesehene Ansatz:

- `Link` Header mit `rel="next"` und `rel="prev"` (RFC 8288)
- Optional: `X-ADP-Total-Count` Header für Gesamtanzahl
- Optional: `limit` und `offset` Query-Parameter auf POST /adp/offer

**Workaround für v0.2.0:**
Provider mit großen Katalogen SOLLEN die Antwort auf die Requirements des DealRequest filtern und nur passende Offers zurückgeben. Dies reduziert die Response-Größe natürlich. Zusätzlich SOLLEN Provider maximal **100 Offers pro Response** liefern.

**Example für zukünftige v0.3-Implementierung (informativ):**
```http
POST /adp/offer HTTP/1.1
Host: api.provider.com
Authorization: Bearer adp_v2_...

# Query parameters (v0.3 only)
?limit=50&offset=0

---

HTTP/1.1 200 OK
Link: <https://api.provider.com/adp/offer?limit=50&offset=50>; rel="next"
X-ADP-Total-Count: 247

{
  "adp": { ... },
  "offers": [ ... ]
}
```

### 2.7 Health Check (GET /adp/health)

**Beschreibung:** Prüft ob der Provider erreichbar und operational ist.

**Request:**
```http
GET /adp/health HTTP/1.1
Host: api.provider.com
Accept: application/json
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "adp_version": "0.2.0",
  "timestamp": "2026-03-12T10:00:00Z",
  "services": {
    "offer_endpoint": "available",
    "intent_endpoint": "available"
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "degraded",
  "adp_version": "0.2.0",
  "timestamp": "2026-03-12T10:00:00Z",
  "services": {
    "offer_endpoint": "available",
    "intent_endpoint": "unavailable"
  },
  "message": "Intent processing temporarily unavailable"
}
```

**Notes:**
1. **Unauthenticated Endpoint:** Health check is **not authenticated** (no Authorization header required). Rate Limit headers are **optional** on this endpoint.
2. **Purpose:** Used by agents and load balancers to verify provider availability. Not intended as a substitute for proper monitoring.

---

## 3. Error Code Registry

ADP v0.2.0 defines a centralized registry of all error codes used across the protocol. This ensures consistency across all specs (Core, Auth, HTTP Binding) and provides clear semantics for each error condition.

### 3.1 Complete Error Code Table

| Error Code | HTTP Status | Spec Origin | Beschreibung | Retryable | Retry-After |
|-----------|-------------|-------------|-----------|-----------|-------------|
| `INVALID_REQUEST` | 400 Bad Request | Core v0.1.1 | Request format or schema invalid | Nein | — |
| `PROVIDER_UNAVAILABLE` | 500/502/503 | Core v0.1.1 | Provider-side server error | Ja | 60s (default) |
| `EXPIRED` | 400 Bad Request | Core v0.1.1 | DealRequest or DealOffer has expired | Nein | — |
| `VERSION_MISMATCH` | 400 Bad Request | Core v0.1.1 | Unsupported ADP protocol version | Nein | — |
| `RATE_LIMITED` | 429 Too Many Requests | Core v0.1.1 | Rate limit exceeded | Ja | Header: `Retry-After` |
| `NOT_FOUND` | 404 Not Found | Core v0.1.1 | Endpoint or resource not found | Nein | — |
| `UNAUTHORIZED` | 401 Unauthorized | Auth v0.2.0 | Missing or invalid authentication token | Nein | — |
| `FORBIDDEN` | 403 Forbidden | Auth v0.2.0 | Insufficient permissions/scope | Nein | — |
| `INVALID_SIGNATURE` | 401 Unauthorized | Auth v0.2.0 | HMAC signature validation failed (Request Signing) | Nein | — |
| `TOKEN_EXPIRED` | 401 Unauthorized | Auth v0.2.0 | OAuth access token has expired | Ja | Refresh token |

### 3.2 Reference in Other Specs

- **Auth Spec (auth.md):** Refers to this central registry instead of defining duplicate error codes.
- **HTTP Binding (http-binding.md, this document):** Uses error codes from this registry.
- **Core Spec (v0.1.1):** Original definitions of the first 6 error codes.

### 3.3 Semantic Interpretation

**Retryable Errors:**
- `PROVIDER_UNAVAILABLE` — Server temporarily down; retry with exponential backoff
- `RATE_LIMITED` — Quota exhausted; honor `Retry-After` or `X-ADP-RateLimit-Reset` header
- `TOKEN_EXPIRED` — OAuth token needs refresh; obtain new token and retry

**Non-Retryable Errors:**
- `INVALID_REQUEST`, `EXPIRED`, `VERSION_MISMATCH`, `NOT_FOUND` — Fix the request before retrying
- `UNAUTHORIZED`, `FORBIDDEN`, `INVALID_SIGNATURE` — Authentication/authorization issue; user must act

---

## 4. Standard-Header

### 4.1 Request Header

| Header | Pflicht | Format | Beschreibung |
|--------|---------|--------|--------------|
| `Authorization` | Ja (außer Discovery/Health) | `Bearer <token>` | Auth-Token |
| `Content-Type` | Ja | `application/adp+json` | Content-Type |
| `X-ADP-Version` | Ja | `major.minor.patch` | ADP Version |
| `X-ADP-Idempotency-Key` | Optional | UUID v4 | Idempotenz-Key |
| `Accept` | Empfohlen | `application/adp+json` | Akzeptierter Content-Type |

### 4.2 Response Header

| Header | Pflicht | Beschreibung |
|--------|---------|--------------|
| `Content-Type` | Ja | `application/adp+json` |
| `X-ADP-Version` | Ja | ADP Version der Response |
| `X-ADP-RateLimit-Limit` | Ja (nur auth. Endpoints) | Rate Limit Maximum |
| `X-ADP-RateLimit-Remaining` | Ja (nur auth. Endpoints) | Verbleibende Requests |
| `X-ADP-RateLimit-Reset` | Ja (nur auth. Endpoints) | Reset Timestamp |
| `Retry-After` | Bei 429/503 | Sekunden bis Retry |

**Note on Rate Limit Headers:**
Rate Limit headers (`X-ADP-RateLimit-*`) are **required on authenticated endpoints** (POST /adp/offer, POST /adp/intent, any endpoint requiring Authorization header). They are **optional on unauthenticated endpoints** (GET /.well-known/adp.json, GET /adp/health).

---

## 5. Status Codes

### 5.1 Erfolg

| Code | Bedeutung | Wann verwenden |
|------|-----------|----------------|
| `200 OK` | Request erfolgreich | DealOffer(s) zurückgegeben |
| `202 Accepted` | Request akzeptiert, asynchrone Verarbeitung | DealIntent empfangen |

### 5.2 Client-Fehler

| Code | Bedeutung | DealError Code |
|------|-----------|----------------|
| `400 Bad Request` | JSON ungültig oder Schema-Fehler | `INVALID_REQUEST` |
| `401 Unauthorized` | Kein/ungültiger Auth-Token | `UNAUTHORIZED` |
| `403 Forbidden` | Unzureichende Berechtigungen | `FORBIDDEN` |
| `404 Not Found` | Endpoint existiert nicht | `NOT_FOUND` |
| `422 Unprocessable Entity` | Schema valid, aber semantischer Fehler | `INVALID_REQUEST` |
| `429 Too Many Requests` | Rate Limit überschritten | `RATE_LIMITED` |

### 5.3 Server-Fehler

| Code | Bedeutung | DealError Code |
|------|-----------|----------------|
| `500 Internal Server Error` | Unbekannter Server-Fehler | `PROVIDER_UNAVAILABLE` |
| `502 Bad Gateway` | Upstream-Fehler | `PROVIDER_UNAVAILABLE` |
| `503 Service Unavailable` | Wartung/Überlastung | `PROVIDER_UNAVAILABLE` |

### 5.4 Error Response Format

**400 Bad Request:**
```http
HTTP/1.1 400 Bad Request
Content-Type: application/adp+json

{
  "adp": {
    "version": "0.2.0",
    "type": "DealError",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-12T10:00:00Z",
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid request format",
    "field_errors": [
      {
        "field": "request.requirements.task_classes[0]",
        "code": "INVALID_ENUM",
        "message": "Expected one of: general, reasoning, coding, ..."
      }
    ],
    "retryable": false
  }
}
```

**429 Rate Limited:**
```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-ADP-RateLimit-Reset: 2026-03-12T10:01:00Z
Content-Type: application/adp+json

{
  "adp": { ... },
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Try again in 60 seconds.",
    "retryable": true,
    "retry_after_ms": 60000
  }
}
```

---

## 6. Content-Type

### 6.1 application/adp+json

**Media Type:** `application/adp+json`

**Beschreibung:** JSON-Dokumente, die dem ADP-Schema folgen.

**Charset:** UTF-8 (implizit bei JSON)

**Beispiel:**
```http
Content-Type: application/adp+json; version=0.2.0
```

**Hinweis (UPDATED - v0.2.0 Draft Status):** Der Media Type `application/adp+json` ist derzeit **nicht bei IANA registriert**. Eine formale Registration als `application/vnd.apideals.adp+json` ist für die RFC-Submission-Phase geplant. Bis dahin wird `application/adp+json` als De-facto-Standard verwendet.

**Fallback:** Provider SOLLEN zusätzlich `application/json` als Fallback akzeptieren. Dies erhöht die Kompatibilität mit Clients, die Custom Media Types nicht unterstützen.

---

## 7. Version Negotiation

### 7.1 Version Header

Der `X-ADP-Version` Header gibt die verwendete ADP-Version an:

**Request:**
```http
X-ADP-Version: 0.2.0
```

**Response:**
```http
X-ADP-Version: 0.2.0
```

### 7.2 Version Mismatch

Wenn ein Provider die angeforderte Major-Version nicht unterstützt:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/adp+json

{
  "adp": {
    "version": "0.2.0",
    "type": "DealError",
    ...
  },
  "error": {
    "code": "VERSION_MISMATCH",
    "message": "Unsupported ADP version. Supported: 0.1.1, 0.2.0",
    "supported_versions": ["0.1.1", "0.2.0"],
    "retryable": false
  }
}
```

### 7.3 Backwards Compatibility

| Request Version | Provider Support | Verhalten |
|-----------------|------------------|-----------|
| v0.1.1 | Nur v0.2.0 | VERSION_MISMATCH oder v0.1.1 Emulation |
| v0.2.0 | v0.1.1 + v0.2.0 | v0.2.0 Response |
| v0.2.0 | Nur v0.1.1 | VERSION_MISMATCH |

---

## 8. OpenAPI 3.1 Spezifikation

```yaml
openapi: 3.1.0
info:
  title: ADP HTTP API
  version: 0.2.0
  description: |
    HTTP Binding für das apideals Deal Protocol (ADP) v0.2.0

servers:
  - url: https://api.provider.com
    description: Production

paths:
  /.well-known/adp.json:
    get:
      summary: Provider Discovery
      operationId: discovery
      responses:
        '200':
          description: Provider metadata
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Discovery'

  /adp/offer:
    post:
      summary: Request Deal Offers
      operationId: requestOffer
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/adp+json:
            schema:
              $ref: '#/components/schemas/DealRequest'
      responses:
        '200':
          description: Deal Offer(s)
          content:
            application/adp+json:
              schema:
                oneOf:
                  - $ref: '#/components/schemas/DealOffer'
                  - type: array
                    items:
                      $ref: '#/components/schemas/DealOffer'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '429':
          $ref: '#/components/responses/RateLimited'

  /adp/intent:
    post:
      summary: Submit Deal Intent
      operationId: submitIntent
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/adp+json:
            schema:
              $ref: '#/components/schemas/DealIntent'
      responses:
        '202':
          description: Intent accepted
          content:
            application/adp+json:
              schema:
                $ref: '#/components/schemas/DealIntentAck'
        '400':
          $ref: '#/components/responses/BadRequest'
        '401':
          $ref: '#/components/responses/Unauthorized'

  /adp/health:
    get:
      summary: Health Check
      operationId: healthCheck
      responses:
        '200':
          description: Service healthy
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'
        '503':
          description: Service degraded
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HealthResponse'

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: ADP-API-Key

  schemas:
    Discovery:
      type: object
      required: [adp_supported, adp_versions]
      properties:
        discovery_version:
          type: string
          pattern: "^\\d+\\.\\d+\\.\\d+$"
          description: "Version of the Discovery document format (semver, OPTIONAL). Defaults to v0.1.1 if omitted."
          example: "0.2.0"
        adp_supported:
          type: boolean
        adp_versions:
          type: array
          items:
            type: string
        offer_endpoint:
          type: string
          format: uri
        intent_endpoint:
          type: string
          format: uri

    DealRequest:
      type: object
      # Siehe ADP Core Spec

    DealOffer:
      type: object
      # Siehe ADP Core Spec

    DealIntent:
      type: object
      # Siehe ADP Core Spec

    DealIntentAck:
      type: object
      required: [adp, acknowledgment]
      properties:
        adp:
          type: object
          required: [version, type, id, timestamp, correlation_id]
          properties:
            version:
              type: string
              pattern: "^0\\.2\\."
              description: "ADP Protocol version"
            type:
              type: string
              const: "DealIntentAck"
              description: "Message type identifier"
            id:
              type: string
              format: uuid
              description: "Unique message ID (UUIDv4)"
            timestamp:
              type: string
              format: date-time
              description: "Creation timestamp (ISO 8601 UTC)"
            correlation_id:
              type: string
              format: uuid
              description: "Reference to the DealIntent being acknowledged"
        acknowledgment:
          type: object
          required: [status]
          properties:
            status:
              type: string
              enum: [received, processing, confirmed]
              description: "Acknowledgment status"
            next_steps:
              type: string
              description: "Human-readable next steps for the requester"
            reference_id:
              type: string
              description: "Provider-side reference ID for this intent"
            expires_at:
              type: string
              format: date-time
              description: "When this acknowledgment expires (optional)"

    HealthResponse:
      type: object
      required: [status, adp_version, timestamp]
      properties:
        status:
          type: string
          enum: [healthy, degraded, unhealthy]
        adp_version:
          type: string
        timestamp:
          type: string
          format: date-time
        services:
          type: object

  responses:
    BadRequest:
      description: Invalid request
      content:
        application/adp+json:
          schema:
            $ref: '#/components/schemas/DealError'

    Unauthorized:
      description: Authentication required
      content:
        application/adp+json:
          schema:
            $ref: '#/components/schemas/DealError'

    RateLimited:
      description: Rate limit exceeded
      headers:
        Retry-After:
          schema:
            type: integer
        X-ADP-RateLimit-Reset:
          schema:
            type: string
            format: date-time
            description: ISO 8601 UTC timestamp when the rate limit resets
      content:
        application/adp+json:
          schema:
            $ref: '#/components/schemas/DealError'
```

---

## 9. Beispiele

### 9.1 cURL

**Discovery:**
```bash
curl -s https://api.together.xyz/.well-known/adp.json | jq
```

**DealRequest:**
```bash
curl -X POST https://api.provider.com/adp/offer \
  -H "Authorization: Bearer adp_v2_..." \
  -H "Content-Type: application/adp+json" \
  -H "X-ADP-Version: 0.2.0" \
  -d '{
    "adp": {
      "version": "0.2.0",
      "type": "DealRequest",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "timestamp": "2026-03-12T10:00:00Z"
    },
    "request": {
      "requirements": {
        "task_classes": ["reasoning"],
        "modalities": ["text"]
      },
      "budget": {
        "max_cost_per_mtok_input": 3.00,
        "currency": "USD"
      }
    }
  }'
```

### 9.2 Python (requests)

```python
import requests
import uuid
from datetime import datetime, timezone

def request_deal(api_key, provider_url, requirements, budget):
    request_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()
    
    payload = {
        "adp": {
            "version": "0.2.0",
            "type": "DealRequest",
            "id": request_id,
            "timestamp": timestamp,
            "correlation_id": None
        },
        "request": {
            "requirements": requirements,
            "budget": budget
        }
    }
    
    response = requests.post(
        f"{provider_url}/adp/offer",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/adp+json",
            "X-ADP-Version": "0.2.0"
        },
        json=payload
    )
    
    response.raise_for_status()
    return response.json()
```

### 9.3 Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "time"

    "github.com/google/uuid"
)

type ADPHeader struct {
    Version         string    `json:"version"`
    Type            string    `json:"type"`
    ID              string    `json:"id"`
    Timestamp       time.Time `json:"timestamp"`
    CorrelationID   *string   `json:"correlation_id"`
}

type DealRequest struct {
    ADP     ADPHeader   `json:"adp"`
    Request interface{} `json:"request"`
}

func requestDeal(apiKey, providerURL string, req DealRequest) (*http.Response, error) {
    body, err := json.Marshal(req)
    if err != nil {
        return nil, err
    }
    
    httpReq, err := http.NewRequest(
        "POST",
        fmt.Sprintf("%s/adp/offer", providerURL),
        bytes.NewBuffer(body),
    )
    if err != nil {
        return nil, err
    }
    
    httpReq.Header.Set("Authorization", fmt.Sprintf("Bearer %s", apiKey))
    httpReq.Header.Set("Content-Type", "application/adp+json")
    httpReq.Header.Set("X-ADP-Version", "0.2.0")
    
    client := &http.Client{Timeout: 30 * time.Second}
    return client.Do(httpReq)
}
```

---

## 10. Migration von v0.1.1

### 10.1 Breaking Changes

| v0.1.1 | v0.2.0 | Migration |
|--------|--------|-----------|
| Keine HTTP-Spec definiert | Vollständige HTTP Binding Spec | Neue Implementierung |
| Kein Auth-Layer | Auth required | Auth implementieren (siehe auth.md) |
| Discovery nur über `.well-known/adp.json` | Erweitert um Auth-Info | Discovery-Response erweitern |
| Rate Limit Reset: Unix Timestamp | Rate Limit Reset: ISO 8601 UTC | Alle `X-ADP-RateLimit-Reset` auf ISO 8601 konvertieren |

### 10.2 Backwards Compatibility

Provider können v0.1.1 und v0.2.0 parallel unterstützen:

- Anhand des `X-ADP-Version` Headers entscheiden
- Oder: Separate Endpoints (`/v0.1/adp/offer`, `/v0.2/adp/offer`)

### 10.3 Zeitformat-Vereinheitlichung

**v0.2.0 vereinheitlicht alle Zeitangaben auf ISO 8601 UTC.** 

- `X-ADP-RateLimit-Reset` war in früheren Entwürfen ein Unix Timestamp (integer)
- Ab v0.2.0 ist es ein ISO 8601 String mit dem Format `YYYY-MM-DDTHH:MM:SSZ`
- Clients müssen entsprechend angepasst werden (String-Parsing statt Integer-Konversion)

**Beispiel Migration:**
```
v0.1.1 (alt):  X-ADP-RateLimit-Reset: 1712346000
v0.2.0 (neu):  X-ADP-RateLimit-Reset: 2026-03-12T10:00:00Z
```

---

## Appendix: Zusammenfassung

| Feature | Status |
|---------|--------|
| Discovery (/.well-known/adp.json) | Required |
| DealRequest/DealOffer (/adp/offer) | Required |
| DealIntent (/adp/intent) | Required |
| Health Check (/adp/health) | Recommended |
| Content-Type: application/adp+json | Required |
| X-ADP-Version Header | Required |
| Idempotency Key | Optional |

---

## Changelog

### 2026-03-12 — Critical fixes

**Fix 1: Endpoint Path Consistency (v0.1.1 vs v0.2.0)**
- Standardized endpoint paths to singular form: `/adp/offer`, `/adp/intent`, `/adp/health`
- Added `models_endpoint` and `static_offers_url` as optional fields in Discovery for v0.1.1 backwards compatibility
- Added migration note: "v0.1.1 used partial plural endpoints. v0.2.0 standardizes on singular."

**Fix 2: Formal DealIntentAck Specification (New Section 2.5)**
- Added complete formal specification of `DealIntentAck` message type (5th core message type)
- Field reference table with all required and optional fields
- JSON Schema definition
- OpenAPI 3.1 schema update (Section 8) with full DealIntentAck schema
- Added note: "New message type in v0.2.0 — not present in v0.1.1"

**Fix 3: Central Error Code Registry (New Section 3)**
- Created unified error code registry with all 10 error codes from Core v0.1.1 and Auth v0.2.0
- Table includes: HTTP Status, origin spec, description, retryable status, retry-after handling
- Semantic interpretation for retryable vs. non-retryable errors
- Auth spec now references this central registry (no more duplicate definitions)

**Fix 4: Rate Limit Headers Scope Clarification**
- Clarified: Rate Limit headers are **required on authenticated endpoints** (POST /adp/offer, POST /adp/intent)
- Clarified: Rate Limit headers are **optional on unauthenticated endpoints** (GET /.well-known/adp.json, GET /adp/health)
- Updated Response Header table (Section 4.2) with conditional requirement note
- Added explicit notes to Discovery (2.2) and Health Check (2.7) sections

**Fix 6: `application/adp+json` Media Type — IANA-Status und Fallback klargestellt**
- Updated Section 6.1 mit Hinweis auf fehlende IANA-Registrierung
- Added note: Formale Registration als `application/vnd.apideals.adp+json` geplant für RFC-Phase
- Added Fallback-Empfehlung: Provider SOLLEN `application/json` zusätzlich akzeptieren
- Erhöht Kompatibilität mit älteren Clients

**Fix 11: Discovery nicht versioniert**
- Added `discovery_version` field (string, semver, OPTIONAL) to Discovery response (Section 2.2)
- Defaults to v0.1.1 format if omitted (backwards compatibility)
- Updated OpenAPI Schema (Section 8) with new `discovery_version` property
- Agents can now determine correct parsing logic based on `discovery_version`

**Fix 12: Pagination ungelöst**
- Added new Section 2.6: "Pagination" with Status: Deferred to v0.3
- Documented future v0.3 approach: Link headers (RFC 8288), X-ADP-Total-Count, limit/offset parameters
- v0.2.0 workaround: Provider SHOULD filter responses based on DealRequest requirements and limit to 100 Offers per response
- Prevents huge response payloads for providers with 500+ models

**Fix 14: Zeitangaben auf ISO 8601 vereinheitlichen**
- Changed `X-ADP-RateLimit-Reset` from Unix Timestamp to ISO 8601 UTC in all examples (Sections 2.3, 5.4)
- Updated Rate Limited (429) response example with ISO 8601 timestamp
- Updated OpenAPI RateLimited response schema: Header X-ADP-RateLimit-Reset now `string` with `format: date-time`
- Added migration note (Section 10.3): Detailed timestamp format change explanation
- All three ADP specs now use ISO 8601 UTC consistently

**Consistency fixes:** Added Discovery-Versioning, Pagination-Section, Zeitformat-Vereinheitlichung

*Ende der HTTP Binding Spezifikation v0.2.0*
