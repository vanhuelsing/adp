# ADP v0.2.0 — Master Roadmap

**Projekt:** apideals.ai / ADP Spec v0.2.0  
**Version:** 0.2.0-v1  
**Erstellt:** 2026-03-12  
**Letztes Update:** 2026-03-12 18:38 UTC  
**Autor:** Luca (🦊) — Projekt-Koordination  
**Status:** 🟡 AT RISK (Multimodal Pricing ausstehend, alles andere ON TRACK)

---

## 🎯 Vision

ADP v0.2.0 macht das Deal Protocol production-ready: Auth, HTTP Binding, Multimodal Pricing — und SDKs für Python + Go. Gleichzeitig bereiten wir die Etablierung als offener Standard vor.

---

## 📊 Executive Summary

| Workstream | Status | Owner | ETA | Kommentar |
|------------|--------|-------|-----|----------|
| **WS1: v0.2.0 Spec** | 🟡 AT RISK | Protocol Architect | Freitag 14.03 | Auth ✅, HTTP ✅, Multimodal ⏳, Schemas ⏳ |
| **WS2: SDKs** | 🟡 AT RISK | Backend Dev | Woche 4 | Blockiert auf WS1 Finalisierung |
| **WS3: RFC/Standard** | 🟢 ON TRACK | Consultant | Woche 6 | Kann parallel laufen |

**Kritische Abhängigkeit:** SDKs (WS2) blockiert auf Spec-Finalisierung (WS1)

---

## 🚀 Workstream 1: v0.2.0 Spec Planung

### Ziel
Auth, HTTP Binding, Multimodal Pricing für ADP v0.2.0 definieren — die Basis für alle SDK-Implementierungen.

### Deliverables

#### 1.1 Auth-Spezifikation (`spec/v0.2/auth.md`)
**Rolle:** Protocol Architect  
**Status:** 🟢 ON TRACK

| Feature | Priorität | Beschreibung |
|---------|-----------|--------------|
| API Key Auth | P0 | `Authorization: Bearer adp_<key>` Header-Format |
| OAuth 2.0 | P1 | Client Credentials Flow für Enterprise |
| Request Signing | P2 | HMAC-SHA256 für Integrität (optional) |
| Rate Limit Headers | P1 | `X-ADP-RateLimit-*` Standard-Header |

**Entscheidungen:**
- ✅ **API Keys als Primary:** Einfacher für Anbieter, 80% der Use-Cases
- ✅ **OAuth 2.0 als Secondary:** Für Enterprise/SSO-Szenarien
- ✅ **Kein eigenes ADP-Auth:** Standards nutzen, nicht erfinden

#### 1.2 HTTP Binding (`spec/v0.2/http-binding.md`)
**Rolle:** Protocol Architect  
**Status:** 🟢 ON TRACK

```
POST /.well-known/adp/offer
Content-Type: application/adp+json
Authorization: Bearer <token>
X-ADP-Version: 0.2.0

{ "adp": { "type": "DealRequest", ... } }
```

| Endpoint | Methode | Zweck |
|----------|---------|-------|
| `/.well-known/adp.json` | GET | Discovery (bestehend) |
| `/adp/offer` | POST | DealRequest → DealOffer(s) |
| `/adp/intent` | POST | DealIntent senden |
| `/adp/health` | GET | Provider-Health-Check |

**Status Codes:**
- `200` — Success (auch bei leerem Offer-Array)
- `400` — Invalid Request (JSON + DealError Body)
- `401` — Unauthorized
- `429` — Rate Limited (Retry-After Header)
- `422` — Semantic Error (Schema valid, aber Logikfehler)

#### 1.3 Multimodal Pricing (`spec/v0.2/pricing-multimodal.md`)
**Rolle:** Protocol Architect  
**Status:** 🔴 BLOCKED (Nicht gestartet)

**Neue Pricing-Units:**

| Modality | Unit | Beispiel-Anbieter |
|----------|------|-------------------|
| Image Input | $/megapixel | GPT-4o Vision |
| Image Output | $/image | DALL-E, Midjourney |
| Audio Input | $/minute | Whisper |
| Audio Output | $/character | ElevenLabs TTS |
| Video Input | $/frame oder $/second | Gemini 2.0 |

**Schema-Erweiterung:**
```json
{
  "pricing": {
    "modalities": {
      "text": { "input_per_mtok": 2.00, "output_per_mtok": 10.00 },
      "image_input": { "per_megapixel": 0.50 },
      "image_output": { "per_image": 0.04, "per_megapixel": 0.10 },
      "audio_input": { "per_minute": 0.006 },
      "audio_output": { "per_character": 0.000015 }
    }
  }
}
```

#### 1.4 JSON Schemas
**Rolle:** Protocol Architect  
**Status:** 🟡 AT RISK (Warten auf Multimodal-Pricing Spec)

| Schema | Status | Abhängigkeit |
|--------|--------|------------|
| `adp-header.schema.json` | ✅ v0.1.1 vorhanden | Keine |
| `deal-request.schema.json` | 🔄 Update für v0.2 | Auth-Spec fertig |
| `deal-offer.schema.json` | ⏳ Multimodal-Pricing | Pricing-Spec fertig |
| `auth.schema.json` | ✅ Entwurf vorhanden | Auth-Spec fertig |
| `http-binding.schema.json` | ✅ OpenAPI Draft | HTTP-Spec fertig |

### Timeline WS1

| Phase | Dauer | Deliverable |
|-------|-------|-------------|
| Auth-Spec | 2 Tage | `auth.md` + Beispiele |
| HTTP-Binding | 2 Tage | `http-binding.md` + OpenAPI Spec |
| Multimodal-Pricing | 2 Tage | `pricing-multimodal.md` |
| Schemas | 2 Tage | Alle JSON Schemas validiert |
| Review | 1 Tag | Internes Review |
| **Gesamt** | **9 Tage** | **Woche 2 (Freitag)** |

---

## 🛠️ Workstream 2: SDK-Erweiterung

### Ziel
Python SDK und Go SDK bauen — beide basierend auf ADP v0.2.0 Spec.

⚠️ **KRITISCHE ABHÄNGIGKEIT:** SDKs können erst finalisiert werden, wenn WS1 (Spec) abgeschlossen ist. Jetzt: Vorbereitung & Interface-Design.

### 2.1 Python SDK (`sdk/python/`)
**Rolle:** Backend Dev  
**Status:** 🟡 AT RISK (wartet auf Spec)

**Requirements:**
- pip-installierbar: `pip install apideals`
- Python 3.9+ Support
- Async + Sync APIs (asyncio + synchronous wrapper)
- Pydantic v2 Models
- 100% Type Hints
- pytest + coverage >90%

**API-Design (Draft):**
```python
import apideals
from apideals import DealRequest, DealOffer

# Sync
client = apideals.Client(api_key="adp_...")
offers = client.request_deal(
    requirements={"task_classes": ["reasoning"], ...}
)

# Async
async with apideals.AsyncClient(api_key="adp_...") as client:
    offers = await client.request_deal(...)
```

**Module-Struktur:**
```
apideals/
├── __init__.py
├── client.py          # Sync + Async Client
├── models.py          # Pydantic Models
├── validator.py       # Schema-Validierung
├── pricing.py         # Pricing-Calculator
├── auth.py            # Auth-Handler
└── exceptions.py      # Custom Exceptions
```

### 2.2 Go SDK (`sdk/go/`)
**Rolle:** Backend Dev  
**Status:** 🟡 AT RISK (wartet auf Spec)

**Requirements:**
- `go get github.com/apideals/adp-go`
- Idiomatic Go (Interfaces, Context, Error-Handling)
- Go 1.21+
- 100% Test Coverage

**API-Design (Draft):**
```go
package main

import (
    "context"
    "github.com/apideals/adp-go"
)

func main() {
    client := adp.NewClient("adp_...")
    
    req := &adp.DealRequest{
        Requirements: &adp.Requirements{
            TaskClasses: []string{"reasoning"},
        },
    }
    
    offers, err := client.RequestDeal(context.Background(), req)
    // ...
}
```

**Package-Struktur:**
```
adp-go/
├── client.go          # HTTP Client
├── types.go           # Structs + Interfaces
├── validator.go       # JSON Schema Validierung
├── pricing.go         # Pricing Calculator
├── auth.go            # Auth-Handler
└── examples/
    ├── basic/main.go
    └── multimodal/main.go
```

### Timeline WS2

| Phase | Dauer | Abhängigkeit |
|-------|-------|--------------|
| Interface-Design | 3 Tage | WS1 Draft verfügbar |
| Python SDK Core | 4 Tage | WS1 final |
| Go SDK Core | 4 Tage | WS1 final |
| Tests & Docs | 3 Tage | — |
| PyPI / Go Modules Publish | 1 Tag | — |
| **Gesamt** | **15 Tage** | **Woche 4 (Freitag)** |

---

## 📝 Workstream 3: Spec-Veröffentlichung

### Ziel
ADP Spec als RFC/Standard etablieren — Reputation, Adoption, Langzeitwirkung.

### 3.1 IETF RFC-Prozess
**Rolle:** Consultant  
**Status:** 🟢 ON TRACK

**Research-Fragen:**
1. Ist ADP im Scope eines IETF Internet-Draft?
2. Welche Working Group? (httpapi? oauth? neue?)
3. Timeline: Wie lange dauert RFC-Publikation?
4. Chancen auf Akzeptanz?

**Optionen:**
| Weg | Aufwand | Chancen | Timeline |
|-----|---------|---------|----------|
| **IETF Internet-Draft** | Hoch | Mittel | 12-24 Monate |
| **W3C Community Group** | Mittel | Gut | 6-12 Monate |
| **GitHub + Blogpost** | Niedrig | Hoch (kurzfristig) | Sofort |
| **ISO/IEC JTC 1** | Sehr hoch | Gering | 24+ Monate |

**Empfehlung:**
- **Sofort:** GitHub + Blogpost → "De-facto Standard" etablieren
- **Parallel:** W3C Community Group evaluieren
- **Optional:** IETF Draft als Langzeit-Option

### 3.2 GitHub + Community-Standard
**Rolle:** Consultant  
**Status:** 🟢 ON TRACK

**Deliverables:**
1. **Blogpost:** "Why ADP? The Missing Protocol for AI API Deals"
2. **Hacker News Launch:** Show HN post
3. **Reddit:** r/MachineLearning, r/selfhosted
4. **Provider-Integrations:** 3-5 Anbieter als Launch-Partner
5. **Reference Implementations:** apideals.ai als Showcase

### 3.3 W3C Community Group
**Rolle:** Consultant  
**Status:** 🟢 ON TRACK

**Schritte:**
1. Community Group Proposal erstellen
2. 5+ Unterstützer finden (Organisationen)
3. Bei W3C einreichen
4. CG Charter definieren

### Timeline WS3

| Phase | Dauer | Deliverable |
|-------|-------|-------------|
| IETF Research | 2 Tage | Report mit Empfehlung |
| W3C Evaluierung | 2 Tage | CG Proposal Draft |
| GitHub-Strategie | 2 Tage | Community-Plan |
| Blogpost Draft | 2 Tage | "Why ADP?" Artikel |
| Launch-Plan | 2 Tage | Timeline + Kanäle |
| **Gesamt** | **10 Tage** | **Woche 3-6** |

---

## 🔗 Abhängigkeiten & Kritische Pfade

```
Woche 1        Woche 2        Woche 3        Woche 4        Woche 5        Woche 6
   |              |              |              |              |              |
   ├─[WS1: Auth Spec]───────────┤              │              │              │
   ├─[WS1: HTTP Binding]───────┤              │              │              │
   ├─[WS1: Multimodal]─────────┤              │              │              │
   │              ├─[WS1: Schemas]─────────────┤              │              │
   │              │              ├─[WS2: Python SDK]──────────┤              │
   │              │              ├─[WS2: Go SDK]──────────────┤              │
   │              │              │              ├─[WS2: Publish]─────────────┤
   ├─[WS3: Research]────────────┤              │              │              │
   │              ├─[WS3: GitHub Strategy]─────┤              │              │
   │              │              │              ├─[WS3: Blogpost]────────────┤
   │              │              │              │              ├─[WS3: Launch]┤
```

**Kritische Pfad:**
1. WS1 (Spec) muss Woche 2 fertig sein
2. WS2 (SDKs) braucht WS1 → frühestens Woche 4
3. WS3 (RFC) ist parallel möglich

---

## 👥 Rollen-Zuordnung

| Workstream | Rolle | Datei | Modell |
|------------|-------|-------|--------|
| **WS1: Auth Spec** | Protocol Architect | `apideals/roles/protocol-architect.md` | Opus |
| **WS1: HTTP Binding** | Protocol Architect | `apideals/roles/protocol-architect.md` | Opus |
| **WS1: Multimodal** | Protocol Architect | `apideals/roles/protocol-architect.md` | Opus |
| **WS2: Python SDK** | Backend Dev | `Luca/roles/backend-dev.md` | Kimi/Sonnet |
| **WS2: Go SDK** | Backend Dev | `Luca/roles/backend-dev.md` | Kimi/Sonnet |
| **WS3: RFC Research** | Consultant | `Luca/roles/consultant.md` | Opus |
| **WS3: Community Strategy** | Consultant | `Luca/roles/consultant.md` | Opus |

---

## 📋 Nächste Aktionen — 48h Roadmap (12.03 – 14.03)

### 🚨 KRITISCHER PFAD — HEUTE (12.03 18:38 UTC)

**[SOFORT] 1. Multimodal Pricing Spec finalisieren**
- **Rolle:** Protocol Architect
- **Input:** Bestehende Draft-Struktur aus Roadmap
- **Deliverable:** `concepts/spec-v0.2/pricing-multimodal.md`
- **Abhängigkeit:** Keine (kann parallel zu Reviews laufen)
- **Zeitbudget:** 3-4 Stunden
- **Action:** Subagent spawnen mit Prompt "ADP v0.2.0: Multimodal Pricing Specification"

**[PARALLEL] 2. Auth & HTTP Binding Specs finalisieren**
- **Rolle:** Protocol Architect
- **Input:** Existierende Drafts (`auth.md`, `http-binding.md`)
- **Task:** 
  - Überprüfe auf Vollständigkeit
  - Ergänze Fehlendes (z.B. Error-Handling-Edge-Cases)
  - Review gegen ADP v0.1.1 Core-Spec auf Konsistenz
- **Deliverable:** Finale Versionen ohne "draft" Tag
- **Zeitbudget:** 2 Stunden
- **Action:** Subagent spawnen mit Prompt "ADP v0.2.0: Finalize Auth & HTTP Binding Specs"

### 📋 MORGEN (13.03)

**3. JSON Schemas aktualisieren**
- **Rolle:** Protocol Architect / Backend Dev
- **Input:** Finale Specs von Punkt 1-2
- **Deliverable:** Alle 5 Schemas validiert gegen Beispiele
  - `auth.schema.json`
  - `http-binding.schema.json`
  - `pricing-multimodal.schema.json` (NEU)
  - Update `deal-request.schema.json`
  - Update `deal-offer.schema.json`
- **Validierung:** Jedes Schema mit ≥3 Beispielen testen (Go `ajv` CLI)
- **Zeitbudget:** 3-4 Stunden
- **Action:** Subagent spawnen mit Prompt "ADP v0.2.0: Generate & Validate JSON Schemas"

**4. Review & Sign-off vorbereiten**
- **Rolle:** Luca (du)
- **Input:** Alle Specs + Schemas
- **Task:**
  - Lese Multimodal Pricing Spec komplett durch
  - Prüfe auf Konsistenz mit Auth- & HTTP-Specs
  - Markiere offene Fragen für Dani
  - Erstelle Review-Checklist für QA Engineer
- **Deliverable:** `review-checklist.md` mit:
  - [ ] Backward-Compatibility zu v0.1.1?
  - [ ] Alle Error-Cases behandelt?
  - [ ] Alle Provider-Use-Cases covered?
  - [ ] JSON Schemas validieren?
- **Zeitbudget:** 2 Stunden
- **Keine Subagent-Delegation nötig**

### 🎯 FREITAG (14.03)

**5. QA Engineer Sign-off**
- **Rolle:** QA Engineer
- **Input:** Alle Specs + Schemas + Review-Checklist
- **Task:** Volle QA-Durchführung:
  - JSON Schemas gegen >10 Test-Cases validieren
  - Auth-Flows durchspielen (API Key, OAuth, Signing)
  - HTTP Status-Codes gegen Spec überprüfen
  - Multimodal Pricing gegen Provider-Realität prüfen (GPT-4V, DALL-E, Whisper)
  - Backward-Compatibility-Check
- **Deliverable:** QA-Report mit Go/No-Go für Release
- **Zeitbudget:** 4-5 Stunden
- **Action:** Subagent spawnen mit Prompt "ADP v0.2.0: Full QA Review"

**6. Dani Sign-off & Freigabe**
- **Rolle:** Luca (du)
- **Task:**
  - Präsentiere QA-Report an Dani
  - Frage nach Genehmigung für v0.2.0 Final
  - Markiere `.md`-Dateien als FINAL (remove "draft" tag)
- **Deliverable:** Go/No-Go für SDK-Phase (WS2)
- **Abhängig von:** QA Sign-off

---

### ⏸️ NACH SPEC-SIGN-OFF (Woche 3)

Erst wenn WS1 FINAL ist:

**7. SDK-Phase starten (WS2)**
- Backend Dev → Python SDK (Interface-Design + Core)
- Backend Dev → Go SDK (Interface-Design + Core)
- Timeline: Woche 3-4 (15 Tage)

**8. Parallel: RFC Research (WS3)**
- Consultant → IETF/W3C Evaluierung
- Consultant → GitHub-Strategie
- Timeline: Woche 3-5 (10 Tage)

---

### 🎯 Sprint-Übersicht (12.03 – 14.03)

| Datum | Milestone | Owner | Status |
|-------|-----------|-------|--------|
| **12.03 (Heute)** | 🚀 Multimodal + Auth/HTTP Finalisierung | Protocol Architect | → Subagent-Start |
| **13.03** | ✅ JSON Schemas + Review-Vorbereitung | Protocol Architect + Luca | → Subagent-Start |
| **14.03** | ✅ QA Sign-off + Dani Freigabe | QA Engineer + Luca | → Subagent-Start |
| **15.03+** | 🚀 SDK-Phase beginnt | Backend Dev | → Warten auf WS1 Final |

---

## ⚠️ Blockaden & Risiken (aktuelle Sprint)

### 🔴 Blockaden

| Blockade | Status | Lösung | ETA |
|----------|--------|--------|-----|
| **Multimodal Pricing Spec nicht gestartet** | 🔴 AKTIV | Sofort Subagent spawnen | Heute 20:00 |
| **Keine Multimodal-Pricing-Expertise intern** | 🟡 RISIKO | Consultant konsultieren OR Selbstforschung | Während Spec-Erstellung |
| **JSON Schema Validierung-Tools nicht klar** | 🟡 RISIKO | `ajv-cli` für JSON Schema, `openapi-generator` für OpenAPI | Setup vor Schemas |

### 🟡 Risiken (Sprint)

| Risiko | W'keit | Impact | Mitigation |
|--------|--------|--------|------------|
| Multimodal Pricing Spec nicht bis Freitag fertig | Mittel | Hoch | Tägliche Status-Checks, Reserve-Zeit einplanen |
| QA findet kritische Fehler am Freitag | Niedrig | Hoch | QA früh einbeziehen, nicht erst am Ende |
| Backward-Compatibility-Probleme | Niedrig | Hoch | Detaillierte Migration-Dok + v0.1.1 Test-Cases |
| Provider-Realität weicht vom Design ab | Mittel | Mittel | Early-Adopter-Feedback einplanen (nach Release) |

### 🔴 Risiken (Langfristig)

| Risiko | W'keit | Impact | Mitigation |
|--------|--------|--------|------------|
| Spec-Änderungen während SDK-Entwicklung | Hoch | Hoch | **Freeze-Date Freitag 14.03 18:00 UTC** — danach nur Bugfixes |
| Python/Go Expertise nicht verfügbar | Niedrig | Hoch | Externe Freelancer als Backup (evaluate in Woche 2) |
| Provider zeigen kein Interesse | Mittel | Mittel | Fokus auf "De-facto Standard" statt RFC |
| IETF/W3C Prozess zu langsam | Hoch | Niedrig | GitHub-first Strategie als Fallback |

---

## 🎯 Erfolgskriterien (Checkpoints)

### WS1 (Spec) — Freitag 14.03 18:00 UTC

**Für "FINAL" Status:**
- [ ] Auth-Spec final (alle Feedback eingebaut, kein "draft" Tag)
- [ ] HTTP Binding Spec final
- [ ] Multimodal Pricing Spec final + Feedback von Consultant (Provider-Realität)
- [ ] Alle 5 JSON Schemas vorhanden + validiert gegen >3 Test-Cases
- [ ] OpenAPI 3.1 vollständig + validierbar
- [ ] Migration-Guide v0.1.1 → v0.2.0 dokumentiert
- [ ] QA Engineer Sign-off erhalten
- [ ] Dani gibt Go-Signal für SDK-Phase

**Für "AT RISK" Status:**
- [ ] Minor-Fixes noch möglich nach 14.03, aber SDK-Start nicht verzögert

### WS2 (SDKs) — Start 15.03, Ende 28.03

- [ ] `pip install apideals` funktioniert
- [ ] `go get github.com/apideals/adp-go` funktioniert
- [ ] Beide SDKs haben >90% Test-Coverage
- [ ] Documentation + Runnable Examples (Python + Go)
- [ ] Type-Safety: 100% Typing (Python/Pydantic), Interfaces (Go)

### WS3 (Standard) — Start 15.03, Ende 02.04

- [ ] IETF/W3C Optionen evaluiert + Recommendation
- [ ] Blogpost "Why ADP?" geschrieben + Draft
- [ ] GitHub Community Plan finalisiert
- [ ] 3-5 Provider ansprechen (Together AI, OpenRouter, Groq, ...)

---

## 📁 Datei-Struktur

```
Luca/projects/apideals/
├── concepts/
│   ├── adp-v0.2.0-roadmap.md          ← Diese Datei
│   ├── rfc-submission/
│   │   ├── ietf-research.md
│   │   ├── w3c-evaluation.md
│   │   └── community-strategy.md
│   └── spec-v0.2/
│       ├── auth.md
│       ├── http-binding.md
│       ├── pricing-multimodal.md
│       └── schemas/
├── sdks/
│   ├── python/                          ← Python SDK
│   └── go/                              ← Go SDK
└── research/
    └── provider-adoption-plan.md
```

---

## 📝 Changelog (Roadmap)

| Datum | Änderung | Autor |
|-------|----------|-------|
| 2026-03-12 | Initialer Master-Plan erstellt | Luca |
| 2026-03-12 18:38 UTC | Status aktualisiert: Auth ✅, HTTP ✅, Multimodal ⏳; 48h Action-Plan hinzugefügt | Subagent (PM-ADP-v0.2.0-SDKs) |

---

**Nächstes Update:** Woche 2 (nach Spec-Finalisierung)

*Dokument gepflegt von Luca (🦊) — Fragen? → `#project_calls` auf Discord*

---

## ✅ Aktueller Status (Stand: 2026-03-12)

### Workstream 1: Spec v0.2.0 — COMPLETE 🟢

Alle drei Spezifikationen wurden erstellt und sind bereit für Review:

| Dokument | Pfad | Länge | Inhalt |
|----------|------|-------|--------|
| Auth Spec | `concepts/spec-v0.2/auth.md` | ~12.800 Bytes | API Keys, OAuth 2.0, Rate Limits, HMAC |
| HTTP Binding | `concepts/spec-v0.2/http-binding.md` | ~18.000 Bytes | Endpoints, Headers, Status Codes, OpenAPI |
| Multimodal Pricing | `concepts/spec-v0.2/pricing-multimodal.md` | ~19.400 Bytes | Bild/Audio/Video Pricing, JSON Schema |

### Nächste Schritte

1. **Review durch Dani** — Alle drei Specs abnehmen lassen
2. **JSON Schemas finalisieren** — Nach Spec-Approval
3. **SDK-Entwicklung starten** — Python + Go SDKs (WS2)
4. **RFC-Research** — IETF/W3C Evaluation (WS3)

### Update-Log

| Datum | Änderung |
|-------|----------|
| 2026-03-12 | Initialer Master-Plan erstellt |
| 2026-03-12 | **ABGESCHLOSSEN:** Alle drei Spec-Dokumente erstellt |
| 2026-03-12 | Auth Spec v0.2.0 → `spec-v0.2/auth.md` ✅ |
| 2026-03-12 | HTTP Binding Spec v0.2.0 → `spec-v0.2/http-binding.md` ✅ |
| 2026-03-12 | Multimodal Pricing Spec v0.2.0 → `spec-v0.2/pricing-multimodal.md` ✅ |
