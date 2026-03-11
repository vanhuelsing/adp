import Ajv from 'ajv/dist/2020';
import addFormats from 'ajv-formats';

// Import schemas
import adpHeaderSchema from './schemas/adp-header.schema';
import dealRequestSchema from './schemas/deal-request.schema';
import dealOfferSchema from './schemas/deal-offer.schema';
import dealIntentSchema from './schemas/deal-intent.schema';
import dealErrorSchema from './schemas/deal-error.schema';
import pricingSchema from './schemas/pricing.schema';
import complianceSchema from './schemas/compliance.schema';

import type { DealRequest, DealOffer, DealIntent, DealError } from './types';
import type { ValidateFunction } from 'ajv';

const ajv = new Ajv({
  strict: true,
  allErrors: true
});
addFormats(ajv);

// Register schemas
ajv.addSchema(adpHeaderSchema as object, 'adp-header');
ajv.addSchema(pricingSchema as object, 'pricing');
ajv.addSchema(complianceSchema as object, 'compliance');

const validateDealRequestFn = ajv.compile(dealRequestSchema as object);
const validateDealOfferFn = ajv.compile(dealOfferSchema as object);
const validateDealIntentFn = ajv.compile(dealIntentSchema as object);
const validateDealErrorFn = ajv.compile(dealErrorSchema as object);

export interface ValidationResult {
  valid: boolean;
  errors?: string[];
}

function formatErrors(validator: ValidateFunction<unknown>): string[] {
  if (!validator.errors) return [];
  return validator.errors.map((err: { instancePath?: string; message?: string }) => {
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
