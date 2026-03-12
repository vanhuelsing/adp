# ADP

<p align="center">
  <img src="https://raw.githubusercontent.com/vanhuelsing/adp/main/assets/logo.png" width="120" height="120" alt="ADP Logo">
</p>

<h1 align="center">ADP</h1>

<p align="center">
  <strong>The open protocol for AI agents to discover and compare LLM API deals</strong>
</p>

<p align="center">
  <a href="https://github.com/vanhuelsing/adp/releases"><img src="https://img.shields.io/github/v/release/vanhuelsing/adp?include_prereleases" alt="Release"></a>
  <a href="spec/v0.1/protocol.md"><img src="https://img.shields.io/badge/spec-v0.1.1-blue" alt="Spec v0.1.1"></a>
  <a href="spec/v0.2/README.md"><img src="https://img.shields.io/badge/spec-v0.2.0--draft-orange" alt="Spec v0.2.0 Draft"></a>
  <a href="LICENSE-SPEC"><img src="https://img.shields.io/badge/license-CC--BY%204.0-lightgrey" alt="License: CC-BY 4.0"></a>
  <a href="LICENSE-CODE"><img src="https://img.shields.io/badge/code-Apache%202.0-green" alt="License: Apache 2.0"></a>
</p>

<p align="center">
  <a href="https://adp.sh/docs">Documentation</a> •
  <a href="https://adp.sh/playground">Playground</a> •
  <a href="https://github.com/vanhuelsing/adp/discussions">Discussions</a> •
  <a href="https://github.com/vanhuelsing/adp/issues">Issues</a>
</p>

---

## Why ADP?

LLM API pricing is a fragmented mess. Agents today must:

```
❌ Parse 15+ pricing pages (HTML, PDFs, sales calls)
❌ Normalize units ($/MTok vs $/1k tokens vs credits)
❌ Hunt for hidden conditions (batch discounts, cache hits, free tiers)
❌ Manually verify compliance (GDPR, SOC2, EU hosting)
❌ Sign up individually at each provider
```

**ADP solves this.** One JSON protocol for agents to request, compare, and signal intent for LLM API deals — machine-readable, provider-agnostic, legally safe.

```
✅ Standardized JSON messages
✅ Machine-readable pricing with modifiers
✅ Built-in compliance vocabulary
✅ Provider discovery via .well-known
✅ Non-binding intent signaling
```

---

## What's New in v0.2.0 (Draft)

> **[Read the full v0.2.0 spec →](spec/v0.2/README.md)**

| Feature | Description | Spec |
|---------|-------------|------|
| 🔐 **Authentication** | API Key, OAuth 2.0, HMAC Request Signing | [`auth.md`](spec/v0.2/auth.md) |
| 🌐 **HTTP Binding** | Standardized endpoints, headers, status codes, OpenAPI 3.1 | [`http-binding.md`](spec/v0.2/http-binding.md) |
| 🖼️ **Multimodal Pricing** | Image, Audio, Video pricing ($/Megapixel, $/Minute, $/Frame) | [`pricing-multimodal.md`](spec/v0.2/pricing-multimodal.md) |
| ✅ **DealIntentAck** | New 5th message type — provider confirms intent receipt | [`http-binding.md`](spec/v0.2/http-binding.md#25) |
| 📋 **Error Code Registry** | Central registry of all 10 error codes | [`http-binding.md`](spec/v0.2/http-binding.md#3) |

---

## Quick Start

### Provider: Host a discovery file

```bash
# Serve at https://your-domain.com/.well-known/adp.json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1", "0.2.0"],
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

### Provider: Respond with DealOffer(s)

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

---

## Installation

### npm

```bash
npm install @adp/sdk
```

### Python

```bash
pip install adp-sdk
```

### Go

```bash
go get github.com/vanhuelsing/adp/sdk/go
```

---

## Message Types

| Type | Direction | Purpose | Since |
|------|-----------|---------|-------|
| `DealRequest` | Agent → Provider | Request LLM API with requirements | v0.1 |
| `DealOffer` | Provider → Agent | Offer model at specific terms | v0.1 |
| `DealIntent` | Agent → Provider | Signal intent (non-binding) | v0.1 |
| `DealError` | Both | Machine-readable error | v0.1 |
| `DealIntentAck` | Provider → Agent | Confirm intent receipt | v0.2 |

---

## Documentation

### v0.1.1 (Stable)
- **[Full Specification](spec/v0.1/protocol.md)** — Core protocol reference
- **[JSON Schemas](spec/v0.1/schemas/)** — Draft 2020-12 validation schemas
- **[Examples](spec/v0.1/examples/)** — JSON message examples

### v0.2.0 (Draft)
- **[Overview & Migration Guide](spec/v0.2/README.md)** — What's new, how to migrate
- **[Auth & Security](spec/v0.2/auth.md)** — API Key, OAuth 2.0, Rate Limiting
- **[HTTP Binding](spec/v0.2/http-binding.md)** — Endpoints, OpenAPI 3.1, Error Codes
- **[Multimodal Pricing](spec/v0.2/pricing-multimodal.md)** — Image, Audio, Video
- **[JSON Schemas](spec/v0.2/schemas/)** — v0.2.0 validation schemas
- **[Examples](spec/v0.2/examples/)** — v0.2.0 message examples

### General
- **[Implementation Guide](docs/implementation-guide.md)** — Integration guide
- **[Security Considerations](docs/security-considerations.md)** — Threat model & mitigations
- **[FAQ](docs/faq.md)** — Common questions

---

## Validation

All messages can be validated against JSON Schema:

```typescript
import { validateDealRequest } from '@adp/sdk/validator';

const result = validateDealRequest(json);
if (!result.valid) {
  console.error(result.errors);
}
```

---

## Roadmap

| Version | Focus | Status |
|---------|-------|--------|
| **v0.1.1** | Core messages, discovery, legal safety | ✅ Released |
| **v0.2.0** | Auth, HTTP binding, multimodal pricing | 📝 [Draft available](spec/v0.2/README.md) |
| **v0.3.0** | Counter-offers, pagination, usage reporting | 🔜 Planned |
| **v1.0.0** | Payment escrow, governance, formal schemas | 📋 Planned |

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md).

- **Bug reports**: [Issues](https://github.com/vanhuelsing/adp/issues)
- **Feature requests**: [Discussions](https://github.com/vanhuelsing/adp/discussions)
- **Protocol changes**: Open an issue with the `rfc` label

---

## License

- **Specification** ([`spec/`](spec/)): [CC-BY 4.0](LICENSE-SPEC)
- **Code/SDKs** ([`sdk/`](sdk/)): [Apache 2.0](LICENSE-CODE)

---

<p align="center">
  <em>Published by <a href="https://github.com/vanhuelsing">vanhuelsing</a></em>
</p>
