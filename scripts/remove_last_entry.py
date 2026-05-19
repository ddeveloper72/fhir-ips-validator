import json
import sys

# Load the bundle
with open('examples/Diana_Ferreira_bundle_no_profile.json', 'r') as f:
    bundle = json.load(f)

print(f"Original entries: {len(bundle['entry'])}")

# Remove the last entry (entry 43 - the Provenance resource)
removed_entry = bundle['entry'].pop()
print(f"Removed entry: {removed_entry['resource']['resourceType']} (ID: {removed_entry['resource'].get('id', 'NO ID')})")
print(f"Remaining entries: {len(bundle['entry'])}")

# Save the modified bundle
output_file = 'examples/Diana_Ferreira_bundle_no_provenance.json'
with open(output_file, 'w') as f:
    json.dump(bundle, f, indent=4)

print(f"\n✅ Saved to: {output_file}")
