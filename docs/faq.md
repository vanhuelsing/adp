# ADP FAQ

## General

**Q: Why not just use OpenRouter?**  
A: OpenRouter is a centralized proxy (marketplace model). ADP is a decentralized protocol. Providers using OpenRouter pay a margin and lose the direct customer relationship. With ADP, providers keep both — and agents can reach them directly without a middleman.

**Q: Is ADP transport-specific?**  
A: No. v0.1 is transport-agnostic — it defines message formats only. Providers can serve ADP over HTTP, WebSocket, or even as static JSON files. An HTTP binding will be added in v0.2.

**Q: Is DealIntent legally binding?**  
A: No. `DealIntent` contains `"binding": false` and is explicitly a non-binding signal of interest. The actual contract is formed at the provider's signup/redirect URL. Please consult legal counsel for your specific jurisdiction.

**Q: What about auth?**  
A: v0.1 is auth-free by design to minimize adoption friction. Authentication will be added in v0.2.

## Pricing

**Q: Why $/MTok as the only unit?**  
A: The LLM API market has converged on $/MTok as the dominant unit. Using one unit eliminates conversion errors. Non-token pricing ($/request, $/minute) will be addressed in v0.2.

**Q: How do I calculate the effective price with tiers and modifiers?**  
A: See the [implementation guide](implementation-guide.md) for a step-by-step example and code.

## Compliance

**Q: Can I trust `compliance_verified_by: "self-declared"`?**  
A: Self-declared means the provider is asserting the compliance claims without third-party verification. Always verify compliance claims independently for your use case, especially for GDPR/HIPAA requirements (Art. 28 GDPR).

**Q: What does `apideals-verified` mean?**  
A: This value is reserved for future use. apideals.ai does not verify compliance claims in v0.1.

## Contributing

**Q: How do I propose a protocol change?**  
A: Open a GitHub issue with the `rfc` label. See [CONTRIBUTING.md](../CONTRIBUTING.md).
