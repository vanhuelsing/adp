#!/usr/bin/env python3
"""Validate ADP JSON schemas and examples."""

import json
import glob
import re
import sys

def main():
    errors = 0
    
    # 1. JSON syntax validation
    for pattern in ['spec/*/schemas/*.json', 'spec/*/examples/*.json']:
        for f in sorted(glob.glob(pattern)):
            try:
                with open(f) as fh:
                    json.load(fh)
                print(f"✅ {f}")
            except json.JSONDecodeError as e:
                print(f"❌ {f}: {e}")
                errors += 1
    
    # 2. UUID v4 format check in examples
    uuid_v4 = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}', re.I)
    any_uuid = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)
    
    for f in sorted(glob.glob('spec/*/examples/*.json')):
        with open(f) as fh:
            text = fh.read()
        for u in any_uuid.findall(text):
            if not uuid_v4.match(u):
                print(f"❌ Bad UUID in {f}: {u}")
                errors += 1
    
    # 3. Timestamp check (ISO 8601 UTC)
    # Check fields that should be timestamps
    iso_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$')
    timestamp_fields = {'timestamp', 'valid_from', 'valid_until', 'expires_at', 'last_updated', 'reset_at'}
    
    errors_list = []
    for f in sorted(glob.glob('spec/*/examples/*.json')):
        with open(f) as fh:
            data = json.load(fh)
        check_timestamps(data, f, '', timestamp_fields, iso_pattern, errors_list)
    
    errors += len(errors_list)
    for e in errors_list:
        print(e)
    
    if errors:
        print(f"\n❌ {errors} error(s) found")
        sys.exit(1)
    else:
        print(f"\n✅ All validations passed")
        sys.exit(0)

def check_timestamps(obj, filename, path, fields, pattern, errors):
    if isinstance(obj, dict):
        for k, v in obj.items():
            current = f"{path}.{k}" if path else k
            if k in fields and isinstance(v, str):
                if not pattern.match(v):
                    errors.append(f"❌ Bad timestamp in {filename} at {current}: {v}")
            check_timestamps(v, filename, current, fields, pattern, errors)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            check_timestamps(v, filename, f"{path}[{i}]", fields, pattern, errors)

if __name__ == '__main__':
    main()
