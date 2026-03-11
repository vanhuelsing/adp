.PHONY: help validate test build clean

help:
	@echo "ADP Development Commands"
	@echo ""
	@echo "  make validate  - Validate all example JSON files against schemas"
	@echo "  make test      - Run TypeScript SDK tests"
	@echo "  make build     - Build TypeScript SDK"
	@echo "  make clean     - Clean build artifacts"

validate:
	@cd sdk/typescript && npm install && npm run validate-examples

test:
	@cd sdk/typescript && npm install && npm test

build:
	@cd sdk/typescript && npm install && npm run build

clean:
	@rm -rf sdk/typescript/dist
	@rm -rf sdk/typescript/node_modules
