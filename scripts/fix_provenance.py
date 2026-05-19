import json

# Load original bundle
with open('examples/Diana_Ferreira_bundle_no_profile.json', 'r') as f:
    bundle = json.load(f)

# Get the problematic Provenance
old_provenance_entry = bundle['entry'][43]

# Recreate the Provenance entry from scratch with the same data
new_provenance_entry = {
    "fullUrl": old_provenance_entry['fullUrl'],
    "resource": {
        "resourceType": "Provenance",
        "id": old_provenance_entry['resource']['id'],
        "target": old_provenance_entry['resource']['target'],
        "recorded": old_provenance_entry['resource']['recorded'],
        "activity": old_provenance_entry['resource']['activity'],
        "agent": old_provenance_entry['resource']['agent']
    }
}

# Replace the entry
bundle['entry'][43] = new_provenance_entry

# Save
output_file = 'examples/Diana_Ferreira_bundle_fixed.json'
with open(output_file, 'w') as f:
    json.dump(bundle, f, indent=4, ensure_ascii=False)

print(f"✅ Created {output_file} with recreated Provenance resource")
