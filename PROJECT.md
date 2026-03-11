# ADP Project

The **apideals Deal Protocol (ADP)** — An open protocol for AI agents to discover and compare LLM API deals.

## Quick Links

- 🌐 **Website**: https://vanhuelsing.github.io/adp/
- 📖 **Specification**: [spec/v0.1/protocol.md](spec/v0.1/protocol.md)
- 💻 **GitHub**: https://github.com/vanhuelsing/adp
- 📦 **npm**: `@adp/sdk` (coming soon)

## Repository Structure

```
├── spec/v0.1/           # Protocol specification
│   ├── protocol.md      # Full spec
│   ├── schemas/         # JSON Schemas (Draft 2020-12)
│   └── examples/        # Message examples
├── sdk/                 # SDKs
│   └── typescript/      # TypeScript SDK (@adp/sdk)
├── docs/                # Documentation
│   ├── implementation-guide.md
│   ├── security-considerations.md
│   └── faq.md
├── assets/              # Logo and branding
└── index.html           # GitHub Pages landing page
```

## Development

```bash
# Clone
git clone https://github.com/vanhuelsing/adp.git
cd adp

# Validate examples
cd sdk/typescript
npm install
npm run validate-examples

# Run tests
npm test
```

## License

- **Specification**: [CC-BY 4.0](LICENSE-SPEC)
- **Code/SDKs**: [Apache 2.0](LICENSE-CODE)

Published by [vanhuelsing](https://github.com/vanhuelsing).
