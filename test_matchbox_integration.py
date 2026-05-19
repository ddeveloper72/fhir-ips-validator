"""Quick test of EHDS Matchbox validation with example file"""
import sys
import json
sys.path.insert(0, 'scripts')

from validate_with_matchbox import validate_fhir_with_matchbox, DEFAULT_BUNDLE_PROFILE

# Load example bundle
with open('examples/Patrick_Murphy_bundle.json', 'r', encoding='utf-8') as f:
    bundle = json.load(f)

print(f'Testing: Patrick Murphy Bundle')
print(f'Profile: {DEFAULT_BUNDLE_PROFILE}\n')

# Validate
result = validate_fhir_with_matchbox(bundle, DEFAULT_BUNDLE_PROFILE)

if result.get('success'):
    print('✅ Validation successful!')
    print(f'   Errors: {len(result["errors"])}')
    print(f'   Warnings: {len(result["warnings"])}')
    print(f'   Information: {len(result["information"])}')
    
    if result['errors']:
        print('\n❌ Errors found:')
        for i, err in enumerate(result['errors'][:3], 1):
            print(f'   {i}. {err["diagnostics"][:80]}')
    
    if result['warnings']:
        print('\n⚠️ Warnings:')
        for i, warn in enumerate(result['warnings'][:3], 1):
            print(f'   {i}. {warn["diagnostics"][:80]}')
else:
    print(f'❌ Validation failed: {result.get("error_message")}')
