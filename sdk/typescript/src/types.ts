export interface ADPHeader {
  version: string;
  type: 'DealRequest' | 'DealOffer' | 'DealIntent' | 'DealError';
  id: string;
  timestamp: string;
  correlation_id: string | null;
}

export interface Contact {
  email?: string;
  webhook_url?: string;
  support_url?: string;
}

export interface Requester {
  agent_id: string;
  is_automated: boolean;
  name?: string;
  contact?: Contact;
}

export interface Requirements {
  task_classes?: TaskClass[];
  min_context_window?: number;
  min_output_tokens?: number;
  modalities?: Modality[];
  capabilities?: Capability[];
  compliance?: ComplianceTag[];
  max_latency_ms?: {
    ttft?: number;
    tps?: number;
  };
}

export interface Volume {
  estimated_monthly_input_tokens?: number;
  estimated_monthly_output_tokens?: number;
  pattern?: 'steady' | 'bursty' | 'batch' | 'on_demand';
  batch_eligible?: boolean;
}

export interface Budget {
  max_cost_per_mtok_input?: number;
  max_cost_per_mtok_output?: number;
  currency: string;
  max_monthly_spend?: number;
}

export interface Preferences {
  commitment?: 'none' | 'monthly' | 'annual';
  preferred_providers?: string[];
  excluded_providers?: string[];
  deal_type?: 'pay_as_you_go' | 'commitment' | 'prepaid' | 'enterprise_custom';
}

export interface DealRequest {
  adp: ADPHeader;
  request: {
    requester: Requester;
    requirements?: Requirements;
    volume?: Volume;
    budget?: Budget;
    preferences?: Preferences;
    valid_until?: string;
    request_ttl_hours?: number;
  };
}

export interface Provider {
  provider_id: string;
  name: string;
  url?: string;
  contact?: Contact;
}

export interface Model {
  model_id: string;
  name: string;
  version?: string;
  task_classes: TaskClass[];
  context_window: number;
  max_output_tokens: number;
  modalities: Modality[];
  capabilities: Capability[];
  knowledge_cutoff?: string;
  ai_act_risk_class?: 'minimal' | 'limited' | 'high' | 'unacceptable';
  gpai_model_card_url?: string;
  prohibited_uses?: string[];
}

export interface PricingTier {
  threshold_mtok_monthly: number;
  input_per_mtok: number;
  output_per_mtok: number;
}

export interface PricingModifier {
  type: 'batch' | 'cache_read' | 'cache_write' | 'long_context' | 'fine_tuned' | 'custom';
  discount_pct?: number;
  input_per_mtok?: number;
  output_per_mtok?: number;
  threshold_tokens?: number;
  conditions?: string;
}

export interface FreeTier {
  monthly_input_tokens?: number;
  monthly_output_tokens?: number;
  rate_limit_rpm?: number;
  valid_until?: string | null;
  notes?: string;
}

export interface CommitmentDeal {
  type: 'monthly_prepaid' | 'annual_prepaid' | 'enterprise_custom';
  discount_pct: number;
  min_monthly_spend?: number;
  duration_months?: number;
  conditions?: string;
}

export interface Pricing {
  currency: string;
  base: {
    input_per_mtok: number;
    output_per_mtok: number;
  };
  tiers?: PricingTier[];
  modifiers?: PricingModifier[];
  free_tier?: FreeTier;
  commitment_deals?: CommitmentDeal[];
}

export interface Compliance {
  compliance_verified_by: 'self-declared' | 'third-party' | 'apideals-verified';
  certifications?: Certification[];
  data_regions?: string[];
  gdpr_compliant?: boolean;
  dpa_available?: boolean;
  data_retention_days?: number;
  training_on_data?: boolean;
  privacy_policy_url?: string;
  subprocessors_url?: string;
}

export interface SLA {
  uptime_pct?: number;
  ttft_p50_ms?: number;
  ttft_p99_ms?: number;
  tps_median?: number;
}

export interface DealOffer {
  adp: ADPHeader;
  offer: {
    provider: Provider;
    model: Model;
    pricing: Pricing;
    compliance: Compliance;
    sla?: SLA;
    valid_from: string;
    valid_until: string;
    terms_url?: string;
  };
}

export interface PricingSnapshot {
  input_per_mtok: number;
  output_per_mtok: number;
  modifiers_applied?: string[];
}

export interface VolumeCommitment {
  estimated_monthly_input_tokens?: number;
  estimated_monthly_output_tokens?: number;
  commitment_type?: 'none' | 'soft' | 'hard';
  commitment_duration_months?: number;
}

export interface Activation {
  type: 'redirect' | 'api_provision' | 'manual';
  redirect_url?: string;
}

export interface DealIntent {
  adp: ADPHeader;
  intent: {
    binding: false;
    requires_human_confirmation?: boolean;
    party_type?: 'business' | 'consumer';
    requester: Requester;
    accepted_offer_id: string;
    accepted_pricing_snapshot: PricingSnapshot;
    volume_commitment?: VolumeCommitment;
    activation: Activation;
    notes?: string;
  };
}

export interface FieldError {
  field: string;
  code: string;
  message: string;
}

export interface DealError {
  adp: ADPHeader;
  error: {
    code: 'INVALID_REQUEST' | 'PROVIDER_UNAVAILABLE' | 'EXPIRED' | 'VERSION_MISMATCH' | 'RATE_LIMITED' | 'NOT_FOUND';
    message: string;
    field_errors?: FieldError[];
    retryable: boolean;
    retry_after_ms?: number | null;
  };
}

export type TaskClass = 
  | 'general' 
  | 'reasoning' 
  | 'coding' 
  | 'creative' 
  | 'classification' 
  | 'extraction' 
  | 'embedding' 
  | 'multimodal';

export type Modality = 
  | 'text' 
  | 'image_input' 
  | 'image_output' 
  | 'audio_input' 
  | 'audio_output' 
  | 'video_input';

export type Capability = 
  | 'tool_use' 
  | 'structured_output' 
  | 'function_calling' 
  | 'streaming' 
  | 'batch_api' 
  | 'prompt_caching' 
  | 'fine_tuning' 
  | 'vision' 
  | 'audio_input' 
  | 'audio_output' 
  | 'web_search' 
  | 'code_execution';

export type ComplianceTag = 
  | 'gdpr' 
  | 'eu_hosting' 
  | 'eu_company' 
  | 'soc2' 
  | 'iso27001' 
  | 'hipaa' 
  | 'baa_available' 
  | 'fedramp' 
  | 'no_training' 
  | 'zero_retention' 
  | 'on_premise' 
  | 'data_residency_de' 
  | 'data_residency_eu' 
  | 'pci_dss';

export type Certification = 
  | 'soc2' 
  | 'iso27001' 
  | 'hipaa' 
  | 'fedramp';

export type ADPMessage = DealRequest | DealOffer | DealIntent | DealError;
