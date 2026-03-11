import Ajv from 'ajv';
import addFormats from 'ajv-formats';

// Import schemas
import adpHeaderSchema from '../../spec/v0.1/schemas/adp-header.schema.json';
import dealRequestSchema from '../../spec/v0.1/schemas/deal-request.schema.json';
import dealOfferSchema from '../../spec/v0.1/schemas/deal-offer.schema.json';
import dealIntentSchema from '../../spec/v0.1/schemas/deal-intent.schema.json';
import dealErrorSchema from '../../spec/v0.1/schemas/deal-error.schema.json';
import pricingSchema from '../../spec/v0.1/schemas/pricing.schema.json';
import complianceSchema from '../../spec/v0.1/schemas/compliance.schema.json';

import type { DealRequest, DealOffer, DealIntent, DealError } from './types';

const ajv = new Ajv({ 
  strict: false,
  allErrors: true 
});
addFormats(ajv);

// Register schemas
ajv.addSchema(adpHeaderSchema, 'adp-header');
ajv.addSchema(pricingSchema, 'pricing');
ajv.addSchema(complianceSchema, 'compliance');

const validateDealRequestFn = ajv.compile(dealRequestSchema);
const validateDealOfferFn = ajv.compile(dealOfferSchema);
const validateDealIntentFn = ajv.compile(dealIntentSchema);
const validateDealErrorFn = ajv.compile(dealErrorSchema);

export interface ValidationResult {
  valid: boolean;
  errors?: string[];
}

function formatErrors(validator: Ajv.ValidateFunction): string[] {
  if (!validator.errors) return [];
  return validator.errors.map(err => {
    const path = err.instancePath || 'root';
    return `${path}: ${err.message}`;
  });
}

export function validateDealRequest(data: unknown): ValidationResult {
  const valid = validateDealRequestFn(data);
  return {
    valid,
    errors: valid ? undefined : formatErrors(validateDealRequestFn)
  };
}

export function validateDealOffer(data: unknown): ValidationResult {
  const valid = validateDealOfferFn(data);
  return {
    valid,
    errors: valid ? undefined : formatErrors(validateDealOfferFn)
  };
}

export function validateDealIntent(data: unknown): ValidationResult {
  const valid = validateDealIntentFn(data);
  return {
    valid,
    errors: valid ? undefined : formatErrors(validateDealIntentFn)
  };
}

export function validateDealError(data: unknown): ValidationResult {
  const valid = validateDealErrorFn(data);
  return {
    valid,
    errors: valid ? undefined : formatErrors(validateDealErrorFn)
  };
}

export function validateADPMessage(data: unknown): ValidationResult & { type?: string } {
  if (typeof data !== 'object' || data === null) {
    return { valid: false, errors: ['Invalid: expected object'] };
  }
  
  const msg = data as { adp?: { type?: string } };
  const type = msg.adp?.type;
  
  switch (type) {
    case 'DealRequest':
      return { ...validateDealRequest(data), type };
    case 'DealOffer':
      return { ...validateDealOffer(data), type };
    case 'DealIntent':
      return { ...validateDealIntent(data), type };
    case 'DealError':
      return { ...validateDealError(data), type };
    default:
      return { 
        valid: false, 
        errors: [`Unknown message type: ${type || 'undefined'}`] 
      };
  }
}
