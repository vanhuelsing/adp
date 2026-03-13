# ADP v0.2.0 — Complete Index

**Stand:** 2026-03-12 18:38 UTC  
**Sprint:** 1 (Spec Finalisierung — 12.03 bis 14.03)  
**Status:** 🟡 AT RISK (Multimodal Pricing nicht gestartet)

---

## 📍 Navigation

### 🚀 START HERE (Schnell-Einstieg)
- **[concepts/adp-v0.2.0-START-HERE.md](./concepts/adp-v0.2.0-START-HERE.md)** — Für jeden (5 min overview)

### 👤 Rollen-spezifisch

#### **Dani** (Auftraggeber)
- [Executive Summary](./project_management/adp-v020-executive-summary.md) — Status + what's needed
- [Daily Standups](./project_management/adp-v020-daily-standup.md) — Track progress
- [Master Roadmap](./concepts/adp-v0.2.0-roadmap.md) — Full vision

#### **Luca** (Koordination)
- [Sprint 1 Status](./project_management/adp-v020-status-sprint-1.md) — 48h action plan
- [Daily Standup Template](./project_management/adp-v020-daily-standup.md) — Discord posts
- [Master Roadmap](./concepts/adp-v0.2.0-roadmap.md) — All details

#### **Subagents** (Ausführung)
- [Subagent Runbook](./project_management/adp-v020-subagent-runbook.md) — "Was muss ich machen?"
  - Task 1: Multimodal Pricing Spec
  - Task 2: Auth/HTTP Finalize
  - Task 3: JSON Schemas
  - Task 4: QA Review

---

## 📚 All Documents

### 📋 Project Management

```
project_management/
├── adp-v020-briefing.md                    ← Initial task (existing)
├── adp-v020-status-sprint-1.md             ← 48h action plan (NEW)
├── adp-v020-subagent-runbook.md            ← Delegation instructions (NEW)
├── adp-v020-daily-standup.md               ← Standup templates (NEW)
├── adp-v020-executive-summary.md           ← For Dani (NEW)
└── adp-v020-qa-results.md                  ← (will be created Friday)
```

### 📖 Specifications (Concepts)

```
concepts/
├── adp-v0.2.0-START-HERE.md                ← Quick nav (NEW)
├── adp-v0.2.0-roadmap.md                   ← Master plan (UPDATED)
└── spec-v0.2/
    ├── auth.md                             ✅ Draft (finalize today)
    ├── http-binding.md                     ✅ Draft (finalize today)
    ├── pricing-multimodal.md               🔴 NOT STARTED (today!)
    └── schemas/                            ⏳ (tomorrow)
        ├── auth.schema.json
        ├── http-binding.schema.json
        ├── pricing-multimodal.schema.json
        ├── deal-request-v0.2.schema.json
        └── deal-offer-v0.2.schema.json
```

### 🧠 Memory (Daily Logs)

```
memory/
└── 2026-03-12-adp-v0.2.0-sprint-kickoff.md    ← Session log (NEW)
```

---

## 🎯 Critical Path (48h)

```
12.03 (Heute)          13.03 (Morgen)          14.03 (Freitag)
   |                      |                        |
   ├─ Multimodal          ├─ Schemas             ├─ QA Review
   ├─ Auth/HTTP           ├─ Review              └─ FINAL
   └─ [23:00]             └─ [19:00]                [18:00] 🎯
```

---

## 🚀 Subagent Sequence

1. **Protocol Architect** (TODAY 18:38)
   - Create Multimodal Pricing Spec
   - Finalize Auth/HTTP Specs
   - ETA: 23:00 UTC

2. **Backend Dev** (TOMORROW 09:00)
   - Generate 5 JSON Schemas
   - Validate against test-cases
   - ETA: 19:00 UTC

3. **QA Engineer** (FRIDAY 09:00)
   - Full review of all specs/schemas
   - Go/No-Go recommendation
   - ETA: 14:30 UTC

4. **Dani** (FRIDAY 18:00)
   - Sign-off for SDK phase
   - Go/At-Risk/Blocked decision

---

## 📊 Status Summary

| Component | Status | Owner | ETA | Doc |
|-----------|--------|-------|-----|-----|
| **Multimodal Pricing** | 🔴 NOT STARTED | Protocol Architect | 12.03 23:00 | Runbook T1 |
| **Auth Spec Finalize** | 🟡 In Plan | Protocol Architect | 12.03 23:00 | Runbook T2 |
| **HTTP Binding Finalize** | 🟡 In Plan | Protocol Architect | 12.03 23:00 | Runbook T2 |
| **JSON Schemas** | 🟡 Planned | Backend Dev | 13.03 19:00 | Runbook T3 |
| **QA Review** | 🟡 Planned | QA Engineer | 14.03 14:30 | Runbook T4 |
| **Dani Sign-off** | 🟡 Planned | Dani | 14.03 18:00 | Executive Summary |

---

## 🔑 Key Files (Quick Access)

### For Quick Overview
- [START HERE](./concepts/adp-v0.2.0-START-HERE.md) (5 min)
- [Executive Summary](./project_management/adp-v020-executive-summary.md) (5 min for Dani)

### For Detailed Planning
- [Master Roadmap](./concepts/adp-v0.2.0-roadmap.md) (20 min)
- [Sprint 1 Status](./project_management/adp-v020-status-sprint-1.md) (15 min)

### For Execution
- [Subagent Runbook](./project_management/adp-v020-subagent-runbook.md) (per task)
- [Daily Standup Template](./project_management/adp-v020-daily-standup.md) (18:00 UTC)

### For Reference
- [Memory Log](../../../memory/2026-03-12-adp-v0.2.0-sprint-kickoff.md) (session notes)

---

## ✅ What's Ready

- ✅ All docs created
- ✅ Runbooks detailed
- ✅ Timeline realistic
- ✅ Success criteria clear
- ✅ Ready to spawn first subagent

**Next Step:** Spawn Protocol Architect → Multimodal Pricing Spec (TODAY NOW)

---

## 🆘 In Case of Emergency

**Blocker during sprint?**
1. Post in Discord `#project_calls` immediately (don't wait for standup)
2. Include: What? Why? Impact? Solution?
3. Luca will adjust plan + communicate to Dani

**Missing something?**
- Check [START HERE](./concepts/adp-v0.2.0-START-HERE.md)
- Or [Master Roadmap](./concepts/adp-v0.2.0-roadmap.md)

**Questions about subagent task?**
- Check [Subagent Runbook](./project_management/adp-v020-subagent-runbook.md) for your task number

---

**Index Created:** 2026-03-12 18:38 UTC  
**Updated:** [Daily]  
**Status:** 🟡 Sprint 1 IN PROGRESS

