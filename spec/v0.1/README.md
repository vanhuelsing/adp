# ADP Specification v0.1

**Status:** Draft  
**Version:** 0.1.1  

## Contents

- [`protocol.md`](protocol.md) — Full specification with all fields and design decisions
- [`examples/`](examples/) — JSON message examples
- [`schemas/`](schemas/) — JSON Schemas *(coming in v0.1.x)*

## Quick Links

| Resource | Description |
|----------|-------------|
| [Implementation Guide](../../docs/implementation-guide.md) | Step-by-step integration guide |
| [FAQ](../../docs/faq.md) | Common questions |

## Message Types

| Type | Purpose |
|------|---------|
| `DealRequest` | Agent requests LLM API offers |
| `DealOffer` | Provider responds with pricing |
| `DealIntent` | Agent signals non-binding interest |
| `DealError` | Error response |
