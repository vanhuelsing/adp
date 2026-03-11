# FAQ

## General

**Q: Why not use OpenRouter?**  
A: OpenRouter is a centralized proxy. ADP is a decentralized protocol — providers keep direct customer relationships and avoid middleman margins.

**Q: Is ADP tied to a specific transport?**  
A: No. v0.1 defines message formats only. Use HTTP, WebSocket, or static files. HTTP binding comes in v0.2.

**Q: Is DealIntent legally binding?**  
A: No. `DealIntent` has `"binding": false` and signals non-binding interest. The actual contract forms at the provider's signup URL. Consult legal counsel for your jurisdiction.

**Q: How does authentication work?**  
A: v0.1 is auth-free by design. Authentication will be added in v0.2.

## Pricing

**Q: Why only $/MTok?**  
A: The market has converged on $/MTok. One unit eliminates conversion errors. Non-token pricing comes in v0.2.

**Q: How do tiers work?**  
A: Flat-rate tiers — when you exceed a threshold, the lower price applies to **all** tokens. See the [implementation guide](implementation-guide.md) for details.

**Q: Can modifiers stack?**  
A: Yes. Modifiers apply sequentially (not additively). A 50% discount followed by 10% discount = 55% total discount, not 60%.

## Compliance

**Q: Can I trust self-declared compliance?**  
A: Self-declared means the provider asserts compliance without third-party verification. Always verify independently, especially for GDPR/HIPAA.

**Q: What's `apideals-verified`?**  
A: Reserved for future use. Not implemented in v0.1.

## Contributing

**Q: How do I propose protocol changes?**  
A: Open a GitHub issue with the `rfc` label. See [CONTRIBUTING.md](../CONTRIBUTING.md).

**Q: What contributions are needed?**  
A: Implementer feedback, provider perspectives, agent developer requirements.
