"""
Quick test to verify EHDS Gazelle validators are accessible
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from test_evs_validation import list_available_validators

# Test EHDS Gazelle
print("=" * 80)
print("EHDS Gazelle Validator Check")
print("=" * 80)

EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'

print(f"\nConnecting to: {EHDS_WSDL}")
validators = list_available_validators(EHDS_WSDL)

print(f"\n✓ Found {len(validators)} validators\n")

# Find epSOS validators
epsos_validators = [v for v in validators if 'epSOS' in v]
print(f"epSOS validators ({len(epsos_validators)}):")
for i, v in enumerate(epsos_validators, 1):
    print(f"  {i}. {v}")

# Find Patient Summary validators
ps_validators = [v for v in validators if 'Patient Summary' in v or 'PS' in v]
print(f"\nPatient Summary validators ({len(ps_validators)}):")
for i, v in enumerate(ps_validators, 1):
    marker = "← TARGET" if v == "epSOS - Patient Summary Pivot" else ""
    print(f"  {i}. {v} {marker}")

# Find generic CDA validators
cda_validators = [v for v in validators if 'CDA Release 2' in v]
print(f"\nGeneric CDA R2 validators ({len(cda_validators)}):")
for i, v in enumerate(cda_validators, 1):
    print(f"  {i}. {v}")
