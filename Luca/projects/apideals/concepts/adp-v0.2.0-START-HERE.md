# ADP v0.2.0 — START HERE 🚀

**Für:** Jeder der ADP v0.2.0 arbeitet  
**Datum:** 2026-03-12  
**Status:** Sprint 1 (12.03 – 14.03) — Spec Finalisierung

---

## 📍 Quick Navigation

### Für **Dani** (Auftraggeber)
1. **Executive Summary** (5 min read)
   - `project_management/adp-v020-executive-summary.md`
   - Was ist der Status? Brauchst du mein Input?
2. **Daily Standups** (wenn verfügbar)
   - Discord `#project_calls` — täglich 18:00 UTC
3. **Sign-off Gate** (Freitag 18:00)
   - QA-Report kommt, dann deine Entscheidung

---

### Für **Luca** (Koordination)
1. **Master-Roadmap** (Überblick)
   - `adp-v0.2.0-roadmap.md` — vollständiger Plan, Status, Risiken
2. **Sprint 1 Status** (aktuelles Sprint)
   - `project_management/adp-v020-status-sprint-1.md` — detaillierter 48h-Plan
3. **Subagent Runbook** (Delegation)
   - `project_management/adp-v020-subagent-runbook.md` — Was sagt man jedem Subagent?
4. **Daily Standup Template** (Koordination)
   - `project_management/adp-v020-daily-standup.md` — Discord-Posts vorbereitet

---

### Für **Subagenten** (Ausführung)

#### Protocol Architect (Spec-Schreiber)
1. **Subagent Runbook — Task 1 & 2**
   - `project_management/adp-v020-subagent-runbook.md`
   - Was muss ich machen? Welche Outputs?
2. **Multimodal Pricing Input**
   - Pricing-Struktur aus Roadmap (oben)
   - Provider-Beispiele: DALL-E, Whisper, GPT-4o Vision, Gemini 2.0

#### Backend Dev (Schema-Generierung)
1. **Subagent Runbook — Task 3**
   - Welche 5 Schemas? Wie validieren?
2. **Bestehende Specs**
   - `spec-v0.2/auth.md`, `http-binding.md`, `pricing-multimodal.md`

#### QA Engineer (Review)
1. **Subagent Runbook — Task 4**
   - Volle QA-Durchführung, Checklist, Sign-off
2. **QA-Checklist**
   - `project_management/adp-v020-status-sprint-1.md` → "Erfolgskriterien"

---

## 🎯 Current Status (Stand 12.03 18:38 UTC)

### ✅ Fertig (Draft)
- **Auth Spec** — API Keys, OAuth 2.0, Rate Limiting
- **HTTP Binding Spec** — Endpoints, Status Codes, OpenAPI 3.1

### 🔴 In Arbeit (Kritisch)
- **Multimodal Pricing Spec** — Startet JETZT
- **JSON Schemas** — Morgen
- **QA Review** — Freitag

### 🎯 Ziel
- **Freitag 18:00 UTC:** Alle Specs FINAL + QA Sign-off
- **Montag 15.03:** SDK Phase startet (Python + Go)

---

## 📊 Timeline (Sprint 1)

```
12.03 (Jetzt)          13.03 (Morgen)          14.03 (Freitag)
   |                      |                        |
   ├─ Multimodal Pricing  ├─ JSON Schemas        ├─ QA Review
   │  Finalisierung       │  + Validation        │  + Sign-off
   │                      │                      │
   ├─ Auth/HTTP Finalize  ├─ Luca Review        ├─ FINAL Decision
   │                      │  Prep                │  (Go/At Risk/Blocked)
   └─ [23:00 UTC]         └─ [19:00 UTC]         └─ [18:00 UTC] 🎯
```

---

## 🚀 Subagent Delegation Sequence

**Heute (12.03):**
```
1. spawn Protocol Architect
   → "Create ADP v0.2.0 Multimodal Pricing Spec"
   → input: Pricing structure from roadmap, Provider examples
   → output: pricing-multimodal.md (final, 3-4h)

2. spawn Protocol Architect (after #1 done)
   → "Finalize ADP v0.2.0 Auth & HTTP Binding Specs"
   → input: auth.md, http-binding.md drafts
   → output: Both specs FINAL, OpenAPI 3.1 validated (2-3h)
```

**Morgen (13.03):**
```
3. spawn Backend Dev
   → "Generate & Validate ADP v0.2.0 JSON Schemas"
   → input: All 3 final specs
   → output: 5 validated schemas (4h)

4. Luca (koordiniert, kein spawn)
   → Read all specs, prepare QA checklist (2h)
```

**Freitag (14.03):**
```
5. spawn QA Engineer
   → "Full ADP v0.2.0 QA Review — Go/No-Go Decision"
   → input: All specs + schemas + checklist
   → output: QA-Report with sign-off recommendation (4-5h)

6. Luca
   → Present QA to Dani, get sign-off, mark specs as FINAL
```

---

## 💾 Key Files

### Specs (in `concepts/spec-v0.2/`)
- `auth.md` — Authentication & Security Layer
- `http-binding.md` — HTTP Transport, Endpoints, OpenAPI
- `pricing-multimodal.md` — Image, Audio, Video Pricing (🔴 TBD)

### Schemas (in `concepts/spec-v0.2/schemas/` — TBD)
- `auth.schema.json`
- `http-binding.schema.json`
- `pricing-multimodal.schema.json`
- `deal-request-v0.2.schema.json`
- `deal-offer-v0.2.schema.json`

### Project Management (in `project_management/`)
- `adp-v020-briefing.md` — Initial task briefing
- `adp-v020-status-sprint-1.md` — 48h action plan
- `adp-v020-subagent-runbook.md` — Subagent instructions
- `adp-v020-daily-standup.md` — Standup templates
- `adp-v020-executive-summary.md` — For Dani
- `adp-v020-qa-results.md` — (will be created Friday)

### Master-Roadmap
- `adp-v0.2.0-roadmap.md` — Full picture, all workstreams, timelines

---

## 🎯 Success Criteria (Friday 18:00)

**For "GO to SDK Phase":**
- [ ] All 3 Specs FINAL (no "draft" tag)
- [ ] All 5 JSON Schemas validated
- [ ] QA Engineer gives sign-off
- [ ] Dani gives approval

**For "AT RISK":**
- [ ] Specs done, minor QA issues fixable after SDK-start

**For "BLOCKED":**
- [ ] Critical issues need resolution before SDK-start

---

## ❓ Questions?

- **Dani:** → `project_management/adp-v020-executive-summary.md`
- **Luca:** → `project_management/adp-v020-status-sprint-1.md`
- **Subagents:** → `project_management/adp-v020-subagent-runbook.md`
- **Discord:** → `#project_calls` (daily 18:00 UTC standup)

---

## 🚦 Status-at-a-Glance

| Component | Status | Owner | ETA |
|-----------|--------|-------|-----|
| Auth Spec | 🟡 Draft → FINAL | Protocol Architect | 12.03 23:00 |
| HTTP Binding | 🟡 Draft → FINAL | Protocol Architect | 12.03 23:00 |
| Multimodal Pricing | 🔴 Not Started | Protocol Architect | 12.03 23:00 |
| JSON Schemas | 🟡 Planned | Backend Dev | 13.03 19:00 |
| QA Review | 🟡 Planned | QA Engineer | 14.03 14:30 |
| **Final Decision** | 🟡 Awaiting | Dani | 14.03 18:00 |

---

**Last Updated:** 2026-03-12 18:38 UTC  
**Next Update:** 2026-03-13 18:00 UTC (daily standup)

**Navigation:** [Master Roadmap](./adp-v0.2.0-roadmap.md) | [Status Report](../project_management/adp-v020-status-sprint-1.md) | [Executive Summary](../project_management/adp-v020-executive-summary.md)

