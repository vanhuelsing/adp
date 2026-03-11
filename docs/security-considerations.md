# Security Considerations

**Version:** 0.1.1-draft  
**Status:** Draft  
**Last Updated:** 2026-03-11

---

## 1. Threat Model

Das ADP (apideals Deal Protocol) v0.1.1 ist für die maschinelle Kommunikation zwischen Agenten und API-Providern konzipiert. Folgende Bedrohungsakteure und Angriffsvektoren wurden identifiziert:

### 1.1 Agent Spoofing
Ein Angreifer könnte versuchen, sich als legitimer Agent auszugeben, um:
- Falsche Volumen- oder Budget-Angaben zu machen (Marktmanipulation)
- Gegenangebote zu sammeln ohne ernsthaftes Interesse
- Informationen über Wettbewerber zu sammeln

**Risiko:** Mittel  
**Auswirkung:** Verzerrte Marktdaten, Ressourcenverschwendung

### 1.2 Provider Impersonation
Ein bösartiger Akteur könnte sich als legitimer Provider ausgeben, um:
- Gefälschte Angebote zu unterbreiten (spätere Preisänderungen)
- Phishing-URLs in `activation.redirect_url` zu platzieren
- Falsche Compliance-Angaben (z.B. `gdpr_compliant: true`) zu machen

**Risiko:** Hoch  
**Auswirkung:** Datenverlust, regulatorische Verstöße, finanzielle Schäden

### 1.3 Replay-Attacken
ADP-Nachrichten enthalten keinen Replay-Schutz. Ein Angreifer könnte:
- Gültige `DealIntent`-Nachrichten wiederverwenden
- `DealRequest`-Nachrichten wiederholen (DoS/Ressourcenverschwendung)
- Abgelaufene Angebote erneut einreichen

**Risiko:** Mittel  
**Auswirkung:** Unbeabsichtigte Vertragsbindungen, Ressourcen-Überlastung

### 1.4 Denial of Service (DoS)
Angriffe auf die Verfügbarkeit:
- Massenhaftes Senden von `DealRequest`-Nachrichten
- Übermäßig große Payloads (JSON-Bombing)
- Verschachtelte Preis-Tiers zur CPU-Überlastung

**Risiko:** Mittel  
**Auswirkung:** Service-Unterbrechung, erhöhte Kosten

### 1.5 Man-in-the-Middle (MitM)
Da v0.1 transport-agnostisch ist, kann bei unsicheren Transportkanälen:
- Angebotspreise manipuliert werden
- Redirect-URLs umgeleitet werden
- Compliance-Daten verfälscht werden

**Risiko:** Hoch (bei unsicherem Transport)  
**Auswirkung:** Finanzbetrug, Datenabgriff

---

## 2. Authentication & Authorization

### 2.1 Out-of-Scope für v0.1

ADP v0.1 bewusst **keine** Authentifizierung oder Autorisierung:

- Keine API-Keys im Protokoll-Schema
- Keine Signatur-Mechanismen
- Keine Identity-Provider-Integration
- Keine OAuth-Flows
- Keine mTLS-Anforderungen

**Begründung:**
> "Transport layer (HTTP, WebSocket) — transport-agnostic"  
> "Authentication/authorization — v0.2"

Das Protokoll definiert ausschließlich Nachrichtenformate. Sicherheitsschichten sind implementierungsspezifisch zu lösen.

### 2.2 Empfohlene Workarounds für v0.1

Bis v0.2 verfügbar ist, sollten Implementierer folgendes etablieren:

| Mechanismus | Anwendung | Implementierung |
|-------------|-----------|-----------------|
| **TLS 1.3** | Alle Transporte | Verbindungsverschlüsselung obligatorisch |
| **API-Keys** | Provider-Endpoints | Im HTTP-Header, nicht im JSON-Body |
| **IP-Whitelisting** | B2B-Szenarien | Statische IP-Allowlists |
| **Rate Limiting** | Beide Seiten | Siehe Abschnitt 4 |

### 2.3 Geplant für v0.2

- **JWS-Signaturen** (JSON Web Signature) für Nachrichtenintegrität
- **JWT-basierte Claims** für Agent- und Provider-Identity
- **OAuth 2.0 / mTLS** für Transport-Authentifizierung
- **Verifiable Credentials** für Compliance-Behauptungen

---

## 3. Message Integrity

### 3.1 Keine Signaturen in v0.1

Das Protokoll enthält keine kryptographischen Signaturen:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "uuid",
    "timestamp": "2026-03-10T12:00:00Z"
    // Kein "signature" Feld
  }
}
```

**Risiken ohne Signaturen:**
1. **Preis-Manipulation:** Ein MitM-Angreifer könnte Angebotspreise ändern
2. **Terms-Manipulation:** `terms_url` oder `valid_until` könnten modifiziert werden
3. **Identity-Spoofing:** Jeder kann Nachrichten mit beliebiger `agent_id` oder `provider_id` erstellen

### 3.2 Empfohlene Workarounds

| Risiko | Workaround |
|--------|------------|
| Preis-Manipulation | TLS 1.3 mit Zertifikat-Pinning |
| Terms-Manipulation | HTTPS für alle URLs, Domain-Validierung |
| Identity-Spoofing | API-Keys + Out-of-Band-Identity-Verifikation |

### 3.3 Validierungs-Prüfpunkte

Implementierer sollten folgende Validierungen durchführen:

```python
def validate_offer_integrity(offer):
    # 1. Preis-Plausibilität
    assert offer.pricing.base.input_per_mtok > 0
    assert offer.pricing.base.output_per_mtok > 0
    
    # 2. Zeitliche Gültigkeit
    assert offer.valid_until > offer.valid_from
    assert offer.valid_until > now()
    
    # 3. URL-Validierung
    assert offer.terms_url.startswith("https://")
    assert offer.provider.url.startswith("https://")
    
    # 4. Provider-Konsistenz
    assert offer.provider.provider_id.isalnum()  # Keine Sonderzeichen
```

---

## 4. Rate Limiting

### 4.1 Standard-Mechanismus

ADP v0.1 definiert einen standardisierten Rate-Limit-Error:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealError",
    "id": "...",
    "timestamp": "2026-03-10T12:00:01Z"
  },
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded. Please retry after backoff.",
    "retryable": true,
    "retry_after_ms": 60000
  }
}
```

### 4.2 Empfohlene Rate-Limit-Strategien

**Für Provider:**

| Endpoint | Limit | Fenster |
|----------|-------|---------|
| `/.well-known/adp.json` | 100 req/min | IP-basiert |
| DealRequest-Endpunkt | 60 req/min | API-Key-basiert |
| DealIntent-Endpunkt | 10 req/min | API-Key-basiert |

**Für Agents:**

```python
class ADPRateLimiter:
    def __init__(self):
        self.backoff_ms = 1000
        self.max_backoff_ms = 60000
    
    def on_rate_limited(self, retry_after_ms=None):
        if retry_after_ms:
            sleep(retry_after_ms / 1000)
        else:
            sleep(self.backoff_ms / 1000)
            self.backoff_ms = min(self.backoff_ms * 2, self.max_backoff_ms)
    
    def on_success(self):
        self.backoff_ms = 1000  # Reset
```

### 4.3 Rate-Limit-Header (Best Practice)

Bei HTTP-Transport sollten Provider diese Header senden:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1647000000
```

---

## 5. Data Validation

### 5.1 Schema-Validierung

Alle ADP-Nachrichten müssen gegen ein JSON Schema validiert werden:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["adp"],
  "properties": {
    "adp": {
      "type": "object",
      "required": ["version", "type", "id", "timestamp"],
      "properties": {
        "version": { "type": "string", "pattern": "^0\\.1\\.\\d+$" },
        "type": { "enum": ["DealRequest", "DealOffer", "DealIntent", "DealError"] },
        "id": { "type": "string", "format": "uuid" },
        "timestamp": { "type": "string", "format": "date-time" }
      }
    }
  }
}
```

### 5.2 Input-Validierung

**Für String-Felder:**
- `agent_id`: Max. 256 Zeichen, erlaubt: `a-z0-9:._-`
- `provider_id`: Max. 64 Zeichen, erlaubt: `a-z0-9-`
- `email`: RFC 5322 konforme Validierung

**Für Numerische Felder:**
- Preise: Nicht-negativ, max. 6 Dezimalstellen
- Token-Zahlen: Positiv, max. 10^15
- Prozentwerte: 0.0 - 100.0

**Für URLs:**
- Nur HTTPS-Protokoll erlauben
- Keine Loopback-Adressen (127.0.0.1, localhost)
- Keine private IP-Ranges (10.0.0.0/8, 192.168.0.0/16)

### 5.3 Max. Payload-Size

**Empfohlene Limits:**

| Nachrichtentyp | Max. Größe |
|----------------|------------|
| DealRequest | 100 KB |
| DealOffer | 250 KB |
| DealIntent | 50 KB |
| DealError | 10 KB |

**Begründung:**
- `DealOffer` kann umfangreiche Pricing-Tiers enthalten
- `DealError` sollte minimal bleiben (Stacktraces entfernen)

**Implementierung:**

```python
MAX_PAYLOAD_SIZES = {
    "DealRequest": 100 * 1024,
    "DealOffer": 250 * 1024,
    "DealIntent": 50 * 1024,
    "DealError": 10 * 1024
}

def validate_payload_size(payload_bytes, message_type):
    max_size = MAX_PAYLOAD_SIZES.get(message_type, 100 * 1024)
    if len(payload_bytes) > max_size:
        raise PayloadTooLarge(f"{message_type} exceeds {max_size} bytes")
```

### 5.4 Schutz vor JSON-Bombing

**Schutzmaßnahmen:**

```python
import json

def safe_parse_adp(payload):
    # 1. Tiefe begrenzen
    parsed = json.loads(payload)
    
    def check_depth(obj, depth=0):
        if depth > 20:
            raise ValueError("JSON depth exceeded")
        if isinstance(obj, dict):
            for v in obj.values():
                check_depth(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                check_depth(item, depth + 1)
    
    check_depth(parsed)
    
    # 2. Array-Größen begrenzen
    if len(parsed.get("offer", {}).get("pricing", {}).get("tiers", [])) > 100:
        raise ValueError("Too many pricing tiers")
    
    return parsed
```

---

## 6. GDPR / Compliance

### 6.1 Data Retention

Das `request_ttl_hours` Feld in `DealRequest` ist explizit für GDPR-Art. 17 (Recht auf Löschung) vorgesehen:

```json
{
  "request": {
    "request_ttl_hours": 24
  }
}
```

**Implementierungs-Anforderungen:**

| TTL | Anwendungsfall |
|-----|----------------|
| 1-24h | Kurzfristige Preisvergleiche |
| 7 Tage | Verhandlungen mit Follow-up |
| 30 Tage | Langfristige Ausschreibungen |

**Provider müssen:**
1. Nach Ablauf der TTL alle personenbezogenen Daten löschen
2. Nur aggregierte/anonymisierte Daten für Statistiken behalten
3. Löschnachweise dokumentieren (Audit-Trail)

### 6.2 Keine PII in Beispielen

Alle Beispiele in der Spezifikation verwenden:
- Fiktive `agent_id` (z.B. `agent:acme:bot`)
- Platzhalter-E-Mails (z.B. `api@example.com`)
- Keine echten Namen oder Unternehmen

**Verbotene Daten in Produktions-Requests:**
- Echte Personennamen
- Echte E-Mail-Adressen
- Telefonnummern
- IP-Adressen
- API-Keys oder Secrets

### 6.3 Compliance-Claims

Compliance-Angaben sind selbstdeklariert:

```json
{
  "compliance": {
    "compliance_verified_by": "self-declared",
    "gdpr_compliant": true
  }
}
```

**Empfehlung:** Agents sollten `compliance_verified_by: "third-party"` oder `"apideals-verified"` bevorzugen. Bei `self-declared` ist eine manuelle Verifikation erforderlich.

### 6.4 Data Processing Agreement (DPA)

Das Feld `dpa_available` zeigt an, ob ein DPA verfügbar ist:

```json
{
  "compliance": {
    "dpa_available": true
  }
}
```

**Empfohlener Workflow:**
1. Agent prüft `dpa_available: true`
2. Vor `DealIntent` wird DPA unterzeichnet
3. `DealIntent.requires_human_confirmation: true` setzen

---

## 7. Recommendations for v0.2

### 7.1 JWS/JWT Signaturen

**Vorschlag:** JSON Web Signature (RFC 7515) für Nachrichtenintegrität:

```json
{
  "adp": {
    "version": "0.2.0",
    "type": "DealOffer",
    "id": "...",
    "timestamp": "...",
    "signature": {
      "alg": "ES256",
      "kid": "provider-key-2026",
      "jws": "eyJhbGciOiJFUzI1NiJ9..."
    }
  }
}
```

**Verifikations-Workflow:**
1. Agent besorgt Provider-Public-Key über `/.well-known/jwks.json`
2. JWS-Signatur über ADP-Nachricht wird verifiziert
3. Bei Fehlschlag: Nachricht ablehnen

### 7.2 Nonces für Replay-Protection

**Vorschlag:** Einmalige Nonces pro Nachricht:

```json
{
  "adp": {
    "version": "0.2.0",
    "type": "DealIntent",
    "id": "...",
    "nonce": "uuid-v4",
    "timestamp": "..."
  }
}
```

**Implementierung:**
- Provider speichern gesehene Nonces für 24h
- Doppelte Nonces werden als Replay-Angriff abgelehnt
- Zeitstempel-Validierung: ±5 Minuten Toleranz

### 7.3 Certificate Pinning

Für Provider-Discovery und API-Endpoints:

```python
import hashlib

PINNED_CERTS = {
    "api.provider.com": "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
    "provider.com": "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
}

def verify_cert_pin(hostname, cert_der):
    expected_pin = PINNED_CERTS.get(hostname)
    if expected_pin:
        actual_pin = "sha256/" + base64.b64encode(
            hashlib.sha256(cert_der).digest()
        ).decode()
        if actual_pin != expected_pin:
            raise CertificatePinError(f"Pin mismatch for {hostname}")
```

### 7.4 Mutual TLS (mTLS)

**Vorschlag für B2B-Szenarien:**

```json
{
  "adp": {
    "version": "0.2.0",
    "type": "DealRequest",
    "id": "...",
    "auth": {
      "type": "mtls",
      "client_cert_cn": "agent.acme.com",
      "client_cert_serial": "..."
    }
  }
}
```

**Vorteile:**
- Starke Kryptographie
- Keine Secrets im JSON
- Automatische Identity-Binding

### 7.5 Compliance-Verifizierung

**Vorschlag:** Verifiable Credentials für Compliance-Claims:

```json
{
  "compliance": {
    "compliance_verified_by": "verifiable-credential",
    "credential": {
      "type": ["VerifiableCredential", "GDPRComplianceCredential"],
      "issuer": "did:web:certifier.eu",
      "proof": { "...": "..." }
    }
  }
}
```

---

## Appendix A: Security Checklist

### Für Provider

- [ ] TLS 1.3 erforderlich
- [ ] Rate Limiting implementiert
- [ ] JSON-Schema-Validierung aktiv
- [ ] Payload-Size-Limits gesetzt
- [ ] `request_ttl_hours` respektiert
- [ ] Keine PII in Logs
- [ ] `terms_url` und `redirect_url` validiert (HTTPS)

### Für Agents

- [ ] Nur HTTPS-Endpoints akzeptieren
- [ ] Zertifikate validieren
- [ ] Rate-Limit-Backoff implementiert
- [ ] Angebotspreise plausibilisieren
- [ ] `valid_until` prüfen
- [ ] Compliance-Claims verifizieren (außerhalb von ADP)

---

*End of Security Considerations v0.1.1*
