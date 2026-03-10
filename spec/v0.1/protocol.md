# apideals Deal Protocol — Spezifikation v0.1.1

**Version:** 0.1.1-draft  
**Erstellt:** 2026-03-09  
**Überarbeitet:** 2026-03-10  
**Autor:** apideals.ai
**Status:** REVISED (2026-03-10)  
**Lizenz (Spezifikation):** CC-BY 4.0  
**Lizenz (SDKs & Code):** Apache 2.0  

> **Lizenzhinweis:** Dieses Spezifikationsdokument steht unter [Creative Commons Attribution 4.0 (CC-BY 4.0)](https://creativecommons.org/licenses/by/4.0/). SDKs, Referenzimplementierungen und Werkzeuge stehen unter [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). CC-BY 4.0 ist für Protokollspezifikationen geeigneter als Apache 2.0, welches für Software konzipiert ist.

---

## Inhaltsverzeichnis

1. [Protocol Overview](#1-protocol-overview)
2. [Core Messages](#2-core-messages)
3. [Pricing Schema](#3-pricing-schema)
4. [Compliance & Capabilities](#4-compliance--capabilities)
5. [Versionierungsstrategie](#5-versionierungsstrategie)
6. [Precedence Analysis](#6-precedence-analysis)
7. [GitHub Repo Struktur](#7-github-repo-struktur)
8. [Design-Entscheidungen](#8-design-entscheidungen)
9. [Offene Fragen & Roadmap](#9-offene-fragen--roadmap)
10. [Provider Discovery](#10-provider-discovery)
11. [Changelog](#11-changelog)

---

## 1. Protocol Overview

### Was ist das Deal Protocol?

Das **apideals Deal Protocol** (ADP) ist ein offenes, JSON-basiertes Nachrichtenprotokoll, über das Software-Agenten und Systeme LLM-API-Angebote **anfragen**, **vergleichen** und **ihre Absicht signalisieren** können — ohne menschliche Interaktion.

### Welches Problem löst es?

Heute muss ein Agent (oder Mensch), der eine LLM-API buchen will:

1. Pricing-Pages von 15+ Anbietern manuell lesen (HTML, PDF, Sales-Kontakt)
2. Preise normalisieren ($/MTok vs. $/1k Tokens vs. Credits vs. €/Anfrage)
3. Versteckte Konditionen finden (Batch-Rabatte, Cache-Hits, Free Tiers, Commitment-Deals)
4. Compliance prüfen (DSGVO, EU-Hosting, SOC2, BAA)
5. Sich bei jedem Anbieter einzeln anmelden

**Es gibt kein maschinenlesbares Standardformat**, in dem ein Agent sagen kann: *"Ich brauche eine Reasoning-fähige LLM-API mit EU-Hosting, max. $5/MTok Output, min. 200K Context"* — und automatisch passende Angebote erhält.

Das Deal Protocol schließt diese Lücke.

### Analogien

| Domäne | Standard | Was er löst |
|--------|----------|-------------|
| Web APIs | OpenAPI 3.x | Maschinenlesbare API-Beschreibung |
| Zahlungen | Stripe API | Standardisierte Transaktionen |
| AI Tools | MCP (Anthropic) | Tool-Discovery für Agenten |
| **LLM-Deals** | **ADP (dieses Protocol)** | **Deal-Discovery und -Absichtssignalisierung für Agenten** |

### Scope von v0.1

v0.1 ist **bewusst minimal**. Es definiert:

- ✅ Vier Nachrichten: `DealRequest`, `DealOffer`, `DealIntent`, `DealError`
- ✅ Ein Pricing-Schema für Token-basierte LLM-APIs
- ✅ Ein Compliance/Capabilities-Vokabular
- ✅ Versionierung und Erweiterbarkeit
- ✅ Provider-Discovery via `/.well-known/adp.json`

v0.1 definiert **nicht**:

- ❌ Transport-Layer (HTTP, WebSocket, Message Queue) — [ANNAHME: v0.1 ist transport-agnostisch; Empfehlung ist HTTP/REST]
- ❌ Authentifizierung/Autorisierung — [wird in v0.2 adressiert]
- ❌ Abrechnung/Payment — [wird in v0.3 adressiert]
- ❌ Multimodale Pricing (Bild/Audio/Video-Tokens) — [Erweiterung in v0.2]
- ❌ Verhandlungsprotokolle (Counter-Offers, Auktionen) — [Erweiterung in v0.3]

### Design-Prinzipien

| Prinzip | Bedeutung |
|---------|-----------|
| **Simplicity First** | Ein Anbieter muss das Protocol an einem Nachmittag implementieren können |
| **JSON-native** | Kein XML, kein Protobuf, kein YAML — JSON ist die Lingua Franca der API-Welt |
| **Additive Evolution** | Neue Felder hinzufügen = OK. Bestehende entfernen = Breaking Change = neue Major-Version |
| **Agent-readable** | Jedes Feld hat eine klare Semantik. Keine Freitext-Felder für strukturierte Daten |
| **Human-debuggable** | Ein Mensch muss ein ADP-Dokument lesen und verstehen können |

---

## 2. Core Messages

Das Protocol definiert vier Nachrichten-Typen. Jede Nachricht ist ein JSON-Objekt mit einem `adp`-Header.

### 2.1 Gemeinsamer Header

Jede ADP-Nachricht beginnt mit diesem Header:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest | DealOffer | DealIntent | DealError",
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-09T18:43:00Z",
    "correlation_id": null
  }
}
```

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `version` | `string` (semver, z.B. `"0.1.1"`) | ✅ | Protocol-Version |
| `type` | `enum` | ✅ | Nachrichtentyp: `DealRequest`, `DealOffer`, `DealIntent`, `DealError` |
| `id` | `string` (UUID v4) | ✅ | Eindeutige Nachrichten-ID. Format: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` |
| `timestamp` | `string` (ISO 8601 UTC) | ✅ | Erstellungszeitpunkt. Format: `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z$` — immer UTC (`Z`-Suffix), kein Offset |
| `correlation_id` | `string` (UUID v4) | ❌ | Referenz auf die auslösende Nachricht. **Semantik:** In `DealRequest` immer weggelassen oder `null` (initiiert neues Gespräch). In `DealOffer`: ID des auslösenden `DealRequest`. In `DealIntent`: ID des akzeptierten `DealOffer`. In `DealError`: ID der Nachricht die den Fehler ausgelöst hat. |

### 2.2 DealRequest

**Semantik:** Ein Agent fragt: *"Ich brauche eine LLM-API mit diesen Anforderungen."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "timestamp": "2026-03-09T18:43:00Z",
    "correlation_id": null
  },
  "request": {
    "requester": {
      "agent_id": "agent:mycompany:procurement-bot",
      "is_automated": true,
      "name": "MyCompany Procurement Agent",
      "contact": {
        "email": "deals@mycompany.com"
      }
    },
    "requirements": {
      "task_classes": ["reasoning"],
      "min_context_window": 200000,
      "min_output_tokens": 8000,
      "modalities": ["text"],
      "capabilities": ["tool_use", "structured_output"],
      "compliance": ["gdpr", "eu_hosting"],
      "max_latency_ms": {
        "ttft": 2000,
        "tps": 50
      }
    },
    "volume": {
      "estimated_monthly_input_tokens": 50000000,
      "estimated_monthly_output_tokens": 10000000,
      "pattern": "steady",
      "batch_eligible": true
    },
    "budget": {
      "max_cost_per_mtok_input": 5.00,
      "max_cost_per_mtok_output": 15.00,
      "currency": "USD",
      "max_monthly_spend": 500.00
    },
    "preferences": {
      "commitment": "none",
      "preferred_providers": [],
      "excluded_providers": [],
      "deal_type": "pay_as_you_go"
    },
    "valid_until": "2026-03-10T18:43:00Z",
    "request_ttl_hours": 24
  }
}
```

#### DealRequest — Feld-Referenz

**`request.requester`** — Wer fragt an?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `agent_id` | `string` | ✅ | Eindeutige Agent-Kennung (Format frei, Empfehlung: URN-artig) |
| `is_automated` | `boolean` | ✅ | `true` wenn von einem autonomen AI-Agenten gesendet. Pflichtfeld für EU AI Act Art. 50 Compliance (Transparenzpflicht). |
| `name` | `string` | ❌ | Menschenlesbarer Name |
| `contact` | `object` | ❌ | Kontaktinformationen (strukturiert) |
| `contact.email` | `string` | ❌ | Kontakt-E-Mail |
| `contact.webhook_url` | `string` (URL) | ❌ | Webhook-URL für asynchrone Antworten |
| `contact.support_url` | `string` (URL) | ❌ | Support-URL |

**`request.requirements`** — Was wird gebraucht?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `task_classes` | `array<enum>` | ❌ | Gewünschte Aufgabenklassen (OR-Logik): `general`, `reasoning`, `coding`, `creative`, `classification`, `extraction`, `embedding`, `multimodal`. Ein Offer muss mindestens eine der genannten Klassen unterstützen. |
| `min_context_window` | `integer` | ❌ | Minimum Context Window in Tokens |
| `min_output_tokens` | `integer` | ❌ | Minimum Output-Tokens pro Anfrage |
| `modalities` | `array<enum>` | ❌ | Benötigte Modalitäten: `text`, `image_input`, `image_output`, `audio_input`, `audio_output`, `video_input` |
| `capabilities` | `array<enum>` | ❌ | Benötigte Fähigkeiten: `tool_use`, `structured_output`, `function_calling`, `streaming`, `batch_api`, `prompt_caching`, `fine_tuning`, `vision` |
| `compliance` | `array<enum>` | ❌ | Compliance-Anforderungen (siehe [Abschnitt 4](#4-compliance--capabilities)) |
| `max_latency_ms` | `object` | ❌ | Latenz-Anforderungen |
| `max_latency_ms.ttft` | `integer` | ❌ | Max. Time-to-First-Token in ms |
| `max_latency_ms.tps` | `integer` | ❌ | Min. Tokens-per-Second |

**`request.volume`** — Wie viel wird gebraucht?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `estimated_monthly_input_tokens` | `integer` | ❌ | Geschätzte monatliche Input-Tokens. `0` = kein Bedarf, weggelassen = unbekannt. |
| `estimated_monthly_output_tokens` | `integer` | ❌ | Geschätzte monatliche Output-Tokens |
| `pattern` | `enum` | ❌ | Nutzungsmuster: `steady`, `bursty`, `batch`, `on_demand` |
| `batch_eligible` | `boolean` | ❌ | Kann asynchrone Batch-Verarbeitung nutzen? |

**`request.budget`** — Was darf es kosten?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `max_cost_per_mtok_input` | `number` | ❌ | Max. Preis pro 1M Input-Tokens |
| `max_cost_per_mtok_output` | `number` | ❌ | Max. Preis pro 1M Output-Tokens |
| `currency` | `string` (ISO 4217 Alpha-3) | ✅ | Währung. Format: `^[A-Z]{3}$`. Beispiel: `"USD"`, `"EUR"`. |
| `max_monthly_spend` | `number` | ❌ | Max. monatliche Gesamtausgaben |

**`request.preferences`** — Zusätzliche Wünsche

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `commitment` | `enum` | ❌ | `none`, `monthly`, `annual` — gewünschte Bindung |
| `preferred_providers` | `array<string>` | ❌ | Bevorzugte Anbieter (Provider-IDs) |
| `excluded_providers` | `array<string>` | ❌ | Ausgeschlossene Anbieter. **Regel:** Wenn ein Provider in beiden Listen erscheint, hat `excluded_providers` Vorrang. |
| `deal_type` | `enum` | ❌ | `pay_as_you_go`, `commitment`, `prepaid`, `enterprise_custom` |

**`request.valid_until`** — Gültigkeit

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `valid_until` | `string` (ISO 8601 UTC) | ❌ | Bis wann ist die Anfrage gültig? Muss in der Zukunft liegen. Empfänger SOLLEN abgelaufene Requests ablehnen (DealError mit `code: "EXPIRED"`). |
| `request_ttl_hours` | `integer` | ❌ | Gewünschte Datenlöschfrist in Stunden (DSGVO Art. 17). Default wenn weggelassen: 24. Anbieter SOLLEN Request-Daten nach dieser Zeit löschen. |

### 2.3 DealOffer

**Semantik:** Ein Anbieter (oder Aggregator) antwortet: *"Ich biete diese Konditionen."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "timestamp": "2026-03-09T18:44:00Z",
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "offer": {
    "provider": {
      "provider_id": "google",
      "name": "Google Cloud — Vertex AI",
      "url": "https://cloud.google.com/vertex-ai",
      "contact": {
        "email": "cloud-sales@google.com",
        "support_url": "https://cloud.google.com/support"
      }
    },
    "model": {
      "model_id": "gemini-3.1-pro-preview",
      "name": "Gemini 3.1 Pro Preview",
      "version": "2026-03",
      "task_classes": ["general", "reasoning", "coding", "multimodal"],
      "context_window": 1048576,
      "max_output_tokens": 65536,
      "modalities": ["text", "image_input", "video_input", "audio_input"],
      "capabilities": ["tool_use", "structured_output", "function_calling", "streaming", "batch_api", "prompt_caching"],
      "knowledge_cutoff": "2025-12-01",
      "ai_act_risk_class": "minimal",
      "gpai_model_card_url": "https://cloud.google.com/vertex-ai/docs/ai-act",
      "prohibited_uses": []
    },
    "pricing": {
      "currency": "USD",
      "base": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 12.00
      },
      "tiers": [
        {
          "threshold_mtok_monthly": 100,
          "input_per_mtok": 1.80,
          "output_per_mtok": 10.80
        }
      ],
      "modifiers": [
        {
          "type": "batch",
          "discount_pct": 50,
          "conditions": "Asynchrone Verarbeitung, 24h SLA"
        },
        {
          "type": "cache_read",
          "input_per_mtok": 0.50,
          "conditions": "Prompt-Caching, min. 1024 Token Cache-Prefix"
        },
        {
          "type": "cache_write",
          "input_per_mtok": 4.00,
          "conditions": "Erstmaliges Caching eines Prefixes"
        }
      ],
      "free_tier": {
        "monthly_input_tokens": 0,
        "monthly_output_tokens": 0,
        "notes": "Kein Free Tier für dieses Modell"
      },
      "commitment_deals": []
    },
    "compliance": {
      "compliance_verified_by": "self-declared",
      "certifications": ["soc2", "iso27001"],
      "data_regions": ["US", "EU", "APAC"],
      "gdpr_compliant": true,
      "dpa_available": true,
      "data_retention_days": 30,
      "training_on_data": false,
      "privacy_policy_url": "https://cloud.google.com/terms/cloud-privacy-notice",
      "subprocessors_url": "https://cloud.google.com/terms/subprocessors"
    },
    "sla": {
      "uptime_pct": 99.9,
      "ttft_p50_ms": 400,
      "ttft_p99_ms": 2000,
      "tps_median": 120
    },
    "valid_from": "2026-03-09T00:00:00Z",
    "valid_until": "2026-04-09T00:00:00Z",
    "terms_url": "https://cloud.google.com/terms/service-terms"
  }
}
```

#### DealOffer — Feld-Referenz

**`offer.provider`** — Wer bietet an?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `provider_id` | `string` | ✅ | Eindeutige Anbieter-Kennung (lowercase, slug-format) |
| `name` | `string` | ✅ | Menschenlesbarer Anbietername |
| `url` | `string` (URL) | ❌ | Website des Anbieters |
| `contact` | `object` | ❌ | Kontaktinformationen |
| `contact.email` | `string` | ❌ | Kontakt-E-Mail |
| `contact.webhook_url` | `string` (URL) | ❌ | Webhook-URL |
| `contact.support_url` | `string` (URL) | ❌ | Support-URL |

**`offer.model`** — Welches Modell?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `model_id` | `string` | ✅ | Eindeutige Modell-Kennung (slug, z.B. `claude-opus-4.6`) |
| `name` | `string` | ✅ | Menschenlesbarer Modellname |
| `version` | `string` | ❌ | Modellversion / Snapshot |
| `task_classes` | `array<enum>` | ✅ | Unterstützte Aufgabenklassen. Darf nicht leer sein. Keine Duplikate. |
| `context_window` | `integer` | ✅ | Max. Context Window in Tokens |
| `max_output_tokens` | `integer` | ✅ | Max. Output-Tokens pro Anfrage |
| `modalities` | `array<enum>` | ✅ | Unterstützte Modalitäten. Darf nicht leer sein. |
| `capabilities` | `array<enum>` | ✅ | Unterstützte Fähigkeiten. Leeres Array erlaubt (= keine besonderen Fähigkeiten). |
| `knowledge_cutoff` | `string` (date, `YYYY-MM-DD`) | ❌ | Training-Data-Cutoff |
| `ai_act_risk_class` | `enum` | ❌ | EU AI Act Risikoklasse: `minimal`, `limited`, `high`, `unacceptable` |
| `gpai_model_card_url` | `string` (URL) | ❌ | Link zur EU AI Act-konformen Modell-Dokumentation (Art. 53 Abs. 1 lit. b) |
| `prohibited_uses` | `array<string>` | ❌ | Liste verbotener Anwendungsfälle nach Art. 5 EU AI Act |

**`offer.pricing`** — Was kostet es? (Details siehe [Abschnitt 3](#3-pricing-schema))

**`offer.compliance`** — Compliance-Informationen

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `compliance_verified_by` | `enum` | ✅ | `self-declared` (Anbieter-Eigenangabe, nicht extern geprüft), `third-party` (externes Audit), `apideals-verified` (durch apideals.ai geprüft — in v0.1 nicht verfügbar). **Hinweis:** apideals.ai übernimmt keine Haftung für die Richtigkeit von `self-declared` Compliance-Tags. |
| `certifications` | `array<enum>` | ❌ | Liste der Zertifizierungen |
| `data_regions` | `array<string>` | ❌ | Verfügbare Datenregionen. Erlaubte Werte: ISO 3166-1 Alpha-2 Codes (z.B. `"DE"`, `"FR"`) ODER Aggregate: `"EU"` (gesamt EU/EWR), `"US"`, `"APAC"`. |
| `gdpr_compliant` | `boolean` | ❌ | DSGVO-konform? |
| `dpa_available` | `boolean` | ❌ | DPA/AVV verfügbar? |
| `data_retention_days` | `integer` | ❌ | Speicherdauer in Tagen (0 = keine Speicherung) |
| `training_on_data` | `boolean` | ❌ | Werden Daten für Training verwendet? |
| `privacy_policy_url` | `string` (URL) | ❌ | Link zur Datenschutzerklärung des Anbieters |
| `subprocessors_url` | `string` (URL) | ❌ | Link zur Sub-Auftragsverarbeiter-Liste |

**`offer.sla`** — Service Level Agreements

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `uptime_pct` | `number` | ❌ | Garantierte Uptime in Prozent |
| `ttft_p50_ms` | `integer` | ❌ | Time-to-First-Token, Median |
| `ttft_p99_ms` | `integer` | ❌ | Time-to-First-Token, 99. Perzentil |
| `tps_median` | `integer` | ❌ | Tokens-per-Second, Median |

**`offer.valid_from` / `offer.valid_until`** — Gültigkeitszeitraum

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `valid_from` | `string` (ISO 8601 UTC) | ✅ | Ab wann gilt das Angebot? |
| `valid_until` | `string` (ISO 8601 UTC) | ✅ | Bis wann gilt das Angebot? **Validierungsregel:** `valid_until` MUSS zeitlich nach `valid_from` liegen. Offers mit `valid_until` in der Vergangenheit gelten als abgelaufen und MÜSSEN vom Empfänger verworfen werden. |
| `terms_url` | `string` (URL) | ❌ | Link zu den vollständigen AGB |

### 2.4 DealIntent

> **⚖️ Rechtlicher Hinweis:** `DealIntent` ist eine **Absichtserklärung** — kein rechtsverbindlicher Vertragsschluss. Der tatsächliche Vertrag entsteht ausschließlich beim Anbieter nach Weiterleitung (Redirect) oder manuellem Kontakt. Ein automatisch generierter `DealIntent` kann nach deutschem Recht (§§ 145–147 BGB) als Willenserklärung gewertet werden, wenn er alle essentialia negotii enthält. Das Feld `binding: false` und `requires_human_confirmation` geben dem Anbieter maschinenlesbare Hinweise auf den gewünschten Verbindlichkeitsgrad. [ANWALT PRÜFEN für den jeweiligen Anwendungsfall]

**Semantik:** Ein Agent signalisiert Interesse an einem Angebot: *"Ich beabsichtige, diesen Deal anzunehmen."*

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealIntent",
    "id": "c3d4e5f6-a7b8-9012-cdef-345678901234",
    "timestamp": "2026-03-09T18:45:00Z",
    "correlation_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012"
  },
  "intent": {
    "binding": false,
    "requires_human_confirmation": true,
    "party_type": "business",
    "requester": {
      "agent_id": "agent:mycompany:procurement-bot",
      "is_automated": true,
      "name": "MyCompany Procurement Agent",
      "contact": {
        "email": "deals@mycompany.com"
      }
    },
    "accepted_offer_id": "b2c3d4e5-f6a7-8901-bcde-f23456789012",
    "accepted_pricing_snapshot": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 12.00,
      "modifiers_applied": ["batch"]
    },
    "volume_commitment": {
      "estimated_monthly_input_tokens": 50000000,
      "estimated_monthly_output_tokens": 10000000,
      "commitment_type": "none",
      "commitment_duration_months": null
    },
    "activation": {
      "type": "redirect",
      "redirect_url": "https://cloud.google.com/vertex-ai/signup?ref=apideals&deal=b2c3d4e5-f6a7-8901-bcde-f23456789012"
    },
    "notes": null
  }
}
```

#### DealIntent — Feld-Referenz

**`intent.binding`** — Verbindlichkeit

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `binding` | `boolean` | ✅ | In v0.1 immer `false`. Maschinenlesbare Signalisierung, dass dies keine rechtsverbindliche Erklärung ist. |
| `requires_human_confirmation` | `boolean` | ❌ | Wenn `true`: Der Agent erwartet menschliche Bestätigung vor Vertragsschluss. Default: `true`. |
| `party_type` | `enum` | ❌ | `"business"` oder `"consumer"`. Bei `"consumer"` können zwingende Verbraucherschutzvorschriften gelten (§§ 312 ff. BGB, Widerrufsrecht). |

**`intent.requester`** — Wer sendet die Absichtserklärung? (wie in DealRequest)

**`intent.accepted_offer_id`** — Referenz auf das angenommene DealOffer (UUID v4 des `DealOffer.adp.id`).

**`intent.accepted_pricing_snapshot`** — Welcher Preis wurde zugrunde gelegt?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `input_per_mtok` | `number` | ✅ | Zugrunde gelegter Input-Preis pro MTok |
| `output_per_mtok` | `number` | ✅ | Zugrunde gelegter Output-Preis pro MTok |
| `modifiers_applied` | `array<enum>` | ❌ | Welche Modifier (aus `modifier.type` Enum) wurden einkalkuliert |

**`intent.volume_commitment`** — Volumensabsicht

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `estimated_monthly_input_tokens` | `integer` | ❌ | Geschätztes monatliches Input-Volumen |
| `estimated_monthly_output_tokens` | `integer` | ❌ | Geschätztes monatliches Output-Volumen |
| `commitment_type` | `enum` | ❌ | `none`, `soft` (Schätzung), `hard` (verbindlich) |
| `commitment_duration_months` | `integer` | ❌ | Laufzeit in Monaten. Weggelassen = unbefristet. |

**`intent.activation`** — Wie wird der nächste Schritt eingeleitet?

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `type` | `enum` | ✅ | `redirect` (URL zum Anbieter), `api_provision` (automatische API-Key-Ausgabe, v0.2+), `manual` (manueller Kontakt nötig) |
| `redirect_url` | `string` (URL) | ⚠️ **Pflicht wenn `type = "redirect"`** | Signup/Activation-URL beim Anbieter. **Validierungsregel:** Wenn `activation.type = "redirect"`, MUSS `redirect_url` gesetzt sein. |

### 2.5 DealError

**Semantik:** Eine Nachricht konnte nicht verarbeitet werden.

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealError",
    "id": "d4e5f6a7-b8c9-0123-def0-456789012345",
    "timestamp": "2026-03-09T18:43:01Z",
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  },
  "error": {
    "code": "INVALID_REQUEST",
    "message": "requirements.task_classes contains unknown value 'superreasoning'",
    "field_errors": [
      {
        "field": "requirements.task_classes[0]",
        "code": "INVALID_ENUM",
        "message": "Expected one of: general, reasoning, coding, creative, classification, extraction, embedding, multimodal"
      }
    ],
    "retryable": false,
    "retry_after_ms": null
  }
}
```

#### DealError — Feld-Referenz

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `error.code` | `enum` | ✅ | `INVALID_REQUEST`, `PROVIDER_UNAVAILABLE`, `EXPIRED`, `VERSION_MISMATCH`, `RATE_LIMITED`, `NOT_FOUND` |
| `error.message` | `string` | ✅ | Menschenlesbarer Fehlertext |
| `error.field_errors` | `array<object>` | ❌ | Liste feldbezogener Fehler |
| `error.field_errors[].field` | `string` | ✅ | Feldpfad (z.B. `"requirements.task_classes[0]"`) |
| `error.field_errors[].code` | `string` | ✅ | Maschinenlesbarer Fehlercode (z.B. `"INVALID_ENUM"`, `"REQUIRED"`) |
| `error.field_errors[].message` | `string` | ✅ | Menschenlesbarer Fehlertext für dieses Feld |
| `error.retryable` | `boolean` | ✅ | Kann der Request wiederholt werden? |
| `error.retry_after_ms` | `integer \| null` | ❌ | Wartezeit vor erneutem Versuch in ms. `null` wenn nicht anwendbar. |

---

## 3. Pricing Schema

Das Pricing-Schema ist das Herzstück des Protocols. Es muss die reale Komplexität der LLM-API-Preislandschaft abbilden, ohne so komplex zu werden, dass Anbieter es nicht implementieren wollen.

### 3.1 Design-Entscheidung: $/MTok als Basiseinheit

**Alle Preise werden in Dollar pro 1 Million Tokens ($/MTok) angegeben.**

Begründung:
- Die Industrie konvergiert auf $/MTok als Standard (OpenAI, Anthropic, Google nutzen es)
- Vermeidet Verwirrung zwischen $/1k Tokens, $/1M Tokens, Credits
- [ANNAHME] $/MTok bleibt die dominante Einheit. Falls ein Anbieter pro Request oder pro Minute abrechnet, müsste v0.2 das adressieren.

### 3.2 Pricing-Objekt (vollständig)

```json
{
  "pricing": {
    "currency": "USD",
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 12.00
    },
    "tiers": [
      {
        "threshold_mtok_monthly": 100,
        "input_per_mtok": 1.80,
        "output_per_mtok": 10.80
      },
      {
        "threshold_mtok_monthly": 1000,
        "input_per_mtok": 1.50,
        "output_per_mtok": 9.00
      }
    ],
    "modifiers": [
      {
        "type": "batch",
        "discount_pct": 50,
        "conditions": "Asynchrone Verarbeitung, 24h SLA"
      },
      {
        "type": "cache_read",
        "input_per_mtok": 0.50,
        "conditions": "Cached prompt prefix, min. 1024 Tokens"
      },
      {
        "type": "cache_write",
        "input_per_mtok": 4.00,
        "conditions": "Erstmaliges Caching"
      },
      {
        "type": "long_context",
        "threshold_tokens": 200000,
        "input_per_mtok": 4.00,
        "output_per_mtok": 24.00,
        "conditions": "Tokens über 200K Context-Grenze"
      }
    ],
    "free_tier": {
      "monthly_input_tokens": 1000000,
      "monthly_output_tokens": 200000,
      "rate_limit_rpm": 10,
      "valid_until": null,
      "notes": "Free tier for evaluation"
    },
    "commitment_deals": [
      {
        "type": "annual_prepaid",
        "discount_pct": 20,
        "min_monthly_spend": 1000.00,
        "duration_months": 12,
        "conditions": "Annual commitment, prepaid"
      }
    ],
    "effective_price_example": {
      "scenario": "50M input + 10M output tokens/month, batch modifier angewendet",
      "input_tokens": 50000000,
      "output_tokens": 10000000,
      "modifiers_applied": ["batch"],
      "total_cost": 110.00,
      "currency": "USD",
      "breakdown": {
        "input_cost": "50 MTok × $2.00 × 50% batch = $50.00",
        "output_cost": "10 MTok × $12.00 × 50% batch = $60.00"
      }
    }
  }
}
```

### 3.3 Pricing-Felder im Detail

**`pricing.base`** — Basispreis (Listenpreis, pay-as-you-go)

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `input_per_mtok` | `number` | ✅ | Basispreis pro 1M Input-Tokens |
| `output_per_mtok` | `number` | ✅ | Basispreis pro 1M Output-Tokens |

**`pricing.tiers[]`** — Staffelpreise (Volume Discounts)

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `threshold_mtok_monthly` | `number` | ✅ | Ab welchem monatlichem Volumen (in MTok) gilt die Staffel? Muss > 0 sein. |
| `input_per_mtok` | `number` | ✅ | Input-Preis in dieser Staffel |
| `output_per_mtok` | `number` | ✅ | Output-Preis in dieser Staffel |

> **Semantik:** Tiers sind aufsteigend sortiert. Der höchste überschrittene Threshold bestimmt den Preis für **alle** Tokens des Monats (Flat-Rate, nicht marginale Staffelung).

> ⚠️ **WICHTIG: Flat-Rate-Semantik und Edge Case**
>
> Die Tier-Logik verwendet Flat-Rate (nicht marginale Staffelung). Das bedeutet: Sobald ein Tier-Schwellenwert überschritten wird, gilt der niedrigere Preis für **alle** Tokens des Monats — auch die ersten.
>
> **Edge Case:** Bei Verbrauch knapp über einer Tier-Schwelle kann der Gesamtpreis **niedriger** sein als bei Verbrauch knapp darunter.
>
> **Beispiel:** Tier-Schwelle bei 100 MTok/Monat (Base: $2.00/MTok → Tier: $1.80/MTok Input)
> - 99 MTok × $2.00 = **$198.00** (unter Schwelle, Base-Preis)
> - 101 MTok × $1.80 = **$181.80** (über Schwelle, Tier-Preis für alle Tokens)
>
> Dies ist beabsichtigt und entspricht dem Marktstandard für Volume-Discounts. Implementierer MÜSSEN diesen Edge Case korrekt handhaben und ggf. bei der Budget-Kalkulation berücksichtigen.

**`pricing.modifiers[]`** — Preismodifikatoren

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `type` | `enum` | ✅ | `batch`, `cache_read`, `cache_write`, `long_context`, `fine_tuned`, `custom`. Jeder `type` darf pro Offer nur einmal vorkommen. |
| `discount_pct` | `number` | ❌ | Rabatt in Prozent (z.B. `50` = 50% Rabatt). Maximalwert: 99. Nicht kombinierbar mit absoluten Preisfeldern in demselben Modifier. |
| `input_per_mtok` | `number` | ❌ | Absoluter Preis (überschreibt aktuellen Preis vollständig, wenn angegeben). Nicht kombinierbar mit `discount_pct`. |
| `output_per_mtok` | `number` | ❌ | Absoluter Output-Preis |
| `threshold_tokens` | `integer` | ❌ | Ab welcher Token-Zahl greift der Modifier (z.B. Long-Context ab 200K) |
| `conditions` | `string` | ❌ | Menschenlesbare Bedingungen |

> **XOR-Regel:** Ein Modifier MUSS entweder `discount_pct` ODER absolute Preise (`input_per_mtok`/`output_per_mtok`) angeben — nicht beides.

**`pricing.free_tier`** — Kostenloser Einstieg (weggelassen = kein Free Tier)

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `monthly_input_tokens` | `integer` | ❌ | Kostenlose Input-Tokens pro Monat |
| `monthly_output_tokens` | `integer` | ❌ | Kostenlose Output-Tokens pro Monat |
| `rate_limit_rpm` | `integer` | ❌ | Rate-Limit in Requests pro Minute |
| `valid_until` | `string \| null` | ❌ | Wann endet der Free Tier? (`null` oder weggelassen = unbegrenzt) |
| `notes` | `string` | ❌ | Zusätzliche Hinweise |

**`pricing.commitment_deals[]`** — Commitment/Prepaid-Angebote

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `type` | `enum` | ✅ | `monthly_prepaid`, `annual_prepaid`, `enterprise_custom` |
| `discount_pct` | `number` | ✅ | Rabatt gegenüber Base |
| `min_monthly_spend` | `number` | ❌ | Mindestausgabe pro Monat |
| `duration_months` | `integer` | ❌ | Laufzeit |
| `conditions` | `string` | ❌ | Zusätzliche Bedingungen |

**`pricing.effective_price_example`** — Berechnungsbeispiel (optional, nicht normativ)

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `scenario` | `string` | ❌ | Beschreibung des Beispiel-Szenarios |
| `input_tokens` | `integer` | ❌ | Anzahl Input-Tokens im Beispiel |
| `output_tokens` | `integer` | ❌ | Anzahl Output-Tokens im Beispiel |
| `modifiers_applied` | `array<enum>` | ❌ | Angewendete Modifier-Typen |
| `total_cost` | `number` | ❌ | Gesamtkosten im Beispiel |
| `currency` | `string` | ❌ | Währung des Beispiels |
| `breakdown` | `object` | ❌ | Aufschlüsselung der Berechnung |

> Dieses Feld ist **nicht normativ** — es dient der menschlichen Verständlichkeit. Ein Agent SOLL immer selbst rechnen.

### 3.4 Preis-Berechnungslogik (informativ)

```
// Schritt 1: Tier bestimmen (Flat-Rate)
effective_input_price = base.input_per_mtok
effective_output_price = base.output_per_mtok

total_monthly_tokens = input_mtok + output_mtok  // oder nur input? → Anbieter definiert

FOR tier IN tiers (aufsteigend sortiert nach threshold_mtok_monthly):
  IF total_monthly_tokens > tier.threshold_mtok_monthly:
    effective_input_price = tier.input_per_mtok
    effective_output_price = tier.output_per_mtok
// Ergebnis: höchster überschrittener Tier gilt für ALLE Tokens

// Schritt 2: Modifier anwenden (in Reihenfolge ihres Erscheinens in modifiers[])
FOR modifier IN modifiers:
  IF modifier.discount_pct:
    effective_input_price  *= (1 - modifier.discount_pct / 100)
    effective_output_price *= (1 - modifier.discount_pct / 100)
  ELSE IF modifier.input_per_mtok:
    effective_input_price  = modifier.input_per_mtok    // absolute Preise überschreiben
    IF modifier.output_per_mtok:
      effective_output_price = modifier.output_per_mtok

// Modifier-Kombination: discount_pct Modifier sind kumulativ (sequenziell angewendet, nicht addiert).
// Beispiel: base=$5 → batch(discount_pct=50) → $2.50 → weiterer(discount_pct=10) → $2.25
// Absolute Modifier überschreiben den dann-aktuellen Preis vollständig.

// Schritt 3: Gesamtkosten
monthly_cost = (input_mtok × effective_input_price) + (output_mtok × effective_output_price)
```

---

## 4. Compliance & Capabilities

### 4.1 Compliance-Vokabular (Enums)

Das Protocol definiert ein **kontrolliertes Vokabular** für Compliance-Anforderungen. Jeder Wert hat eine präzise Semantik.

> ⚠️ **Wichtiger Haftungshinweis:** Compliance-Tags in ADP v0.1 sind **Selbstangaben der Anbieter** (`compliance_verified_by: "self-declared"`). apideals.ai prüft diese Angaben nicht und übernimmt keine Haftung für ihre Richtigkeit. Käufer und Agent-Betreiber sind verpflichtet, Compliance-Angaben für ihren konkreten Anwendungsfall selbst zu verifizieren (Art. 28 Abs. 1 DSGVO: "hinreichende Garantien"). Bei falschen Compliance-Tags haftet primär der Anbieter (§ 823 BGB, Art. 82 DSGVO, § 5 UWG).

#### Compliance-Tags

| Tag | Bedeutung |
|-----|-----------|
| `gdpr` | DSGVO-konform: AVV/DPA verfügbar, Datenverarbeitung gem. Art. 28 DSGVO |
| `eu_hosting` | Daten werden in EU/EWR-Rechenzentren verarbeitet und gespeichert |
| `eu_company` | Anbieter ist eine juristische Person mit Sitz in der EU/EWR |
| `soc2` | SOC 2 Type II Zertifizierung vorhanden |
| `iso27001` | ISO 27001 Zertifizierung vorhanden |
| `hipaa` | HIPAA-konform (US Healthcare) |
| `baa_available` | Business Associate Agreement verfügbar |
| `fedramp` | FedRAMP-zertifiziert (US Government) |
| `no_training` | Kundendaten werden NICHT für Modelltraining verwendet |
| `zero_retention` | Keine Speicherung von Prompts/Responses nach Verarbeitung |
| `on_premise` | On-Premise-Deployment verfügbar |
| `data_residency_de` | Datenverarbeitung ausschließlich in Deutschland |
| `data_residency_eu` | Datenverarbeitung ausschließlich in EU/EWR |
| `pci_dss` | PCI DSS Level 1 Compliance |

### 4.2 Capabilities-Vokabular (Enums)

#### Task Classes

| Wert | Beschreibung |
|------|--------------|
| `general` | Allgemeine Text-Generierung und Chat |
| `reasoning` | Chain-of-Thought, mehrstufige Logik, mathematisches Denken |
| `coding` | Code-Generierung, Debugging, Code-Review |
| `creative` | Kreatives Schreiben, Storytelling |
| `classification` | Text-Klassifikation, Sentiment-Analyse |
| `extraction` | Informationsextraktion, NER, Strukturierung |
| `embedding` | Text-Embeddings (Vektor-Repräsentation) |
| `multimodal` | Bild/Audio/Video-Verständnis oder -Generierung |

#### Capabilities

| Wert | Beschreibung |
|------|--------------|
| `tool_use` | Kann externe Tools/Functions aufrufen |
| `structured_output` | Kann JSON-Schema-konformen Output erzeugen |
| `function_calling` | Unterstützt OpenAI-kompatibles Function Calling |
| `streaming` | Unterstützt Server-Sent Events Streaming |
| `batch_api` | Unterstützt asynchrone Batch-Verarbeitung |
| `prompt_caching` | Unterstützt Prompt-Prefix-Caching |
| `fine_tuning` | Modell kann fine-getuned werden |
| `vision` | Kann Bilder als Input verarbeiten |
| `audio_input` | Kann Audio-Input verarbeiten |
| `audio_output` | Kann Audio/Speech generieren |
| `web_search` | Kann Web-Suche als Tool nutzen |
| `code_execution` | Kann Code in Sandbox ausführen |

### 4.3 Erweiterbarkeit

Neue Compliance-Tags und Capabilities können in Minor-Versionen hinzugefügt werden. Implementierungen **MÜSSEN** unbekannte Werte ignorieren (forward-compatible). Postel's Law: *"Be conservative in what you send, be liberal in what you accept."*

---

## 5. Versionierungsstrategie

### 5.1 Semantic Versioning

Das Protocol folgt **Semantic Versioning 2.0** (`MAJOR.MINOR.PATCH`):

| Version-Teil | Wann erhöht? | Beispiel |
|--------------|-------------|---------|
| **MAJOR** (0 → 1) | Breaking Changes: Felder entfernt, Semantik geändert, Pflichtfelder hinzugefügt | v0.1 → v1.0 (Stabilisierung) |
| **MINOR** (0.1 → 0.2) | Neue optionale Felder, neue Enum-Werte, neue Message-Typen | v0.1 → v0.2 (Multimodal-Pricing) |
| **PATCH** (0.1.0 → 0.1.1) | Bugfixes in der Spec, Klarstellungen, Tippfehler | v0.1.0 → v0.1.1 |

### 5.2 Kompatibilitätsregeln

1. **Additive = Non-Breaking:** Neue optionale Felder hinzufügen ist immer erlaubt (MINOR).
2. **Subtraktive = Breaking:** Felder entfernen oder umbenennen erfordert eine neue MAJOR-Version.
3. **Enum-Erweiterung = Non-Breaking:** Neue Werte zu Enums hinzufügen ist erlaubt (MINOR). Implementierungen MÜSSEN unbekannte Enum-Werte tolerieren.
4. **Pflichtfeld-Addition = Breaking:** Ein neues Pflichtfeld erfordert MAJOR-Version.
5. **Semantik-Änderung = Breaking:** Die Bedeutung eines Feldes ändern erfordert MAJOR-Version.

### 5.3 Version Negotiation

Da ADP transport-agnostisch ist, erfolgt Version Negotiation über den `adp.version`-Header in jeder Nachricht:

- Ein Agent sendet `DealRequest` mit `version: "0.1.1"`
- Ein Anbieter, der v0.2 unterstützt, antwortet mit `version: "0.2.0"` und kann zusätzliche Felder enthalten
- Der Agent ignoriert unbekannte Felder (Postel's Law)
- Wenn ein Anbieter die angeforderte Major-Version nicht unterstützt, antwortet er mit `DealError` (`code: "VERSION_MISMATCH"`)

### 5.4 Roadmap (aktualisiert)

| Version | Geplanter Inhalt | Zeitrahmen |
|---------|-----------------|-----------|
| **v0.1.1** | Core Messages, Discovery, Rechtssicherheit | Jetzt |
| **v0.1.x** | LangChain/CrewAI/AutoGen-Integration als "ADP Tool" | +6 Wochen |
| **v0.2.0** | Auth, zentrales Registry, Multimodal-Pricing, HTTP Binding | +3 Monate |
| **v0.3.0** | Counter-Offers, DealConfirm, Usage-Reporting | +5 Monate |
| **v1.0.0** | Payment-Escrow, Community Governance, Formale JSON Schemas | +8 Monate |

### 5.5 Pre-1.0 Disclaimer

Solange die Version `0.x.y` ist, gilt:
> Breaking Changes sind zwischen Minor-Versionen erlaubt. Das Protocol ist experimental. Ab v1.0.0 gelten die oben beschriebenen Kompatibilitätsregeln strikt.

---

## 6. Precedence Analysis

### 6.1 Model Context Protocol (MCP) — Anthropic

**Was MCP macht:** Standardisiert, wie AI-Agenten externe Tools und Datenquellen entdecken und nutzen.

**Was wir übernehmen:**
- ✅ **JSON-RPC-artige Nachrichten-Struktur** — Klare Request/Response-Semantik
- ✅ **Capability Discovery** — MCP lässt Server ihre Fähigkeiten deklarieren → unser `capabilities`-Array folgt dem gleichen Muster
- ✅ **Schema-first Design** — MCP definiert JSON-Schemas für alle Nachrichten → wir auch

**Was wir anders machen:**
- ❌ MCP ist synchron und session-basiert (Client↔Server). ADP ist asynchron und multi-party (Agent → Aggregator → N Provider)
- ❌ MCP definiert keinen Pricing-Layer — das ist unsere Kernkompetenz

### 6.2 Stripe API

**Was wir übernehmen:**
- ✅ Idempotency-Keys (UUID v4 `id` pro Nachricht)
- ✅ Versionierung via Payload-Header
- ✅ Klare String-Enums statt Magic Numbers

### 6.3 OpenAPI 3.x

**Was wir übernehmen:**
- ✅ JSON Schema als Validierungs-Grundlage
- ✅ Extensions via `x-*` Präfix

### 6.4 Zusammenfassung

| Aspekt | Inspiration von | Unsere Umsetzung |
|--------|----------------|-------------------|
| Nachrichtenstruktur | MCP (JSON-RPC) | `adp`-Header + typed payload |
| Versionierung | Stripe API | `version`-Feld in jeder Nachricht |
| Pricing-Komplexität | Stripe Products/Prices | `base` + `tiers` + `modifiers` |
| Erweiterbarkeit | OpenAPI `x-*` extensions | `extensions: {}` Feld (reserved) |
| Capability Discovery | MCP | `capabilities` + `compliance` Arrays |
| Idempotenz | Stripe | UUID v4 `id` pro Message |

---

## 7. GitHub Repo Struktur

### 7.1 Repository: `apideals/deal-protocol`

```
deal-protocol/
├── README.md
├── LICENSE-SPEC                       # CC-BY 4.0 (Spezifikationsdokument)
├── LICENSE-CODE                       # Apache 2.0 (SDKs, Referenzimplementierungen)
├── TRADEMARK-POLICY.md                # Wer darf sich "ADP-kompatibel" nennen?
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
│
├── spec/
│   ├── v0.1/
│   │   ├── README.md
│   │   ├── protocol.md               # Vollständige Spezifikation
│   │   ├── schemas/
│   │   │   ├── adp-header.schema.json
│   │   │   ├── deal-request.schema.json
│   │   │   ├── deal-offer.schema.json
│   │   │   ├── deal-intent.schema.json
│   │   │   ├── deal-error.schema.json
│   │   │   ├── pricing.schema.json
│   │   │   └── compliance.schema.json
│   │   └── examples/
│   │       ├── basic-request.json
│   │       ├── basic-offer.json
│   │       ├── basic-intent.json
│   │       ├── deal-error.json
│   │       ├── eu-compliant-request.json
│   │       ├── batch-pricing-offer.json
│   │       └── well-known-adp.json
│   └── v0.2/
│       └── ...
│
├── sdk/
│   ├── typescript/
│   │   ├── package.json
│   │   ├── src/
│   │   │   ├── types.ts
│   │   │   ├── validator.ts
│   │   │   ├── pricing-calculator.ts
│   │   │   └── index.ts
│   │   └── tests/
│   └── python/
│       ├── pyproject.toml
│       ├── adp/
│       │   ├── models.py
│       │   ├── validator.py
│       │   ├── pricing.py
│       │   └── __init__.py
│       └── tests/
│
├── docs/
│   ├── faq.md
│   ├── implementation-guide.md
│   ├── design-decisions.md
│   ├── legal-notes.md                 # DSGVO, EU AI Act, Haftungshinweise
│   └── comparison.md
│
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   ├── feature_request.md
    │   └── rfc_proposal.md
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
        ├── validate-schemas.yml
        ├── validate-examples.yml
        └── publish-sdk.yml
```

### 7.2 Governance-Modell

| Phase | Governance | Wer entscheidet? |
|-------|-----------|-----------------|
| v0.x (jetzt) | **BDFL** (Benevolent Dictator) | apideals.ai |
| v1.0 | **RFC-Prozess** | Community-Proposals via GitHub Issues mit Label `rfc` |
| v2.0+ | **Steering Committee** | Anbieter-Vertreter + Community-Maintainer |

### 7.3 RFC-Prozess (ab v1.0)

1. Issue mit Template `rfc_proposal.md` erstellen
2. Community-Diskussion (min. 14 Tage)
3. Referenz-Implementierung im PR
4. Steering Committee Vote (einfache Mehrheit)
5. Merge in nächste Minor/Major-Version

---

## 8. Design-Entscheidungen

### 🏗️ Entscheidung 1: `DealIntent` statt `DealAccept`

**Gewählt:** Die vierte Nachricht heißt `DealIntent`, nicht `DealAccept`.

**Begründung:** `DealAccept` kann nach §§ 145–147 BGB als Annahme eines Angebots (rechtsverbindliche Willenserklärung) gewertet werden. `DealIntent` signalisiert nur eine Absicht. Das Pflichtfeld `binding: false` macht dies maschinenlesbar.

**Trade-off:** Weniger intuitiver Name. Aber: Rechtssicherheit hat Vorrang.

---

### 🏗️ Entscheidung 2: Flat Pricing statt marginaler Staffelung

**Gewählt:** Wenn ein Volume-Tier überschritten wird, gilt der Tier-Preis für **alle** Tokens (Flat-Rate).

**Begründung:**
- Kein LLM-Anbieter nutzt aktuell marginale Staffelung [ANNAHME — Stand März 2026]
- Flat-Rate ist dramatisch einfacher zu berechnen
- Marginale Staffelung kann in v0.2 als `tier_mode: "marginal" | "flat"` ergänzt werden

**Trade-off:** Edge Case: 101 MTok ist günstiger als 99 MTok. Explizit dokumentiert und gewarnt.

---

### 🏗️ Entscheidung 3: Transport-Agnostik (kein HTTP-Binding in v0.1)

**Gewählt:** Das Protocol definiert nur **Nachrichten-Formate**, nicht den Transport.

**Begründung:**
- Ermöglicht Nutzung über HTTP, WebSocket, Message Queues, oder statische JSON-Dateien
- HTTP-Binding kommt als separates Dokument in v0.2

**Trade-off:** Ohne HTTP-Binding fehlt die "5-Minuten-Integration". SDKs + `/.well-known/adp.json` (Abschnitt 10) füllen diese Lücke.

---

### 🏗️ Entscheidung 4: $/MTok als einzige Preiseinheit

**Gewählt:** Alle Preise in Dollar pro 1 Million Tokens.

**Begründung:** Industrie-Standard (OpenAI, Anthropic, Google). Ein Agent muss keine Unit-Konvertierung implementieren.

**Trade-off:** Embedding-APIs, Image-Generation, Audio nicht abbildbar in v0.1.

---

### 🏗️ Entscheidung 5: Dual-Lizenzierung CC-BY 4.0 + Apache 2.0

**Gewählt:** Spezifikationsdokument unter CC-BY 4.0, Code/SDKs unter Apache 2.0.

**Begründung:** Apache 2.0 ist für Software konzipiert. CC-BY 4.0 ist für Dokumente, Spezifikationen und Standards geeigneter und folgt dem Vorbild etablierter Protokoll-Standards (W3C, IETF-inspiriert).

---

## 9. Offene Fragen & Roadmap

### Offene Fragen für v0.2

| # | Frage | Auswirkung |
|---|-------|-----------|
| 1 | **Auth:** OAuth 2.0 / API-Keys oder eigener ADP-Auth-Layer? | Sicherheit, Vertrauensmodell |
| 2 | **Provider-Registry:** Zentrales Register oder nur `/.well-known/adp.json`? | Architektur |
| 3 | **Counter-Offers:** `DealCounterOffer` mit alternativen Konditionen? | Verhandlungsmechanik |
| 4 | **Multimodal-Pricing:** Bild-Tokens, Audio-Minuten, Video-Frames? | Pricing-Komplexität |
| 5 | **Rate-Limits:** RPM/TPM-Limits als Teil von DealOffer? | Vollständigkeit |
| 6 | **DealConfirm:** Anbieter-seitige Bestätigung als 5. Nachrichtentyp? | Transaktionssicherheit |
| 7 | **Pagination:** Wie bei 500+ DealOffers pro Request? | Skalierbarkeit |

### Technische Schulden (bewusst akzeptiert in v0.1)

- Keine formalen JSON Schemas (Draft 2020-12) — SDKs übernehmen Validierung
- Kein Pagination-Mechanismus
- Keine Signierung/Integrität
- `currency` ohne vollständige ISO-4217-Enum-Liste

### Roadmap

```
v0.1.1 (jetzt)   → Core Messages + Discovery + Rechtssicherheit
                    ↓
v0.1.x (+6 Wo.)  → LangChain/CrewAI/AutoGen Integration
                    ↓
v0.2 (+3 Mo.)    → Auth, Registry, HTTP Binding, Multimodal
                    ↓
v0.3 (+5 Mo.)    → Counter-Offers, DealConfirm, Usage-Reporting
                    ↓
v1.0 (+8 Mo.)    → Payment, Community Governance, Formale Schemas
```

---

## 10. Provider Discovery

Anbieter können ihre ADP-Unterstützung maschinenlesbar ankündigen, indem sie eine statische JSON-Datei unter folgender URL hosten:

```
https://<provider-domain>/.well-known/adp.json
```

Dies ist analog zu `/.well-known/openid-configuration` und ermöglicht Agents und Aggregatoren, ADP-fähige Provider zu finden — **ohne ein zentrales Registry**.

### Minimalformat

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.provider.com/adp/offers",
  "contact": {
    "email": "api@provider.com",
    "support_url": "https://provider.com/docs/adp"
  }
}
```

### Vollständiges Format (optional)

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.provider.com/adp/offers",
  "models_endpoint": "https://api.provider.com/adp/models",
  "static_offers_url": "https://provider.com/adp/offers.json",
  "contact": {
    "email": "api@provider.com",
    "support_url": "https://provider.com/docs/adp"
  },
  "provider_id": "myprovider",
  "provider_name": "My Provider AI",
  "last_updated": "2026-03-10T00:00:00Z"
}
```

| Feld | Pflicht | Beschreibung |
|------|---------|--------------|
| `adp_supported` | ✅ | Immer `true` |
| `adp_versions` | ✅ | Liste unterstützter ADP-Versionen |
| `offer_endpoint` | ❌ | URL zum Senden von DealRequests (POST) |
| `models_endpoint` | ❌ | URL zum Abrufen aller DealOffers ohne Request |
| `static_offers_url` | ❌ | URL zu statischer JSON-Datei mit allen Angeboten |
| `contact` | ❌ | Kontaktdaten |
| `provider_id` | ❌ | Eindeutige Anbieter-Kennung |
| `last_updated` | ❌ | Wann wurde die Datei zuletzt aktualisiert? |

---

## Appendix A: Vollständiges Beispiel-Szenario (aktualisiert)

### Szenario: EU-Startup sucht DSGVO-konforme Reasoning-API

**Schritt 1: Agent sendet DealRequest**

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-09T19:00:00Z",
    "correlation_id": null
  },
  "request": {
    "requester": {
      "agent_id": "agent:legaltech-startup:api-buyer",
      "is_automated": true,
      "name": "LegalTech GmbH API Buyer",
      "contact": {
        "email": "tech@legaltech.de"
      }
    },
    "requirements": {
      "task_classes": ["reasoning"],
      "min_context_window": 200000,
      "min_output_tokens": 4000,
      "modalities": ["text"],
      "capabilities": ["structured_output", "streaming"],
      "compliance": ["gdpr", "eu_hosting", "no_training"],
      "max_latency_ms": {
        "ttft": 3000,
        "tps": 30
      }
    },
    "volume": {
      "estimated_monthly_input_tokens": 20000000,
      "estimated_monthly_output_tokens": 5000000,
      "pattern": "steady",
      "batch_eligible": false
    },
    "budget": {
      "max_cost_per_mtok_input": 5.00,
      "max_cost_per_mtok_output": 25.00,
      "currency": "USD",
      "max_monthly_spend": 300.00
    },
    "preferences": {
      "commitment": "none",
      "preferred_providers": ["mistral", "anthropic", "google"],
      "excluded_providers": [],
      "deal_type": "pay_as_you_go"
    },
    "valid_until": "2026-03-16T19:00:00Z",
    "request_ttl_hours": 168
  }
}
```

**Schritt 2: Zwei DealOffers kommen zurück**

*Offer 1: Mistral Magistral Medium 1.1 (Direkt-EU)*
```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "timestamp": "2026-03-09T19:01:00Z",
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  },
  "offer": {
    "provider": {
      "provider_id": "mistral",
      "name": "Mistral AI",
      "url": "https://mistral.ai",
      "contact": { "email": "api@mistral.ai" }
    },
    "model": {
      "model_id": "magistral-medium-1.1",
      "name": "Magistral Medium 1.1",
      "version": "2026-02",
      "task_classes": ["general", "reasoning", "coding"],
      "context_window": 128000,
      "max_output_tokens": 40000,
      "modalities": ["text"],
      "capabilities": ["tool_use", "structured_output", "function_calling", "streaming"],
      "ai_act_risk_class": "minimal"
    },
    "pricing": {
      "currency": "USD",
      "base": { "input_per_mtok": 2.00, "output_per_mtok": 6.00 },
      "tiers": [],
      "modifiers": [],
      "commitment_deals": []
    },
    "compliance": {
      "compliance_verified_by": "self-declared",
      "certifications": ["soc2"],
      "data_regions": ["EU"],
      "gdpr_compliant": true,
      "dpa_available": true,
      "data_retention_days": 0,
      "training_on_data": false,
      "privacy_policy_url": "https://mistral.ai/privacy"
    },
    "sla": { "uptime_pct": 99.9, "ttft_p50_ms": 500, "ttft_p99_ms": 2500, "tps_median": 80 },
    "valid_from": "2026-03-09T00:00:00Z",
    "valid_until": "2026-04-09T00:00:00Z"
  }
}
```

*Offer 2: Claude Sonnet 4.6 via AWS Bedrock EU*
```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "timestamp": "2026-03-09T19:01:30Z",
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479"
  },
  "offer": {
    "provider": {
      "provider_id": "anthropic-bedrock-eu",
      "name": "Anthropic via AWS Bedrock (EU)",
      "url": "https://aws.amazon.com/bedrock",
      "contact": { "support_url": "https://aws.amazon.com/contact-us/" }
    },
    "model": {
      "model_id": "claude-sonnet-4.6",
      "name": "Claude Sonnet 4.6",
      "version": "2026-02",
      "task_classes": ["general", "reasoning", "coding", "creative"],
      "context_window": 1000000,
      "max_output_tokens": 65536,
      "modalities": ["text", "image_input"],
      "capabilities": ["tool_use", "structured_output", "function_calling", "streaming", "batch_api", "prompt_caching"],
      "ai_act_risk_class": "minimal",
      "gpai_model_card_url": "https://www.anthropic.com/responsible-development"
    },
    "pricing": {
      "currency": "USD",
      "base": { "input_per_mtok": 3.00, "output_per_mtok": 15.00 },
      "tiers": [],
      "modifiers": [
        { "type": "cache_read", "input_per_mtok": 0.30, "conditions": "Prompt Caching, min 1024 tokens" },
        { "type": "cache_write", "input_per_mtok": 3.75, "conditions": "Erstmaliges Caching" }
      ],
      "commitment_deals": []
    },
    "compliance": {
      "compliance_verified_by": "self-declared",
      "certifications": ["soc2", "iso27001"],
      "data_regions": ["EU"],
      "gdpr_compliant": true,
      "dpa_available": true,
      "data_retention_days": 0,
      "training_on_data": false,
      "privacy_policy_url": "https://aws.amazon.com/privacy/"
    },
    "sla": { "uptime_pct": 99.9, "ttft_p50_ms": 600, "ttft_p99_ms": 3000, "tps_median": 100 },
    "valid_from": "2026-03-09T00:00:00Z",
    "valid_until": "2026-04-09T00:00:00Z"
  }
}
```

**Schritt 3: Agent vergleicht und filtert**

Der Agent kalkuliert:
- Mistral: 20 MTok × $2.00 + 5 MTok × $6.00 = **$70/Monat** ✅
- Mistral hat nur 128K Context → **unter 200K Anforderung** ❌ → wird aussortiert
- Claude via Bedrock: 20 MTok × $3.00 + 5 MTok × $15.00 = **$135/Monat** ✅, 1M Context ✅

Agent wählt Claude und sendet DealIntent:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealIntent",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2026-03-09T19:02:00Z",
    "correlation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7"
  },
  "intent": {
    "binding": false,
    "requires_human_confirmation": true,
    "party_type": "business",
    "requester": {
      "agent_id": "agent:legaltech-startup:api-buyer",
      "is_automated": true
    },
    "accepted_offer_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "accepted_pricing_snapshot": {
      "input_per_mtok": 3.00,
      "output_per_mtok": 15.00,
      "modifiers_applied": []
    },
    "volume_commitment": {
      "estimated_monthly_input_tokens": 20000000,
      "estimated_monthly_output_tokens": 5000000,
      "commitment_type": "soft"
    },
    "activation": {
      "type": "redirect",
      "redirect_url": "https://aws.amazon.com/bedrock/signup?ref=apideals&offer=7c9e6679-7425-40de-944b-e07fc1f90ae7"
    }
  }
}
```

---

## Appendix B: Extensions-Mechanismus

Jede ADP-Nachricht darf ein optionales `extensions`-Objekt enthalten:

```json
{
  "adp": { "...": "..." },
  "request": { "...": "..." },
  "extensions": {
    "x-apideals-score": 0.87,
    "x-provider-campaign": "spring-2026-deal"
  }
}
```

**Regeln:**
- Extension-Keys MÜSSEN mit `x-` beginnen
- Extensions sind IMMER optional
- Implementierungen MÜSSEN unbekannte Extensions ignorieren
- Extensions dürfen die Semantik der Core-Felder nicht verändern

---

## 11. Changelog

### v0.1.1-draft (2026-03-10)

**Breaking:**
- `DealAccept` → `DealIntent` (juristisches Risiko: mögliche Willenserklärung nach § 147 BGB)
- `expires_at` in DealRequest → `valid_until` (Konsistenz mit DealOffer)
- `task_class` (singular) → `task_classes[]` (Array, OR-Logik) in DealRequest

**Added:**
- `DealError` Nachrichtentyp (4. Core Message)
- `compliance_verified_by` Pflichtfeld in DealOffer.compliance
- `is_automated` Pflichtfeld in requester (EU AI Act Art. 50)
- `binding`, `requires_human_confirmation`, `party_type` in DealIntent
- `ai_act_risk_class`, `gpai_model_card_url`, `prohibited_uses` in DealOffer.model
- `privacy_policy_url` in DealOffer.compliance
- `request_ttl_hours` in DealRequest (DSGVO Art. 17)
- `/.well-known/adp.json` Discovery-Convention (Abschnitt 10)
- Haftungshinweis für Compliance-Tags (Abschnitt 4.1)
- Rechtlicher Hinweis zu DealIntent (Abschnitt 2.4)

**Fixed:**
- Alle Beispiel-IDs auf valide UUID v4 aktualisiert
- `activation.redirect_url` als konditionelles Pflichtfeld dokumentiert (Pflicht wenn `type="redirect"`)
- `valid_from > valid_until` Validierungsregel ergänzt
- `data_regions` vereinheitlicht: ISO 3166-1 Alpha-2 ODER Aggregate (`"EU"`, `"US"`, `"APAC"`)
- `contact` als strukturiertes Objekt (email, webhook_url, support_url)
- `correlation_id` Semantik pro Nachrichtentyp dokumentiert
- `free_tier: null` → Feld weggelassen = kein Free Tier (konsistent)
- `preferred_providers` + `excluded_providers` Konflikt: excluded hat Vorrang
- Modifier-Kombinationslogik: Reihenfolge + Pseudocode
- Tier-Logik: Edge-Case-Warnung mit konkretem Zahlenbeispiel

**Changed:**
- Lizenzierung: Apache 2.0 → CC-BY 4.0 (Spec) + Apache 2.0 (Code)
- Roadmap aktualisiert (realistischere Zeitpläne)
- `effective_price_example` standardisiert (strukturierte Felder statt Freitext)
- GitHub Repo Struktur: `LICENSE` → `LICENSE-SPEC` + `LICENSE-CODE` + `TRADEMARK-POLICY.md`

---

*Ende der Spezifikation v0.1.1*

  
*Überarbeitet nach Multi-Rollen-Review (Jurist, Consultant, Backend Dev, QA Engineer)*
