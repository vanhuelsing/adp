# ADP Implementation Guide

> Implement ADP in an afternoon.

## For Providers (Offer side)

### Step 1: Host /.well-known/adp.json

Create a static JSON file at `https://yourdomain.com/.well-known/adp.json`:

```json
{
  "adp_supported": true,
  "adp_versions": ["0.1.1"],
  "offer_endpoint": "https://api.yourdomain.com/adp/offers",
  "contact": { "email": "api@yourdomain.com" },
  "provider_id": "your-provider-id"
}
```

### Step 2: Accept DealRequests

Create an endpoint that:
- Accepts `POST /adp/offers` with a `DealRequest` body
- Validates the `adp.version` field
- Returns one or more `DealOffer` messages

Minimal validation:
- Check `adp.type === "DealRequest"`
- Check `adp.version` major matches your supported version
- Check `request.valid_until` is in the future (if set)

### Step 3: Return DealOffers

Your DealOffer must include:
- `offer.provider.provider_id` + `offer.provider.name` (required)
- `offer.model.model_id`, `task_classes`, `context_window`, `max_output_tokens`, `modalities`, `capabilities` (all required)
- `offer.pricing.currency` + `offer.pricing.base.input_per_mtok` + `offer.pricing.base.output_per_mtok` (required)
- `offer.compliance.compliance_verified_by` (required)
- `offer.valid_from` + `offer.valid_until` (required, valid_until must be after valid_from)

### Step 4: Handle DealIntent

When you receive a `DealIntent`:
- It is **not a binding contract** (`binding: false`)
- Use it as a purchase signal — redirect the user to your signup flow
- The `activation.redirect_url` in the intent points to your signup page

---

## For Agents (Request side)

### Step 1: Discover Providers

Check `/.well-known/adp.json` on provider domains to find their `offer_endpoint`.

### Step 2: Build a DealRequest

Required fields:
```json
{
  "adp": { "version": "0.1.1", "type": "DealRequest", "id": "<uuid-v4>", "timestamp": "<ISO-8601-UTC>" },
  "request": {
    "requester": { "agent_id": "agent:yourorg:yourbot", "is_automated": true },
    "budget": { "currency": "USD" }
  }
}
```

Add optional filters (`task_classes`, `compliance`, `budget.max_cost_per_mtok_input`) to narrow results.

### Step 3: Evaluate DealOffers

For each offer received:
1. Check `offer.valid_until` is in the future
2. Verify `offer.compliance` matches your requirements
3. Calculate effective cost using the pricing algorithm (see spec Section 3.4)
4. Compare and rank

### Step 4: Send DealIntent

```json
{
  "adp": { "version": "0.1.1", "type": "DealIntent", "id": "<uuid-v4>", ... },
  "intent": {
    "binding": false,
    "requires_human_confirmation": true,
    "accepted_offer_id": "<offer-id>",
    "activation": { "type": "redirect", "redirect_url": "<from-offer>" }
  }
}
```

Then redirect your user (or operator) to the `redirect_url`.

---

## Pricing Calculation

```python
def calculate_cost(input_mtok, output_mtok, pricing):
    # Step 1: Find applicable tier (flat-rate)
    input_price = pricing["base"]["input_per_mtok"]
    output_price = pricing["base"]["output_per_mtok"]
    
    total_mtok = input_mtok + output_mtok
    for tier in sorted(pricing.get("tiers", []), key=lambda t: t["threshold_mtok_monthly"]):
        if total_mtok > tier["threshold_mtok_monthly"]:
            input_price = tier["input_per_mtok"]
            output_price = tier["output_per_mtok"]
    
    # Step 2: Apply modifiers in order
    for modifier in pricing.get("modifiers", []):
        if "discount_pct" in modifier:
            input_price *= (1 - modifier["discount_pct"] / 100)
            output_price *= (1 - modifier["discount_pct"] / 100)
        elif "input_per_mtok" in modifier:
            input_price = modifier["input_per_mtok"]
            if "output_per_mtok" in modifier:
                output_price = modifier["output_per_mtok"]
    
    return (input_mtok * input_price) + (output_mtok * output_price)
```

⚠️ **Flat-Rate Tier Edge Case:** When volume crosses a tier threshold, the lower price applies to **all** tokens — including the first ones. 101 MTok at $1.80 = $181.80, which is cheaper than 99 MTok at $2.00 = $198.00. This is intentional.
