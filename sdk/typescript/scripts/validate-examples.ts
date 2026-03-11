import { readFileSync, readdirSync } from 'fs';
import { join } from 'path';
import Ajv from 'ajv';
import addFormats from 'ajv-formats';

const ajv = new Ajv({ strict: false });
addFormats(ajv);

const examplesDir = join(__dirname, '../../../spec/v0.1/examples');
const schemasDir = join(__dirname, '../../../spec/v0.1/schemas');

// Load schemas
const headerSchema = JSON.parse(readFileSync(join(schemasDir, 'adp-header.schema.json'), 'utf8'));
const pricingSchema = JSON.parse(readFileSync(join(schemasDir, 'pricing.schema.json'), 'utf8'));
const complianceSchema = JSON.parse(readFileSync(join(schemasDir, 'compliance.schema.json'), 'utf8'));

ajv.addSchema(headerSchema, 'adp-header');
ajv.addSchema(pricingSchema, 'pricing');
ajv.addSchema(complianceSchema, 'compliance');

const schemas: Record<string, any> = {
  'DealRequest': JSON.parse(readFileSync(join(schemasDir, 'deal-request.schema.json'), 'utf8')),
  'DealOffer': JSON.parse(readFileSync(join(schemasDir, 'deal-offer.schema.json'), 'utf8')),
  'DealIntent': JSON.parse(readFileSync(join(schemasDir, 'deal-intent.schema.json'), 'utf8')),
  'DealError': JSON.parse(readFileSync(join(schemasDir, 'deal-error.schema.json'), 'utf8')),
  'well-known-adp': JSON.parse(readFileSync(join(schemasDir, 'well-known-adp.schema.json'), 'utf8'))
};

let hasErrors = false;

const files = readdirSync(examplesDir).filter(f => f.endsWith('.json'));

console.log(`Validating ${files.length} example files...\n`);

for (const file of files) {
  const content = readFileSync(join(examplesDir, file), 'utf8');
  const data = JSON.parse(content);
  
  // Determine which schema to use
  let schemaName: string | null = null;
  
  if (file.includes('well-known')) {
    schemaName = 'well-known-adp';
  } else if (data.adp?.type && schemas[data.adp.type]) {
    schemaName = data.adp.type;
  }
  
  if (!schemaName) {
    console.log(`⚠️  ${file}: Could not determine schema`);
    continue;
  }
  
  const validate = ajv.compile(schemas[schemaName]);
  const valid = validate(data);
  
  if (valid) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file}:`);
    validate.errors?.forEach(err => {
      console.log(`   ${err.instancePath}: ${err.message}`);
    });
    hasErrors = true;
  }
}

console.log('');

if (hasErrors) {
  console.log('Validation failed!');
  process.exit(1);
} else {
  console.log('All examples validated successfully!');
  process.exit(0);
}
