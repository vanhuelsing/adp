# ADP Implementation Guide

Implement ADP in an afternoon.

---

## For Providers

### Step 1: Host discovery file

Create `/.well-known/adp.json`:

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.yourdomain.com/adp/offers",
  "contact": { "email": "api@yourdomain.com" }
}
```

### Step 2: Accept DealRequests

Create a `POST /adp/offers` endpoint that:

1. Validates `adp.type === "DealRequest"`
2. Checks `adp.version` major matches your supported version
3. Verifies `request.valid_until` is in the future (if set)
4. Returns one or more `DealOffer` messages

### Step 3: Return DealOffers

Required fields in every DealOffer:

```json
{
  "adp": { "version": "0.1.1", "type": "DealOffer", "id": "...", "timestamp": "..." },
  "offer": {
    "provider": {
      "provider_id": "your-id",
      "name": "Your Provider Name"
    },
    "model": {
      "model_id": "model-id",
      "name": "Model Name",
      "task_classes": ["general"],
      "context_window": 128000,
      "max_output_tokens": 4096,
      "modalities": ["text"],
      "capabilities": []
    },
    "pricing": {
      "currency": "USD",
      "base": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 8.00
      }
    },
    "compliance": {
      "compliance_verified_by": "self-declared"
    },
    "valid_from": "2026-03-10T00:00:00Z",
    "valid_until": "2026-04-10T00:00:00Z"
  }
}
```

### Step 4: Handle DealIntent

When you receive a `DealIntent`:

- It is **not binding** (`binding: false`)
- Use it as a purchase signal
- Redirect the user to your signup flow via `activation.redirect_url`

---

## For Agents

### Step 1: Discover providers

Fetch `/.well-known/adp.json` from provider domains:

```javascript
const response = await fetch('https://provider.com/.well-known/adp.json');
const discovery = await response.json();
const endpoint = discovery.offer_endpoint;
```

### Step 2: Build a DealRequest

Minimal request:

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealRequest",
    "id": "uuid-v4-here",
    "timestamp": "2026-03-10T12:00:00Z"
  },
  "request": {
    "requester": {
      "agent_id": "agent:yourorg:yourbot",
      "is_automated": true
    },
    "budget": {
      "currency": "USD"
    }
  }
}
```

Add filters to narrow results:

```json
{
  "requirements": {
    "task_classes": ["reasoning"],
    "compliance": ["gdpr", "eu_hosting"],
    "min_context_window": 200000
  },
  "budget": {
    "max_cost_per_mtok_input": 5.00,
    "max_cost_per_mtok_output": 20.00
  }
}
```

### Step 3: Evaluate DealOffers

For each offer:

1. Check `offer.valid_until` is in the future
2. Verify `offer.compliance` matches your requirements
3. Calculate effective cost (see below)
4. Compare and rank

### Step 4: Send DealIntent

```json
{
  "adp": {
    "version": "0.1.1",
    "type": "DealIntent",
    "id": "uuid-v4-here",
    "timestamp": "2026-03-10T12:00:10Z",
    "correlation_id": "offer-uuid-here"
  },
  "intent": {
    "binding": false,
    "requires_human_confirmation": true,
    "accepted_offer_id": "offer-uuid-here",
    "activation": {
      "type": "redirect",
      "redirect_url": "https://provider.com/signup"
    }
  }
}
```

---

## Pricing Calculation

```python
def calculate_cost(input_mtok, output_mtok, pricing):
    """Calculate monthly cost based on pricing object."""
    
    # Step 1: Determine applicable tier (flat-rate)
    input_price = pricing["base"]["input_per_mtok"]
    output_price = pricing["base"]["output_per_mtok"]
    
    total_mtok = input_mtok + output_mtok
    for tier in sorted(pricing.get("tiers", []), 
                       key=lambda t: t["threshold_mtok_monthly"]):
        if total_mtok > tier["threshold_mtok_monthly"]:
            input_price = tier["input_per_mtok"]
            output_price = tier["output_per_mtok"]
    
    # Step 2: Apply modifiers in sequence
    for modifier in pricing.get("modifiers", []):
        if "discount_pct" in modifier:
            factor = 1 - modifier["discount_pct"] / 100
            input_price *= factor
            output_price *= factor
        elif "input_per_mtok" in modifier:
            input_price = modifier["input_per_mtok"]
            if "output_per_mtok" in modifier:
                output_price = modifier["output_per_mtok"]
    
    # Step 3: Calculate total
    return (input_mtok * input_price) + (output_mtok * output_price)


# Example usage
pricing = {
    "currency": "USD",
    "base": { "input_per_mtok": 3.00, "output_per_mtok": 12.00 },
    "tiers": [
        { "threshold_mtok_monthly": 100, "input_per_mtok": 2.50, "output_per_mtok": 10.00 }
    ],
    "modifiers": [
        { "type": "batch", "discount_pct": 50 }
    ]
}

cost = calculate_cost(50, 10, pricing)  # 50M input, 10M output
# Result: $160.00 (tier price applies, then 50% batch discount)
```

### Tier Edge Case

With flat-rate tiers, crossing a threshold can make the total cost **lower**:

| Volume | Tier | Calculation | Total |
|--------|------|-------------|-------|
| 99 MTok | Base ($2.00) | 99 × $2.00 | **$198.00** |
| 101 MTok | Tier ($1.80) | 101 × $1.80 | **$181.80** |

This is intentional and matches how major providers structure volume discounts.

---

## Validation Checklist

### DealRequest validation

- [ ] `adp.version` follows semver
- [ ] `adp.id` is valid UUID v4
- [ ] `adp.timestamp` is ISO 8601 UTC
- [ ] `requester.agent_id` is present
- [ ] `requester.is_automated` is boolean
- [ ] `budget.currency` is ISO 4217 (3 uppercase letters)
- [ ] `valid_until` is in the future (if present)

### DealOffer validation

- [ ] All required provider fields present
- [ ] All required model fields present
- [ ] `model.task_classes` is non-empty array
- [ ] `pricing.base.input_per_mtok` and `output_per_mtok` are numbers
- [ ] `valid_until` is after `valid_from`

### DealIntent validation

- [ ] `intent.binding` is `false`
- [ ] `intent.accepted_offer_id` references a valid offer
- [ ] `activation.type` is valid enum value
- [ ] `activation.redirect_url` present if `activation.type === "redirect"`
