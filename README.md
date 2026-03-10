# apideals Deal Protocol (ADP)

> **The open standard for LLM API deal discovery by AI agents.**

[![License: CC-BY 4.0](https://img.shields.io/badge/Spec%20License-CC--BY%204.0-blue)](https://creativecommons.org/licenses/by/4.0/)
[![License: Apache 2.0](https://img.shields.io/badge/Code%20License-Apache%202.0-green)](https://www.apache.org/licenses/LICENSE-2.0)
[![Version](https://img.shields.io/badge/version-0.1.1--draft-orange)](spec/v0.1/protocol.md)
[![Status](https://img.shields.io/badge/status-draft-yellow)]()

---

## What is ADP?

Today, an AI agent that needs to procure an LLM API must:

1. Manually read pricing pages from 15+ providers (HTML, PDFs, sales contacts)
2. Normalize prices ($/MTok vs $/1k tokens vs credits)
3. Discover hidden conditions (batch discounts, cache hits, free tiers)
4. Verify compliance (GDPR, EU hosting, SOC2, HIPAA)
5. Sign up individually at each provider

**There is no machine-readable standard** for an agent to say: *"I need a reasoning-capable LLM API with EU hosting, max $5/MTok output, min 200K context"* — and automatically receive matching offers.

ADP closes this gap.

## How It Works

ADP defines 4 JSON message types:

| Message | Direction | Meaning |
|---------|-----------|---------|
| **DealRequest** | Agent → Provider | "I need an LLM API with these requirements" |
| **DealOffer** | Provider → Agent | "I offer this model at this price with these guarantees" |
| **DealIntent** | Agent → Provider | "I intend to take this deal" (non-binding signal) |
| **DealError** | Both | Machine-readable error response |

### Quick Example

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-10T12:00:00Z",
    "correlation_id": null
  },
  "request": {
    "requester": {
      "agent_id": "agent:mycompany:procurement-bot",
      "is_automated": true
    },
    "requirements": {
      "task_classes": ["reasoning"],
      "min_context_window": 200000,
      "compliance": ["gdpr", "eu_hosting"]
    },
    "budget": {
      "max_cost_per_mtok_input": 5.00,
      "max_cost_per_mtok_output": 20.00,
      "currency": "USD"
    }
  }
}
```

## Provider Discovery

Providers announce ADP support by hosting a static file at:

```
https://<your-domain>/.well-known/adp.json
```

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.yourprovider.com/adp/offers"
}
```

No central registry needed — agents discover you automatically.

## Specification

📄 **[Full Specification v0.1.1](spec/v0.1/protocol.md)**

Key design decisions:
- **Transport-agnostic** — works over HTTP, WebSocket, or as static JSON files
- **$/MTok pricing** — the industry-standard unit, normalized for easy comparison
- **Compliance-first** — GDPR, SOC2, EU AI Act fields built in
- **Legally safe** — `DealIntent` (not `DealAccept`) is explicitly non-binding
- **Additive versioning** — unknown fields are always ignored (Postel's Law)

## Analogies

| Domain | Standard | What it solves |
|--------|----------|----------------|
| Web APIs | OpenAPI 3.x | Machine-readable API description |
| Payments | Stripe API | Standardized transactions |
| AI Tools | MCP (Anthropic) | Tool discovery for agents |
| **LLM Deals** | **ADP** | **Deal discovery for agents** |

## Roadmap

| Version | Contents | Timeline |
|---------|----------|----------|
| **v0.1.1** (now) | Core messages, discovery, legal safety | Now |
| **v0.1.x** | LangChain / CrewAI / AutoGen integration | +6 weeks |
| **v0.2.0** | Auth, HTTP binding, multimodal pricing | +3 months |
| **v0.3.0** | Counter-offers, DealConfirm | +5 months |
| **v1.0.0** | Payment, community governance, formal JSON schemas | +8 months |

## Repository Structure

```
adp/
├── spec/v0.1/
│   ├── protocol.md          # Full specification
│   ├── schemas/             # JSON Schemas (coming in v0.1.x)
│   └── examples/            # Example messages
├── sdk/
│   ├── typescript/          # TypeScript SDK (coming in v0.1.x)
│   └── python/              # Python SDK (coming in v0.1.x)
├── docs/
│   ├── faq.md
│   └── implementation-guide.md
├── LICENSE-SPEC             # CC-BY 4.0
└── LICENSE-CODE             # Apache 2.0
```

## Governance

- **v0.x:** BDFL — apideals.ai team decides
- **v1.0+:** RFC process via GitHub Issues (`rfc` label)
- **v2.0+:** Steering Committee with provider representatives

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). For protocol changes, open an issue with the `rfc` label.

## License

- **Specification** (`spec/`): [CC-BY 4.0](LICENSE-SPEC)
- **Code** (SDKs, tools): [Apache 2.0](LICENSE-CODE)

---

*Built by [apideals.ai](https://apideals.ai) — the open marketplace for LLM API deals.*
