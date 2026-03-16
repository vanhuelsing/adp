# ADP v0.2.0 — Multimodal Pricing Specification

**Version:** 0.2.0-draft  
**Specification:** Extension of the Pricing Schema for Images, Audio, Video
**Based on:** ADP v0.1.1 (Section 3: Pricing Schema)
**Status:** Draft
**Author:** Protocol Architect

---

## 1. Overview

This document extends the ADP Pricing Schema to cover multimodal content. While v0.1.1 only supported token-based text pricing, v0.2.0 enables pricing for images, audio, and video.

### Design Principles

| Principle | Implementation |
|-----------|---------------|
| **Backwards Compatible** | `pricing.base` remains for text-only APIs |
| **Industry-Standard Units** | Megapixels, minutes, frames — no custom inventions |
| **Flexible** | Providers can define only the modalities they use |
| **Predictable** | Clear formulas for total costs |

---

## 2. New Modalities

### 2.1 Overview

| Modality | Input Unit | Output Unit | Example Providers |
|----------|------------|-------------|-------------------|
| **Text** | $/MTok | $/MTok | All LLMs |
| **Image Input** | $/Megapixel | — | GPT-4o Vision, Claude Vision |
| **Image Output** | — | $/Image oder $/Megapixel | DALL-E, Midjourney, Stable Diffusion |
| **Audio Input** | $/Minute | — | Whisper, Gemini Audio |
| **Audio Output** | — | $/Character oder $/Minute | ElevenLabs, OpenAI TTS |
| **Video Input** | $/Frame oder $/Second | — | Gemini 2.0 Flash Video |
| **Video Output** | — | $/Frame oder $/Second | Runway, Pika¹ |

¹ **Deferred to v0.3** — Video output pricing APIs are still too unstable for standardization. Defined pricing models are in development for future versions.

### 2.2 Why These Units?

| Modality | Unit | Rationale |
|----------|------|-----------|
| Image | Megapixel | Industry standard in image processing (MP = Million Pixels) |
| Audio | Minute | Intuitive for users ("5 minutes of audio") |
| Audio Output | Character | TTS providers (ElevenLabs) use character-based pricing |
| Video | Frame/Second | Frame for short clips, second for longer videos |

---

## 3. Schema Extension

### 3.1 New Pricing Object

```json
{
  "pricing": {
    "currency": "USD",
    
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 10.00
    },
    
    "modalities": {
      "text": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 10.00
      },
      "image_input": {
        "per_megapixel": 0.50,
        "minimum_megapixels": 0.25
      },
      "image_output": {
        "per_image": 0.04,
        "per_megapixel": 0.10,
        "resolutions": {
          "1024x1024": { "per_image": 0.04 },
          "1792x1024": { "per_image": 0.08 }
        }
      },
      "audio_input": {
        "per_minute": 0.006,
        "minimum_minutes": 0.1
      },
      "audio_output": {
        "per_character": 0.000015,
        "per_minute": 0.015
      },
      "video_input": {
        "per_frame": 0.001,
        "per_second": 0.03,
        "fps_baseline": 30
      }
    },
    
    "tiers": [...],
    "modifiers": [...],
    "free_tier": {...}
  }
}
```

### 3.2 Text (Default)

Text pricing moves from the `base` object into `modalities.text`. `base` is retained for backwards compatibility.

```json
{
  "pricing": {
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 10.00
    },
    "modalities": {
      "text": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 10.00,
        "cached_input_per_mtok": 0.50
      }
    }
  }
}
```

**Rule (UPDATED - v0.2.0 Consistency):** When `modalities.text` is present, `base.input_per_mtok` and `base.output_per_mtok` MUST have identical values to `modalities.text.input_per_mtok` and `modalities.text.output_per_mtok`. This ensures that v0.1.1 clients (which only read `base`) and v0.2.0 clients (which prefer `modalities.text`) see the same prices.

**Validation:** Validators SHOULD emit a warning when `base` and `modalities.text` diverge and flag discrepancies. When `modalities.text` exists, a mismatch is a consistency error.

**Example (CORRECTED):**
```json
{
  "pricing": {
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 10.00
    },
    "modalities": {
      "text": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 10.00,
        "cached_input_per_mtok": 0.50
      }
    }
  }
}
```

Consistent: `base` and `modalities.text` have identical input/output values.

### 3.3 Image Input

**Schema:**
```json
{
  "image_input": {
    "per_megapixel": 0.50,
    "minimum_megapixels": 0.25,
    "tiers": [
      {
        "threshold_megapixels_monthly": 1000,
        "per_megapixel": 0.40
      }
    ],
    "modifiers": [
      {
        "type": "detail_mode",
        "high_detail_per_megapixel": 1.00,
        "low_detail_per_megapixel": 0.25
      }
    ]
  }
}
```

**Example: GPT-4o Vision**
```json
{
  "image_input": {
    "per_megapixel": 0.50,
    "minimum_megapixels": 0.25,
    "notes": "Images are rescaled to fit within 2048x2048 and then tiles of 512x512 are created. Each tile costs a fixed amount."
  }
}
```

**Calculation:**
```
cost = max(actual_megapixels, minimum_megapixels) x per_megapixel

Example:
- 1920x1080 image = 2.07 Megapixels
- Minimum billing: 0.25 MP
- Cost: 2.07 x $0.50 = $1.035
```

### 3.4 Image Output

**Schema:**
```json
{
  "image_output": {
    "per_image": 0.04,
    "per_megapixel": 0.10,
    "resolutions": {
      "1024x1024": { "per_image": 0.04 },
      "1024x1792": { "per_image": 0.08 },
      "1792x1024": { "per_image": 0.08 }
    },
    "quality_tiers": {
      "standard": { "multiplier": 1.0 },
      "hd": { "multiplier": 2.0 }
    }
  }
}
```

**Example: DALL-E 3**
```json
{
  "image_output": {
    "resolutions": {
      "1024x1024": { "per_image": 0.04 },
      "1024x1792": { "per_image": 0.08 },
      "1792x1024": { "per_image": 0.08 }
    },
    "quality": {
      "standard": { "per_image": 0.04 },
      "hd": { "per_image": 0.08 }
    }
  }
}
```

### 3.5 Audio Input

**Schema:**
```json
{
  "audio_input": {
    "per_minute": 0.006,
    "minimum_minutes": 0.1,
    "tiers": [
      {
        "threshold_hours_monthly": 100,
        "per_minute": 0.005
      }
    ]
  }
}
```

**Example: Whisper API**
```json
{
  "audio_input": {
    "per_minute": 0.006,
    "minimum_minutes": 0.0,
    "notes": "Rounded to the nearest second"
  }
}
```

**Calculation:**
```
cost = ceil(audio_seconds / 60, 0.1) x per_minute

Example:
- 3 minutes 45 seconds = 3.75 minutes
- Rounded to 0.1-minute increments: 3.8 minutes
- Cost: 3.8 x $0.006 = $0.0228
```

### 3.6 Audio Output (TTS)

**Schema:**
```json
{
  "audio_output": {
    "per_character": 0.000015,
    "per_minute": 0.015,
    "minimum_characters": 1,
    "voices": {
      "standard": { "per_character": 0.000015 },
      "premium": { "per_character": 0.000030 }
    }
  }
}
```

**Example: ElevenLabs**
```json
{
  "audio_output": {
    "per_character": 0.000018,
    "free_tier": {
      "monthly_characters": 10000
    }
  }
}
```

**Example: OpenAI TTS**
```json
{
  "audio_output": {
    "per_million_characters": 15.00,
    "per_character": 0.000015,
    "models": {
      "tts-1": { "per_million_characters": 15.00 },
      "tts-1-hd": { "per_million_characters": 30.00 }
    }
  }
}
```

### 3.7 Video Input

**Schema:**
```json
{
  "video_input": {
    "per_frame": 0.001,
    "per_second": 0.03,
    "fps_baseline": 30,
    "maximum_duration_seconds": 3600
  }
}
```

**Calculation (Frame-based):**
```
cost = frame_count x per_frame

Example:
- 30 seconds of video @ 30 FPS = 900 frames
- Cost: 900 x $0.001 = $0.90
```

**Calculation (Second-based):**
```
cost = duration_seconds x per_second

Example:
- 30 seconds of video
- Cost: 30 x $0.03 = $0.90
```

**Example: Gemini 2.0 Flash Video**
```json
{
  "video_input": {
    "per_second": 0.03,
    "fps_baseline": 1,
    "notes": "Video is sampled at 1 FPS for processing. Price is per second of video duration."
  }
}
```

---

## 4. Mixed Modalities

### 4.1 Bundle Pricing

Some models (e.g. GPT-4o) support text + images in a single request.

```json
{
  "pricing": {
    "modalities": {
      "text": {
        "input_per_mtok": 2.50,
        "output_per_mtok": 10.00
      },
      "image_input": {
        "per_megapixel": 0.50,
        "fixed_per_image": 0.005,
        "notes": "Images are converted to tokens. ~170 tokens per tile."
      }
    },
    "bundles": [
      {
        "name": "vision_request",
        "includes": ["text", "image_input"],
        "pricing": {
          "text_input_per_mtok": 2.50,
          "image_input_per_megapixel": 0.50
        }
      }
    ]
  }
}
```

### 4.2 Token Equivalents

Some providers convert images/audio into tokens:

```json
{
  "image_input": {
    "token_equivalent": {
      "tokens_per_tile": 170,
      "tile_size": "512x512",
      "pricing_via_text": true
    }
  }
}
```

This signals that image input is billed via text pricing.

**Responsibility for Cost Calculation:**

- **Provider** MUST perform the final cost calculation and report actual costs in the invoice/usage report. The provider has full visibility into all internally relevant factors (e.g. exact tile sizes after rescaling).

- **Agent** MAY use the `token_equivalent` information to estimate costs (e.g. for budget checks before the request). This estimate is **informative and non-binding** — the provider may correct the actual costs.

- **Note:** Tile logic is provider-specific:
  - GPT-4o: 512x512 tiles, max 2048x2048 rescaling
  - Other providers may use different logic

  The `token_equivalent` fields are informative — the actual token count can (and often will) differ from agent estimates.

- **Best Practice for Providers:** Providers that set `pricing_via_text: true` SHOULD document the typical token count per image size in the `notes` field of their DealOffer. Example:
  ```json
  {
    "image_input": {
      "token_equivalent": {
        "tokens_per_tile": 170,
        "pricing_via_text": true
      },
      "notes": "Typical token counts: 512×512=170 tokens, 1024×1024=680 tokens, 2048×2048=2720 tokens"
    }
  }
  ```

---

## 5. JSON Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://apideals.ai/schemas/pricing-v0.2.schema.json",
  "title": "ADP Multimodal Pricing Schema",
  "type": "object",
  "properties": {
    "currency": {
      "type": "string",
      "pattern": "^[A-Z]{3}$"
    },
    
    "base": {
      "$ref": "#/$defs/textPricing"
    },
    
    "modalities": {
      "type": "object",
      "properties": {
        "text": { "$ref": "#/$defs/textPricing" },
        "image_input": { "$ref": "#/$defs/imageInputPricing" },
        "image_output": { "$ref": "#/$defs/imageOutputPricing" },
        "audio_input": { "$ref": "#/$defs/audioInputPricing" },
        "audio_output": { "$ref": "#/$defs/audioOutputPricing" },
        "video_input": { "$ref": "#/$defs/videoInputPricing" }
      }
    },
    
    "tiers": {
      "type": "array",
      "items": { "$ref": "#/$defs/tier" }
    },
    
    "modifiers": {
      "type": "array",
      "items": { "$ref": "#/$defs/modifier" }
    },
    
    "free_tier": { "$ref": "#/$defs/freeTier" }
  },
  
  "$defs": {
    "textPricing": {
      "type": "object",
      "properties": {
        "input_per_mtok": { "type": "number", "minimum": 0 },
        "output_per_mtok": { "type": "number", "minimum": 0 },
        "cached_input_per_mtok": { "type": "number", "minimum": 0 }
      }
    },
    
    "imageInputPricing": {
      "type": "object",
      "properties": {
        "per_megapixel": { "type": "number", "minimum": 0 },
        "minimum_megapixels": { "type": "number", "minimum": 0 },
        "fixed_per_image": { "type": "number", "minimum": 0 },
        "token_equivalent": {
          "type": "object",
          "properties": {
            "tokens_per_tile": { "type": "integer" },
            "tile_size": { "type": "string" },
            "pricing_via_text": { "type": "boolean" }
          }
        }
      }
    },
    
    "imageOutputPricing": {
      "type": "object",
      "properties": {
        "per_image": { "type": "number", "minimum": 0 },
        "per_megapixel": { "type": "number", "minimum": 0 },
        "resolutions": {
          "type": "object",
          "additionalProperties": {
            "type": "object",
            "properties": {
              "per_image": { "type": "number", "minimum": 0 }
            }
          }
        }
      }
    },
    
    "audioInputPricing": {
      "type": "object",
      "properties": {
        "per_minute": { "type": "number", "minimum": 0 },
        "minimum_minutes": { "type": "number", "minimum": 0 },
        "per_hour": { "type": "number", "minimum": 0 }
      }
    },
    
    "audioOutputPricing": {
      "type": "object",
      "properties": {
        "per_character": { "type": "number", "minimum": 0 },
        "per_minute": { "type": "number", "minimum": 0 },
        "minimum_characters": { "type": "integer", "minimum": 0 },
        "per_million_characters": { "type": "number", "minimum": 0 }
      }
    },
    
    "videoInputPricing": {
      "type": "object",
      "properties": {
        "per_frame": { "type": "number", "minimum": 0 },
        "per_second": { "type": "number", "minimum": 0 },
        "fps_baseline": { "type": "integer", "minimum": 1 },
        "maximum_duration_seconds": { "type": "integer", "minimum": 1 }
      }
    },
    
    // video_output: Deferred to v0.3 — see Section 2.1
    // Video output pricing schemas are not yet standardized due to API instability
    // across vendors (Runway, Pika, etc.). Formal definitions planned for v0.3.
    
    "tier": {
      "type": "object",
      "properties": {
        "threshold_mtok_monthly": { "type": "number", "minimum": 0 },
        "input_per_mtok": { "type": "number", "minimum": 0 },
        "output_per_mtok": { "type": "number", "minimum": 0 }
      }
    },
    
    "modifier": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["batch", "cache_read", "cache_write", "detail_mode", "quality"]
        },
        "discount_pct": { "type": "number", "minimum": 0, "maximum": 99 },
        "input_per_mtok": { "type": "number", "minimum": 0 },
        "conditions": { "type": "string" }
      }
    },
    
    "freeTier": {
      "type": "object",
      "properties": {
        "monthly_input_tokens": { "type": "integer", "minimum": 0 },
        "monthly_output_tokens": { "type": "integer", "minimum": 0 },
        "monthly_characters": { "type": "integer", "minimum": 0 },
        "monthly_images": { "type": "integer", "minimum": 0 },
        "monthly_minutes": { "type": "number", "minimum": 0 },
        "rate_limit_rpm": { "type": "integer", "minimum": 0 }
      }
    }
  }
}
```

---

## 6. Examples

### 6.1 GPT-4o (Text + Vision)

```json
{
  "pricing": {
    "currency": "USD",
    "base": {
      "input_per_mtok": 2.50,
      "output_per_mtok": 10.00
    },
    "modalities": {
      "text": {
        "input_per_mtok": 2.50,
        "output_per_mtok": 10.00,
        "cached_input_per_mtok": 1.25
      },
      "image_input": {
        "token_equivalent": {
          "tokens_per_tile": 170,
          "tile_size": "512x512",
          "pricing_via_text": true
        },
        "notes": "Images are tiled into 512x512 squares. Low detail mode uses a single tile."
      }
    },
    "modifiers": [
      {
        "type": "cache_read",
        "input_per_mtok": 1.25,
        "conditions": "Cached prompt tokens"
      }
    ]
  }
}
```

**Cost Example Vision Request:**
```
- 1000 input tokens text: 1K x $2.50/MTok = $0.0025
- 1920x1080 image: ~12 tiles (low detail) = 2040 tokens = $0.0051
- 200 output tokens: 0.2K x $10.00/MTok = $0.002
- Total: ~$0.0096
```

### 6.2 DALL-E 3 (Image Generation)

```json
{
  "pricing": {
    "currency": "USD",
    "modalities": {
      "image_output": {
        "resolutions": {
          "1024x1024": { "per_image": 0.04 },
          "1024x1792": { "per_image": 0.08 },
          "1792x1024": { "per_image": 0.08 }
        },
        "quality": {
          "standard": { 
            "1024x1024": { "per_image": 0.04 },
            "1024x1792": { "per_image": 0.08 }
          },
          "hd": {
            "1024x1024": { "per_image": 0.08 },
            "1024x1792": { "per_image": 0.12 }
          }
        }
      }
    }
  }
}
```

### 6.3 Whisper (Audio Transcription)

```json
{
  "pricing": {
    "currency": "USD",
    "modalities": {
      "audio_input": {
        "per_minute": 0.006,
        "minimum_minutes": 0.0,
        "notes": "Rounded to the nearest second. No minimum charge."
      }
    },
    "free_tier": {
      "rate_limit_rpm": 50
    }
  }
}
```

### 6.4 ElevenLabs (TTS)

```json
{
  "pricing": {
    "currency": "USD",
    "modalities": {
      "audio_output": {
        "per_character": 0.000018,
        "per_thousand_characters": 0.018,
        "voices": {
          "standard": { "per_character": 0.000018 },
          "clone": { "per_character": 0.000030 }
        }
      }
    },
    "free_tier": {
      "monthly_characters": 10000
    }
  }
}
```

### 6.5 Gemini 2.0 Flash (Multimodal)

```json
{
  "pricing": {
    "currency": "USD",
    "modalities": {
      "text": {
        "input_per_mtok": 0.10,
        "output_per_mtok": 0.40
      },
      "image_input": {
        "per_megapixel": 0.05,
        "minimum_megapixels": 0.01
      },
      "video_input": {
        "per_second": 0.03,
        "notes": "Video sampled at 1 FPS"
      },
      "audio_input": {
        "per_minute": 0.006
      }
    }
  }
}
```

---

## 7. Calculation Logic

### 7.1 Calculation Order (Calculation Pipeline)

Cost calculation follows a strict order:

1. **Tiers** — Determine the volume tier based on monthly usage
2. **Bundles** — Apply bundle pricing (if present) for combined modalities
3. **Modifiers** — Apply discounts/surcharges to the resulting costs

**Example: Text + Image, with Batch Modifier**
```
Step 1: Text cost = 1K tokens x $2.50/MTok = $2.50
Step 2: Image cost = 2 MP x $0.50/MP = $1.00
Step 3: Bundle check — does a "text+image_input" bundle exist?
        -> Yes: Bundle price = $2.50 (for both combined)
Step 4: Modifiers — Batch discount = 20%
        -> Final cost: $2.50 x 0.80 = $2.00
```

### 7.2 Pseudocode

```python
def calculate_cost(pricing, usage):
    total_cost = 0
    
    # Step 1: Determine tier based on monthly volume
    applied_tier = determine_tier(pricing["tiers"], usage)

    # Step 2: Calculate modality costs
    modal_costs = {}

    # Text costs
    if "text" in usage:
        text = usage["text"]
        text_pricing = applied_tier.get("modalities", {}).get("text", pricing["modalities"]["text"])
        
        input_cost = text["input_mtok"] * text_pricing["input_per_mtok"]
        output_cost = text["output_mtok"] * text_pricing["output_per_mtok"]
        modal_costs["text"] = input_cost + output_cost
    
    # Image input costs
    if "image_input" in usage:
        image = usage["image_input"]
        image_pricing = applied_tier.get("modalities", {}).get("image_input", pricing["modalities"]["image_input"])
        
        if "token_equivalent" in image_pricing:
            # Token-based billing (e.g. GPT-4o Vision)
            tokens = image["tiles"] * image_pricing["token_equivalent"]["tokens_per_tile"]
            cost = tokens / 1000000 * pricing["modalities"]["text"]["input_per_mtok"]
        else:
            # Megapixel-based billing
            megapixels = max(image["megapixels"], image_pricing.get("minimum_megapixels", 0))
            cost = megapixels * image_pricing["per_megapixel"]
        
        modal_costs["image_input"] = cost
    
    # Image output costs
    if "image_output" in usage:
        image = usage["image_output"]
        image_pricing = applied_tier.get("modalities", {}).get("image_output", pricing["modalities"]["image_output"])
        
        if "resolutions" in image_pricing and image["resolution"] in image_pricing["resolutions"]:
            cost = image_pricing["resolutions"][image["resolution"]]["per_image"]
        else:
            cost = image["count"] * image_pricing.get("per_image", 0)
        
        modal_costs["image_output"] = cost
    
    # Audio input costs
    if "audio_input" in usage:
        audio = usage["audio_input"]
        audio_pricing = applied_tier.get("modalities", {}).get("audio_input", pricing["modalities"]["audio_input"])
        
        minutes = max(audio["minutes"], audio_pricing.get("minimum_minutes", 0))
        modal_costs["audio_input"] = minutes * audio_pricing["per_minute"]
    
    # Audio output costs
    if "audio_output" in usage:
        audio = usage["audio_output"]
        audio_pricing = applied_tier.get("modalities", {}).get("audio_output", pricing["modalities"]["audio_output"])
        
        if "characters" in audio:
            modal_costs["audio_output"] = audio["characters"] * audio_pricing.get("per_character", 0)
        elif "minutes" in audio:
            modal_costs["audio_output"] = audio["minutes"] * audio_pricing.get("per_minute", 0)
    
    # Video input costs
    if "video_input" in usage:
        video = usage["video_input"]
        video_pricing = applied_tier.get("modalities", {}).get("video_input", pricing["modalities"]["video_input"])
        
        if "per_second" in video_pricing:
            modal_costs["video_input"] = video["seconds"] * video_pricing["per_second"]
        elif "per_frame" in video_pricing:
            modal_costs["video_input"] = video["frames"] * video_pricing["per_frame"]
    
    # Step 3: Bundle pricing — overrides individual modality prices
    if "bundles" in pricing:
        for bundle in pricing["bundles"]:
            # Check if all modalities in the bundle are present in usage
            bundle_modalities = set(bundle["includes"])
            usage_modalities = set(usage.keys())
            
            if bundle_modalities.issubset(usage_modalities):
                # Bundle applies — replace individual costs with bundle price
                bundle_cost = calculate_bundle_cost(bundle["pricing"], usage)
                
                # Remove original costs for modalities included in the bundle
                for modality in bundle["includes"]:
                    if modality in modal_costs:
                        del modal_costs[modality]
                
                # Add bundle costs
                total_cost += bundle_cost
                break  # Only the first matching bundle is applied

    # Add remaining modality costs (not included in bundle)
    total_cost += sum(modal_costs.values())
    
    # Step 4: Modifiers (discounts/surcharges)
    if "modifiers" in pricing:
        for modifier in pricing["modifiers"]:
            if modifier["type"] == "batch" and usage.get("batch_enabled"):
                total_cost *= (1 - modifier["discount_pct"] / 100)
            elif modifier["type"] == "cache_read" and usage.get("cached_tokens", 0) > 0:
                # Cache-Read: cheaper token costs
                total_cost = apply_cache_modifier(total_cost, modifier)
    
    return total_cost


def calculate_bundle_cost(bundle_pricing, usage):
    """Calculate costs for a bundle based on the bundle pricing."""
    cost = 0
    
    if "text_input_per_mtok" in bundle_pricing and "text" in usage:
        cost += usage["text"]["input_mtok"] * bundle_pricing["text_input_per_mtok"]
        cost += usage["text"]["output_mtok"] * bundle_pricing.get("text_output_per_mtok", 0)
    
    if "image_input_per_megapixel" in bundle_pricing and "image_input" in usage:
        megapixels = usage["image_input"]["megapixels"]
        cost += megapixels * bundle_pricing["image_input_per_megapixel"]
    
    return cost
```

### 7.3 Numerical Example: GPT-4o Vision + Batch

**Scenario:**
- Model: GPT-4o
- Request: 500 tokens text input + 1920x1080 image (2.07 MP)
- Modifier: Batch processing (20% discount)

**Prices:**
```json
{
  "modalities": {
    "text": {
      "input_per_mtok": 2.50,
      "output_per_mtok": 10.00
    },
    "image_input": {
      "token_equivalent": {
        "tokens_per_tile": 170,
        "pricing_via_text": true
      }
    }
  },
  "modifiers": [
    {
      "type": "batch",
      "discount_pct": 20
    }
  ]
}
```

**Calculation:**

```
Step 1: Tier determination
  -> No tier defined, use standard prices

Step 2: Modality costs
  Text input: 500 tokens / 1,000,000 = 0.0005 MTok
              0.0005 x $2.50 = $0.00125

  Image input: 2.07 MP x $0.50/MP = $1.035
               -> OR token equivalent:
                 ~2 tiles x 170 = 340 tokens
                 340 / 1,000,000 x $2.50 = $0.00085
                 (Use tile method per spec)

  Intermediate cost: $0.00125 + $1.035 = $1.036

Step 3: Bundle pricing
  -> No bundle defined, do not override

Step 4: Modifiers (Batch = 20% discount)
  Final cost: $1.036 x (1 - 0.20) = $1.036 x 0.80 = $0.829
```

**Result:** $0.83 (rounded)

---

## 8. Migration from v0.1.1

### 8.1 Breaking Changes

| v0.1.1 | v0.2.0 | Migration |
|--------|--------|-----------|
| Only `pricing.base` | `pricing.base` + `pricing.modalities` | Support both |
| No image/audio/video | Multimodal | Add new fields optionally |

### 8.2 Backwards Compatibility

**For Providers (text only):**
```json
{
  "pricing": {
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 10.00
    }
  }
}
```
This remains valid.

**For Providers (multimodal):**
```json
{
  "pricing": {
    "base": {
      "input_per_mtok": 2.00,
      "output_per_mtok": 10.00
    },
    "modalities": {
      "text": {
        "input_per_mtok": 2.00,
        "output_per_mtok": 10.00
      },
      "image_input": {
        "per_megapixel": 0.50
      }
    }
  }
}
```

---

## Appendix: Summary

| Modality | Input Unit | Output Unit | Backwards Compatible | Status |
|----------|------------|-------------|---------------------|--------|
| Text | $/MTok | $/MTok | Yes (base remains) | Stable |
| Image Input | $/Megapixel | — | Yes (new) | Stable |
| Image Output | — | $/Image | Yes (new) | Stable |
| Audio Input | $/Minute | — | Yes (new) | Stable |
| Audio Output | — | $/Character | Yes (new) | Stable |
| Video Input | $/Frame or $/Second | — | Yes (new) | Stable |
| Video Output | — | $/Frame or $/Second | — | Deferred to v0.3 |

---

## Changelog

### 2026-03-12 — Consistency fixes

**Fix 5: `base` vs. `modalities.text` ambiguity — consistency rule added**
- Updated Section 3.2 (Text Default) with new consistency rule
- `base` and `modalities.text` MUST have identical values when both exist
- Added validation note: validators should warn on discrepancies
- Prevents different price views for v0.1.1 vs. v0.2.0 clients
- Added corrected example

**Fix 8: `video_output` missing from JSON Schema — deferral to v0.3 documented**
- Added footnote in Section 2.1 overview table: "Video Output¹ Deferred to v0.3"
- Added rationale: "Video output pricing APIs are still too unstable for standardization"
- Added comment in Section 5 JSON Schema after `videoInputPricing`
- Updated appendix table: Video Output status as "Deferred to v0.3"
- Makes clear that Video Output is intentionally not defined

**Fix 10: Bundle Pricing without calculation path**
- Expanded Section 7.1 with new "Calculation Order (Calculation Pipeline)" subsection
- Documented strict ordering: Tiers -> Bundles -> Modifiers
- Added detailed pseudocode with bundle-check logic and tier application
- Added new `calculate_bundle_cost()` helper function in pseudocode
- Added Section 7.3: Numerical example (GPT-4o Vision + Batch modifier with concrete cost calculation)
- Bundle pricing now explicitly shows how it overrides individual modality prices

**Fix 13: Token equivalents — who calculates?**
- Added "Responsibility for Cost Calculation" section to 4.2
- Clarified: **Provider** is responsible for final cost calculation (has full visibility)
- Clarified: **Agent** can estimate costs for budget checks (estimates are informative only)
- Added note: Tile logic is provider-specific; token_equivalent fields are informative
- Best practice: Providers should document typical token counts per image size in `notes` field
- Example added: GPT-4o token counts by resolution (512x512, 1024x1024, 2048x2048)

**Consistency fixes:** Added base/modalities.text consistency rule, Video Output deferred status, bundle calculation logic, token equivalents responsibility

*End of Multimodal Pricing Specification v0.2.0*
