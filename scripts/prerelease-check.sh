#!/bin/bash
set -e

echo "🔍 ADP Pre-Release Check"
echo ""

# Check if all required files exist
echo "Checking required files..."
required_files=(
  "README.md"
  "CHANGELOG.md"
  "LICENSE-SPEC"
  "LICENSE-CODE"
  "CONTRIBUTING.md"
  "CODE_OF_CONDUCT.md"
  "index.html"
  "spec/v0.1/protocol.md"
  "spec/v0.1/schemas/adp-header.schema.json"
  "spec/v0.1/schemas/deal-request.schema.json"
  "spec/v0.1/schemas/deal-offer.schema.json"
  "spec/v0.1/schemas/deal-intent.schema.json"
  "spec/v0.1/schemas/deal-error.schema.json"
  "spec/v0.1/schemas/pricing.schema.json"
  "spec/v0.1/schemas/compliance.schema.json"
  "spec/v0.1/schemas/well-known-adp.schema.json"
  "sdk/typescript/package.json"
  "sdk/typescript/src/types.ts"
  "sdk/typescript/src/validator.ts"
)

for file in "${required_files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file MISSING"
    exit 1
  fi
done

echo ""
echo "Validating JSON schemas..."
for file in spec/v0.1/schemas/*.json; do
  if jq empty "$file" 2>/dev/null; then
    echo "  ✅ $(basename $file)"
  else
    echo "  ❌ $(basename $file) INVALID JSON"
    exit 1
  fi
done

echo ""
echo "Validating example files..."
for file in spec/v0.1/examples/*.json; do
  if jq empty "$file" 2>/dev/null; then
    echo "  ✅ $(basename $file)"
  else
    echo "  ❌ $(basename $file) INVALID JSON"
    exit 1
  fi
done

echo ""
echo "✨ All checks passed!"
echo ""
echo "Release checklist:"
echo "  - [ ] Version bumped in package.json"
echo "  - [ ] CHANGELOG.md updated"
echo "  - [ ] Tag created: git tag -a v0.1.1 -m 'Release v0.1.1'"
echo "  - [ ] Tag pushed: git push origin v0.1.1"
echo "  - [ ] npm published: npm publish (in sdk/typescript/)"
