"""
Test EHDS Gazelle validator matching for Patient Summary
"""
from scripts.detect_cda_type import detect_cda_type
from scripts.test_evs_validation import list_available_validators

# Test with EHDS Gazelle validators
print('=== TESTING EHDS GAZELLE VALIDATOR MATCHING ===\n')

# Get EHDS validators
ehds_wsdl = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
print('Fetching available validators...')
validators = list_available_validators(ehds_wsdl)

# Load test document
print('\nLoading 2-5678-W7_PS.xml...')
with open('examples/2-5678-W7_PS.xml', 'r', encoding='utf-8') as f:
    xml_content = f.read()

# Detect with EHDS validators
print('\n' + '='*80)
print('DETECTION RESULT')
print('='*80)
result = detect_cda_type(xml_content, validators)
print(f'\n📋 Document Type:    {result["document_type"]}')
print(f'✅ Recommended:      {result["recommended_validator"]}')
print(f'🎯 Confidence:       {result["confidence"].upper()}')
print(f'💡 Match Reason:     {result["match_reason"]}')
print(f'🔖 Template IDs:     {len(result["template_ids"])} found')

if result["template_ids"]:
    print(f'\nFirst template: {result["template_ids"][0]}')

print('\n' + '='*80)
print('TEST COMPLETE')
print('='*80)
