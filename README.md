# ADP

The open protocol for AI agents to discover and compare LLM API deals.

[![Spec v0.1.1](https://img.shields.io/badge/spec-v0.1.1-blue)](spec/v0.1/protocol.md)
[![Spec v0.2.0 Draft](https://img.shields.io/badge/spec-v0.2.0--draft-orange)](spec/v0.2/README.md)
[![License: CC-BY 4.0](https://img.shields.io/badge/license-CC--BY%204.0-lightgrey)](LICENSE-SPEC)
[![License: Apache 2.0](https://img.shields.io/badge/code-Apache%202.0-green)](LICENSE-CODE)

---

## Why ADP?

LLM API pricing is scattered across marketing pages, PDFs, and sales calls, with no standard way for software to read it. Every agent builder ends up writing brittle scrapers and doing manual unit conversion between tokens, credits, and megapixels. ADP defines a small set of JSON messages that let agents request quotes, compare offers, and signal intent -- all machine-readable and provider-agnostic.

## Quick Start

### Provider: Host a discovery file

```bash
# Serve at https://your-domain.com/.well-known/adp.json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.your-domain.com/adp/offer"
}
```

### Agent: Send a DealRequest

```typescript
import { DealRequest } from '@adp/sdk';

const request: DealRequest = {
  adp: {
    version: "0.1.1",
    type: "DealRequest",
    id: crypto.randomUUID(),
    timestamp: new Date().toISOString()
  },
  request: {
    requester: {
      agent_id: "agent:acme:bot",
      is_automated: true
    },
    requirements: {
      task_classes: ["reasoning"],
      compliance: ["gdpr", "eu_hosting"]
    },
    budget: {
      max_cost_per_mtok_output: 20.00,
      currency: "USD"
    }
  }
};
```

### Provider: Respond with a DealOffer

```typescript
import { DealOffer } from '@adp/sdk';

const offer: DealOffer = {
  adp: {
    version: "0.1.1",
    type: "DealOffer",
    id: crypto.randomUUID(),
    correlation_id: request.adp.id,
    timestamp: new Date().toISOString()
  },
  offer: {
    provider: { provider_id: "example", name: "Example AI" },
    model: { model_id: "gpt-large", task_classes: ["reasoning"] },
    pricing: {
      currency: "USD",
      base: { input_per_mtok: 3.00, output_per_mtok: 12.00 }
    },
    valid_until: "2026-04-10T00:00:00Z"
  }
};
```

## Installation

```bash
npm install @adp/sdk
```

```bash
pip install adp-sdk
```

> Go SDK is not yet available. Contributions welcome.

## Message Types

| Type | Direction | Purpose | Since |
|------|-----------|---------|-------|
| `DealRequest` | Agent -> Provider | Request LLM API with requirements | v0.1 |
| `DealOffer` | Provider -> Agent | Offer model at specific terms | v0.1 |
| `DealIntent` | Agent -> Provider | Signal intent (non-binding) | v0.1 |
| `DealError` | Both | Machine-readable error | v0.1 |
| `DealIntentAck` | Provider -> Agent | Confirm intent receipt | v0.2 |

## Documentation

- [v0.1.1 Specification](spec/v0.1/protocol.md) -- Core protocol reference
- [v0.1.1 JSON Schemas](spec/v0.1/schemas/) -- Draft 2020-12 validation schemas
- [v0.1.1 Examples](spec/v0.1/examples/) -- JSON message examples
- [v0.2.0 Draft Overview](spec/v0.2/README.md) -- What's new in v0.2, migration guide
- [v0.2.0 JSON Schemas](spec/v0.2/schemas/) -- v0.2 validation schemas

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| v0.1.1 | Core messages, discovery, legal safety | Released |
| v0.2.0 | Auth, HTTP binding, multimodal pricing | Draft |
| v0.3.0 | Counter-offers, pagination, usage reporting | Planned |
| v1.0.0 | Payment escrow, governance, formal schemas | Planned |

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

- Bug reports: [Issues](https://github.com/vanhuelsing/adp/issues)
- Feature requests / protocol changes: [Discussions](https://github.com/vanhuelsing/adp/discussions)

## License

- **Specification** ([`spec/`](spec/)): [CC-BY 4.0](LICENSE-SPEC)
- **Code/SDKs** ([`sdk/`](sdk/)): [Apache 2.0](LICENSE-CODE)
