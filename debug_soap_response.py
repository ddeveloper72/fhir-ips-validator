"""
Debug script to inspect full SOAP response from Gazelle
"""

import sys
import base64
from pathlib import Path
from zeep import Client
from pprint import pprint

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# Configuration
EHDS_WSDL = 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
VALIDATOR = 'HL7 - CDA Release 2'
DOCUMENT = 'examples/2-5678-W7_PS.xml'

print("=" * 80)
print("Inspecting Gazelle SOAP Response")
print("=" * 80)
print(f"\nDocument: {DOCUMENT}")
print(f"Validator: {VALIDATOR}")
print(f"Platform: EHDS Gazelle")

# Read document
with open(DOCUMENT, 'rb') as f:
    xml_content = f.read()

# Create SOAP client
client = Client(EHDS_WSDL)

# Encode to base64
base64_content = base64.b64encode(xml_content).decode('utf-8')

print("\n⏳ Submitting validation request...")

# Call validation service
result = client.service.validateBase64Document(
    base64Document=base64_content,
    validator=VALIDATOR
)

print("✓ Validation completed\n")

print("=" * 80)
print("FULL SOAP RESPONSE OBJECT")
print("=" * 80)

print(f"\nType: {type(result)}")
print(f"\nDir: {dir(result)}")

if hasattr(result, '__dict__'):
    print(f"\n__dict__:")
    pprint(result.__dict__)

if hasattr(result, '__values__'):
    print(f"\n__values__:")
    pprint(result.__values__)

print("\n" + "=" * 80)
print("RESPONSE ATTRIBUTES")
print("=" * 80)

# Check common attributes
common_attrs = ['text', 'reportOid', 'reportURL', 'oid', 'url', 'link', 'report', 'detailedResult', 'status']

for attr in common_attrs:
    if hasattr(result, attr):
        value = getattr(result, attr)
        print(f"\n✓ {attr}: {value[:200] if isinstance(value, str) and len(value) > 200 else value}")
    else:
        print(f"  {attr}: NOT FOUND")

print("\n" + "=" * 80)
print("ZEEP SERIALIZATION")
print("=" * 80)

# Try to serialize using zeep helpers
try:
    from zeep.helpers import serialize_object
    serialized = serialize_object(result)
    print("\nSerialized object:")
    pprint(serialized)
except Exception as e:
    print(f"\n✗ Could not serialize: {e}")

print("\n" + "=" * 80)
