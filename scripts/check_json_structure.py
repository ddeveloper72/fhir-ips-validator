"""Investigate JSON validation issues in IPS bundles."""
import json
from pathlib import Path

# Check Diana Ferreira bundle
print("="*70)
print("DIANA FERREIRA BUNDLE - JSON Structure Check")
print("="*70)

try:
    with open('examples/Diana_Ferreira_bundle.json', 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    print(f"✅ JSON is valid Python JSON")
    print(f"Total entries: {len(bundle['entry'])}")
    
    if len(bundle['entry']) > 43:
        entry_43 = bundle['entry'][43]
        print(f"\nEntry [43]:")
        print(f"  Keys: {list(entry_43.keys())}")
        if 'resource' in entry_43:
            print(f"  Resource Type: {entry_43['resource'].get('resourceType', 'MISSING')}")
            print(f"  Resource ID: {entry_43['resource'].get('id', 'MISSING')}")
        if 'fullUrl' in entry_43:
            print(f"  Full URL: {entry_43['fullUrl']}")
        
        # Check for trailing commas or incomplete structures
        print(f"\n  Entry [43] JSON preview:")
        print(json.dumps(entry_43, indent=2)[:800])
        
except json.JSONDecodeError as e:
    print(f"❌ JSON Parse Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Check Patrick Murphy bundle
print("\n" + "="*70)
print("PATRICK MURPHY BUNDLE - JSON Structure Check")
print("="*70)

try:
    with open('examples/Patrick_Murphy_bundle.json', 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    print(f"✅ JSON is valid Python JSON")
    print(f"Total entries: {len(bundle['entry'])}")
    print(f"Bundle type: {bundle.get('type', 'MISSING')}")
    print(f"Bundle ID: {bundle.get('id', 'MISSING')}")
    
    # Check if Composition exists
    has_composition = any(
        e.get('resource', {}).get('resourceType') == 'Composition' 
        for e in bundle['entry']
    )
    print(f"Has Composition: {has_composition}")
    
except json.JSONDecodeError as e:
    print(f"❌ JSON Parse Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*70)
print("Note: Python's json.load() is more lenient than Azure FHIR parser")
print("Azure FHIR may reject bundles with:")
print("  • Trailing commas")
print("  • Comments")
print("  • Unescaped characters")
print("  • Incomplete JSON structures")
print("="*70)
