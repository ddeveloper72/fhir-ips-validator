import json

# Load the bundle and extract the problematic Provenance resource
with open('examples/Diana_Ferreira_bundle_no_profile.json', 'r') as f:
    bundle = json.load(f)

provenance = bundle['entry'][43]['resource']

print("Provenance Resource Structure:")
print(json.dumps(provenance, indent=2))

# Check required elements for Provenance according to FHIR R4
print("\n=== FHIR R4 Provenance Required Elements ===")
print(f"✓ resourceType: {provenance.get('resourceType', 'MISSING')}")
print(f"✓ target: {provenance.get('target', 'MISSING')}")
print(f"✓ recorded: {provenance.get('recorded', 'MISSING')}")
print(f"✓ agent: {provenance.get('agent', 'MISSING')}")

# Check agent structure
if 'agent' in provenance and provenance['agent']:
    agent = provenance['agent'][0]
    print(f"\n=== Agent Structure ===")
    print(f"  who: {agent.get('who', 'MISSING')}")
    if 'who' in agent and 'reference' in agent['who']:
        print(f"    reference: {agent['who']['reference']}")
