# adp-sdk

Python SDK for the **Agent Deal Protocol (ADP) v0.2** — the open protocol for AI agents to discover, negotiate, and accept LLM deals from providers.

## Installation

```bash
pip install adp-sdk
```

## Quick start

### 1. Discover a provider

```python
from adp_sdk import ADPClient

with ADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
    discovery = client.discover()
    print(discovery.adp_versions)          # ['0.1.1', '0.2.0']
    print(discovery.offer_endpoint)        # 'https://api.provider.com/adp/offer'
```

### 2. Request a deal offer

```python
import uuid
from adp_sdk import ADPClient, ADPHeader, Budget, DealRequest, DealRequestBody, Requirements, Requester

header = ADPHeader(
    version="0.2.0",
    type="DealRequest",
    id=str(uuid.uuid4()),
    timestamp="2026-03-21T10:00:00Z",
    correlation_id=None,
)

deal_request = DealRequest(
    adp=header,
    request=DealRequestBody(
        requester=Requester(agent_id="agent:myorg:procurement-bot", is_automated=True),
        requirements=Requirements(task_classes=["reasoning"], modalities=["text"]),
        budget=Budget(max_cost_per_mtok_input=5.0, currency="USD"),
    ),
)

with ADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
    offer = client.request_deal(deal_request)
    print(offer.offer.model.name, offer.offer.pricing.base.input_per_mtok)
```

### 3. Send a deal intent

```python
import uuid
from adp_sdk import (
    ADPClient, ADPHeader, Activation, DealIntent, DealIntentBody,
    PricingSnapshot, Requester,
)

intent = DealIntent(
    adp=ADPHeader(
        version="0.2.0",
        type="DealIntent",
        id=str(uuid.uuid4()),
        timestamp="2026-03-21T10:05:00Z",
        correlation_id="<offer-id-from-above>",
    ),
    intent=DealIntentBody(
        binding=False,
        requester=Requester(agent_id="agent:myorg:procurement-bot", is_automated=True),
        accepted_offer_id="<offer-id-from-above>",
        accepted_pricing_snapshot=PricingSnapshot(
            input_per_mtok=3.0,
            output_per_mtok=15.0,
        ),
        activation=Activation(
            type="redirect",
            redirect_url="https://provider.com/signup?deal=...",
        ),
    ),
)

with ADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
    ack = client.send_intent(intent)
    print(ack.acknowledgment.status)       # 'received'
    print(ack.acknowledgment.reference_id) # 'REF-12345'
```

### 4. Health check

```python
with ADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
    health = client.get_health()
    print(health)  # raw dict
```

### 5. Async client

```python
import asyncio
from adp_sdk import AsyncADPClient

async def main():
    async with AsyncADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
        discovery = await client.discover()
        print(discovery.adp_versions)

asyncio.run(main())
```

## Validation helpers

```python
from adp_sdk import validate_deal_request, validate_deal_offer_result

# Quick boolean check
ok = validate_deal_request({"adp": {...}, "request": {...}})

# Detailed field-level errors
result = validate_deal_offer_result(raw_dict)
if not result.valid:
    for err in result.errors:
        print(err)
```

## Error handling

```python
from adp_sdk import ADPClient, ADPConnectionError, ADPHTTPError, ADPValidationError

try:
    with ADPClient("https://api.provider.com", api_key="adp_v2_...") as client:
        discovery = client.discover()
except ADPConnectionError as e:
    print("Network error:", e)
except ADPHTTPError as e:
    print(f"HTTP {e.status_code}:", e.response_body)
except ADPValidationError as e:
    print("Schema error:", e.errors)
```

## Models reference

| Model | Description |
|---|---|
| `ADPHeader` | Protocol envelope (version, type, id, timestamp, correlation_id) |
| `DealRequest` | Agent → Provider: request for offers |
| `DealOffer` | Provider → Agent: pricing and model details |
| `DealIntent` | Agent → Provider: signal of intent to accept |
| `DealIntentAck` | Provider → Agent: acknowledgment of intent |
| `DealError` | Error response with retryable flag |
| `Pricing` | Base price, tiers, modifiers, free tier, commitment deals |
| `Provider` | Provider identity |
| `Model` | Model capabilities, context window, modalities |
| `Requirements` | Task class / modality / compliance filters |
| `Budget` | Per-token and monthly spend caps |
| `Volume` | Estimated token usage and traffic pattern |
| `Preferences` | Commitment type and provider allow/deny lists |
| `WellKnownADP` | Discovery document (`/.well-known/adp.json`) |

## License

Apache-2.0
