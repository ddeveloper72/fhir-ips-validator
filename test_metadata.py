"""
Test the updated validation with metadata and Gazelle URL
"""

import sys
from pathlib import Path
from pprint import pprint

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from test_evs_validation import validate_document

# Configuration
EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
VALIDATOR = 'HL7 - CDA Release 2'
DOCUMENT = 'examples/2-5678-W7_PS.xml'

print("=" * 80)
print("Testing Updated Validation with Metadata")
print("=" * 80)

result = validate_document(DOCUMENT, VALIDATOR, EHDS_WSDL)

if result:
    print("\n" + "=" * 80)
    print("VALIDATION METADATA")
    print("=" * 80)
    
    if result.get('metadata'):
        print("\nMetadata:")
        pprint(result['metadata'])
    
    print(f"\n🌐 Gazelle Web URL: {result.get('gazelle_web_url', 'Not available')}")
    print(f"🎯 Validator Name: {result.get('validator_name', 'Not available')}")
    
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    
    print(f"\nStatus: {result.get('status', 'Unknown')}")
    print(f"Errors: {len(result.get('errors', []))}")
    print(f"Warnings: {len(result.get('warnings', []))}")
    print(f"Info: {len(result.get('information', []))}")
    
    print("\n✅ Metadata extraction working!")
else:
    print("\n❌ Validation failed")
