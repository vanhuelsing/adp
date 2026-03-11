import { describe, it, expect } from 'vitest';
import { 
  validateDealRequest, 
  validateDealOffer, 
  validateDealIntent, 
  validateDealError,
  validateADPMessage 
} from '../src/validator';
import type { DealRequest, DealOffer, DealIntent, DealError } from '../src/types';

describe('ADP Validator', () => {
  describe('DealRequest', () => {
    it('validates a correct DealRequest', () => {
      const request: DealRequest = {
        adp: {
          version: '0.1.1',
          type: 'DealRequest',
          id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
          timestamp: '2026-03-10T12:00:00Z',
          correlation_id: null
        },
        request: {
          requester: {
            agent_id: 'agent:test:bot',
            is_automated: true
          }
        }
      };
      
      const result = validateDealRequest(request);
      expect(result.valid).toBe(true);
      expect(result.errors).toBeUndefined();
    });

    it('rejects invalid UUID', () => {
      const request = {
        adp: {
          version: '0.1.1',
          type: 'DealRequest',
          id: 'not-a-uuid',
          timestamp: '2026-03-10T12:00:00Z',
          correlation_id: null
        },
        request: {
          requester: {
            agent_id: 'agent:test:bot',
            is_automated: true
          }
        }
      };
      
      const result = validateDealRequest(request);
      expect(result.valid).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('rejects non-UTC timestamp', () => {
      const request = {
        adp: {
          version: '0.1.1',
          type: 'DealRequest',
          id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
          timestamp: '2026-03-10T12:00:00+02:00',
          correlation_id: null
        },
        request: {
          requester: {
            agent_id: 'agent:test:bot',
            is_automated: true
          }
        }
      };
      
      const result = validateDealRequest(request);
      expect(result.valid).toBe(false);
    });
  });

  describe('DealOffer', () => {
    it('validates a correct DealOffer', () => {
      const offer: DealOffer = {
        adp: {
          version: '0.1.1',
          type: 'DealOffer',
          id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
          timestamp: '2026-03-10T12:00:00Z',
          correlation_id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        },
        offer: {
          provider: {
            provider_id: 'test-provider',
            name: 'Test Provider'
          },
          model: {
            model_id: 'test-model',
            name: 'Test Model',
            task_classes: ['reasoning'],
            context_window: 100000,
            max_output_tokens: 4096,
            modalities: ['text'],
            capabilities: []
          },
          pricing: {
            currency: 'USD',
            base: {
              input_per_mtok: 1.0,
              output_per_mtok: 2.0
            }
          },
          compliance: {
            compliance_verified_by: 'self-declared'
          },
          valid_from: '2026-03-10T00:00:00Z',
          valid_until: '2026-04-10T00:00:00Z'
        }
      };
      
      const result = validateDealOffer(offer);
      expect(result.valid).toBe(true);
    });
  });

  describe('DealIntent', () => {
    it('validates a correct DealIntent', () => {
      const intent: DealIntent = {
        adp: {
          version: '0.1.1',
          type: 'DealIntent',
          id: '550e8400-e29b-41d4-a716-446655440000',
          timestamp: '2026-03-10T12:00:00Z',
          correlation_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7'
        },
        intent: {
          binding: false,
          requester: {
            agent_id: 'agent:test:bot',
            is_automated: true
          },
          accepted_offer_id: '7c9e6679-7425-40de-944b-e07fc1f90ae7',
          accepted_pricing_snapshot: {
            input_per_mtok: 1.0,
            output_per_mtok: 2.0
          },
          activation: {
            type: 'redirect',
            redirect_url: 'https://example.com/signup'
          }
        }
      };
      
      const result = validateDealIntent(intent);
      expect(result.valid).toBe(true);
    });
  });

  describe('DealError', () => {
    it('validates a correct DealError', () => {
      const error: DealError = {
        adp: {
          version: '0.1.1',
          type: 'DealError',
          id: '6ba7b810-9dad-41d1-80b4-00c04fd430c8',
          timestamp: '2026-03-10T12:00:00Z',
          correlation_id: 'f47ac10b-58cc-4372-a567-0e02b2c3d479'
        },
        error: {
          code: 'INVALID_REQUEST',
          message: 'Invalid request',
          retryable: false
        }
      };
      
      const result = validateDealError(error);
      expect(result.valid).toBe(true);
    });
  });

  describe('validateADPMessage', () => {
    it('auto-detects DealRequest', () => {
      const msg = { adp: { type: 'DealRequest' } };
      const result = validateADPMessage(msg);
      expect(result.type).toBe('DealRequest');
    });

    it('auto-detects DealOffer', () => {
      const msg = { adp: { type: 'DealOffer' } };
      const result = validateADPMessage(msg);
      expect(result.type).toBe('DealOffer');
    });

    it('rejects unknown type', () => {
      const msg = { adp: { type: 'UnknownType' } };
      const result = validateADPMessage(msg);
      expect(result.valid).toBe(false);
    });
  });
});
