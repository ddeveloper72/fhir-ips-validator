"""
Test epSOS - Patient Summary Pivot validator on EHDS Gazelle
with 2-5678-W7_PS.xml
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from test_evs_validation import validate_document

# Configuration
EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
VALIDATOR = 'epSOS - Patient Summary Pivot'
DOCUMENT = 'examples/2-5678-W7_PS.xml'

print("=" * 80)
print("Testing: epSOS - Patient Summary Pivot on EHDS Gazelle")
print("=" * 80)
print(f"\nDocument: {DOCUMENT}")
print(f"Validator: {VALIDATOR}")
print(f"Platform: EHDS Gazelle (ehds.gazelle-platform.net)")
print("\nValidating...\n")

# Validate
result = validate_document(DOCUMENT, VALIDATOR, EHDS_WSDL)

if result:
    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)
    
    # Count issues
    error_count = len(result.get('errors', []))
    warning_count = len(result.get('warnings', []))
    info_count = len(result.get('information', []))
    
    print(f"\n📊 Summary:")
    print(f"   ❌ Errors: {error_count}")
    print(f"   ⚠️  Warnings: {warning_count}")
    print(f"   ℹ️  Information: {info_count}")
    
    # Status
    if error_count == 0:
        print(f"\n✅ VALIDATION PASSED")
    else:
        print(f"\n❌ VALIDATION FAILED ({error_count} errors)")
    
    # Show first few errors
    if error_count > 0:
        print(f"\n📋 First 5 Errors:")
        for i, error in enumerate(result['errors'][:5], 1):
            location = error.get('location', 'Unknown')
            message = error.get('diagnostics') or error.get('message', 'No message')
            test = error.get('test', '')
            print(f"\n   {i}. {message}")
            if test:
                print(f"      Test: {test}")
            print(f"      Location: {location}")
        
        if error_count > 5:
            print(f"\n   ... and {error_count - 5} more errors")
    
    # Show first few warnings
    if warning_count > 0:
        print(f"\n⚠️  First 3 Warnings:")
        for i, warning in enumerate(result['warnings'][:3], 1):
            location = warning.get('location', 'Unknown')
            message = warning.get('diagnostics') or warning.get('message', 'No message')
            test = warning.get('test', '')
            print(f"\n   {i}. {message}")
            if test:
                print(f"      Test: {test}")
            print(f"      Location: {location}")
    
    # Report link
    if result.get('report_url'):
        print(f"\n🔗 Full Report: {result['report_url']}")
    
    print("\n" + "=" * 80)
else:
    print("\n❌ Validation failed - no results returned")
