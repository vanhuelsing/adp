# Contributing to ADP

ADP is open for feedback, implementations, and community contributions.

## How to Contribute

### 📝 Spec Improvements

Found an issue or have a suggestion for the specification?

1. Open an issue in [vanhuelsing/adp/issues](https://github.com/vanhuelsing/adp/issues)
2. Tag with `spec` label
3. Describe the use case and proposed change

**Examples of good spec improvements:**
- New provider examples (DALL-E, ElevenLabs, Runway)
- Additional OAuth flows or API key schemes
- Better error handling patterns
- Clarifications on pricing calculation

### 🔧 New Provider Examples

Want to add a new LLM provider to the examples?

1. Fork the repo
2. Add a new section to [pricing-examples.md](../concepts/spec-v0.2/pricing-examples.md)
3. Include realistic pricing data (cite sources)
4. Run validation: `python3 validate-pricing.py` (coming in v0.2.1)
5. Open a PR with label `provider-example`

**Required for each provider:**
- Token pricing (input/output)
- Image pricing (if supported)
- Audio pricing (if supported)
- Free tier details
- Effective date of pricing
- Link to official pricing page

### 💻 SDK Contributions

Interested in building an SDK in your favorite language?

1. Create a new directory: `sdks/python/`, `sdks/go/`, `sdks/typescript/`, etc.
2. Generate types from JSON schemas (see below)
3. Implement core types and validation
4. Add examples and documentation
5. Open a PR with label `sdk`

**SDK Implementation Checklist:**
- [ ] Validates against ADP JSON schemas
- [ ] Supports all auth schemes (API Key, OAuth 2.0, HMAC)
- [ ] Handles rate limiting headers
- [ ] Includes comprehensive error handling
- [ ] Includes examples and README
- [ ] 80%+ test coverage

**Generating Types from Schemas:**
- Python: `dataclasses-json` or `pydantic`
- Go: `github.com/xeipuuv/gojsonschema` + code generation
- TypeScript: `json-schema-to-typescript`

### 🚀 Roadmap Contributions

See [adp-v0.2.0-roadmap.md](../concepts/adp-v0.2.0-roadmap.md) for planned work.

Current priorities:
1. Video output pricing (v0.3)
2. Commitment deals & volume discounts (v0.2.1)
3. Python SDK (v0.2.1)
4. Go SDK (v0.2.2)

Want to help? Comment on related issues or open a new feature request.

## Code of Conduct

- Be respectful and constructive
- Assume good faith
- Focus on technical merit
- No spam, harassment, or discrimination

## Questions?

- Open an issue with label `question`
- Check existing issues first
- Provide context and examples

---

**Thank you for contributing to ADP!** 🙌

See LICENSE for licensing terms.
