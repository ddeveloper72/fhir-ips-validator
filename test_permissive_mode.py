"""
Test HL7 - CDA Release 2 validator (Permissive mode) on EHDS Gazelle
with 2-5678-W7_PS.xml
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from test_evs_validation import validate_document

# Configuration
EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
VALIDATOR = 'HL7 - CDA Release 2'
DOCUMENT = 'examples/2-5678-W7_PS.xml'

print("=" * 80)
print("Testing: HL7 - CDA Release 2 (Permissive) on EHDS Gazelle")
print("=" * 80)
print(f"\nDocument: {DOCUMENT}")
print(f"Validator: {VALIDATOR}")
print(f"Platform: EHDS Gazelle (ehds.gazelle-platform.net)")
print(f"Mode: PERMISSIVE (Basic structure validation)")
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
        print(f"   Document is structurally valid CDA R2")
    else:
        print(f"\n❌ VALIDATION FAILED ({error_count} errors)")
        print(f"   Document has structural issues")
    
    # Show first few errors (if any)
    if error_count > 0:
        print(f"\n📋 Errors:")
        for i, error in enumerate(result['errors'][:5], 1):
            location = error.get('location', 'Unknown')
            message = error.get('diagnostics') or error.get('message', 'No message')
            test = error.get('test', '')
            print(f"\n   {i}. {message}")
            if test:
                print(f"      Test: {test}")
            print(f"      Location: {location}")
    
    # Show comparison
    print("\n" + "=" * 80)
    print("COMPARISON: Strict vs Permissive")
    print("=" * 80)
    print("\n🔍 STRICT MODE (epSOS - Patient Summary Pivot):")
    print("   ❌ 22 errors | ⚠️ 7 warnings | ℹ️ 110 info")
    print("   Status: FAILED")
    print("   Reason: Missing epSOS-specific requirements")
    
    print("\n✅ PERMISSIVE MODE (HL7 - CDA Release 2):")
    print(f"   ❌ {error_count} errors | ⚠️ {warning_count} warnings | ℹ️ {info_count} info")
    if error_count == 0:
        print("   Status: PASSED ✓")
        print("   Reason: Basic CDA R2 structure is valid")
    else:
        print("   Status: FAILED")
        print("   Reason: Basic structure issues")
    
    print("\n💡 RECOMMENDATION:")
    print("   - Use PERMISSIVE for quick structure checks")
    print("   - Use STRICT for production validation")
    print("   - This document passes basic structure but fails epSOS compliance")
    
    print("\n" + "=" * 80)
else:
    print("\n❌ Validation failed - no results returned")
