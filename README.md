# ADP

**The open protocol for AI agents to discover and compare LLM API deals.**

[![Spec](https://img.shields.io/badge/spec-v0.1.1--draft-blue)](spec/v0.1/protocol.md)
[![License: CC-BY 4.0](https://img.shields.io/badge/license-CC--BY%204.0-lightgrey)](LICENSE-SPEC)
[![License: Apache 2.0](https://img.shields.io/badge/code-Apache%202.0-green)](LICENSE-CODE)

---

## Why ADP?

Today, AI agents procuring LLM APIs face a fragmented mess:

- **15+ pricing pages** to parse (HTML, PDFs, sales calls)
- **Inconsistent units** ($/MTok vs $/1k tokens vs credits)
- **Hidden conditions** (batch discounts, cache hits, free tiers)
- **Manual compliance checks** (GDPR, SOC2, EU hosting)
- **Individual signups** at each provider

**ADP solves this.** One JSON protocol for agents to request, compare, and signal intent for LLM API deals — machine-readable, provider-agnostic, legally safe.

---

## Quick Start

### 1. Provider hosts discovery file

```json
// https://provider.com/.well-known/adp.json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.provider.com/adp/offers"
}
```

### 2. Agent sends DealRequest

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-10T12:00:00Z"
  },
  "request": {
    "requester": {
      "agent_id": "agent:acme:bot",
      "is_automated": true
    },
    "requirements": {
      "task_classes": ["reasoning"],
      "compliance": ["gdpr", "eu_hosting"]
    },
    "budget": {
      "max_cost_per_mtok_output": 20.00,
      "currency": "USD"
    }
  }
}
```

### 3. Provider responds with DealOffer(s)

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealOffer",
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "timestamp": "2026-03-10T12:00:05Z"
  },
  "offer": {
    "provider": { "provider_id": "example", "name": "Example AI" },
    "model": { "model_id": "gpt-large", "task_classes": ["reasoning"] },
    "pricing": {
      "currency": "USD",
      "base": { "input_per_mtok": 3.00, "output_per_mtok": 12.00 }
    },
    "valid_until": "2026-04-10T00:00:00Z"
  }
}
```

### 4. Agent signals DealIntent

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealIntent",
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "correlation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "timestamp": "2026-03-10T12:00:10Z"
  },
  "intent": {
    "binding": false,
    "accepted_offer_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "activation": { "type": "redirect", "redirect_url": "https://example.com/signup" }
  }
}
```

---

## Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `DealRequest` | Agent → Provider | "I need an LLM API with these requirements" |
| `DealOffer` | Provider → Agent | "I offer this model at this price" |
| `DealIntent` | Agent → Provider | "I intend to take this deal" (non-binding) |
| `DealError` | Both | Machine-readable error response |

---

## Documentation

| Resource | Description |
|----------|-------------|
| [Full Specification](spec/v0.1/protocol.md) | Complete protocol reference, field definitions, design decisions |
| [Implementation Guide](docs/implementation-guide.md) | Step-by-step integration for providers and agents |
| [FAQ](docs/faq.md) | Common questions and answers |
| [Examples](spec/v0.1/examples/) | JSON message examples |

---

## Roadmap

| Version | Focus | ETA |
|---------|-------|-----|
| **v0.1.1** | Core messages, discovery, legal safety | Now |
| **v0.2.0** | Auth, HTTP binding, multimodal pricing | +3 months |
| **v0.3.0** | Counter-offers, usage reporting | +5 months |
| **v1.0.0** | Payment escrow, governance, JSON schemas | +8 months |

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). For protocol changes, open an issue with the `rfc` label.

---

## License

- **Specification** ([`spec/`](spec/)): [CC-BY 4.0](LICENSE-SPEC)
- **Code/SDKs** ([`sdk/`](sdk/)): [Apache 2.0](LICENSE-CODE)

---

*Published by [vanhuelsing](https://github.com/vanhuelsing)*
