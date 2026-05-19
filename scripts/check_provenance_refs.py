import json

bundle = json.load(open('examples/Diana_Ferreira_bundle_no_profile.json'))

# Get all fullUrls
full_urls = [entry['fullUrl'] for entry in bundle['entry']]

# Check Provenance references
composition_ref = 'urn:uuid:9d72d68d-0ffc-4f05-b8c3-683e74a903e9'
agent_ref = 'urn:uuid:2e76b2e9-6cc7-442d-9e79-191bc67444dd'

print(f"Composition reference exists: {composition_ref in full_urls}")
print(f"Agent reference exists: {agent_ref in full_urls}")

# Find what those entries are if they exist
for entry in bundle['entry']:
    if entry['fullUrl'] == composition_ref:
        print(f"\nComposition entry: {entry['resource']['resourceType']}")
    if entry['fullUrl'] == agent_ref:
        print(f"Agent entry: {entry['resource']['resourceType']}")
