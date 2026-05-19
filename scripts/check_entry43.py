import json

with open('examples/Diana_Ferreira_bundle_no_profile.json', 'r') as f:
    bundle = json.load(f)

entry43 = bundle['entry'][43]
print(f"Entry 43 fullUrl: {entry43.get('fullUrl', 'NONE')}")
print(f"Entry 43 resource type: {entry43['resource']['resourceType']}")
print(f"Entry 43 resource ID: {entry43['resource'].get('id', 'NO ID')}")
print(f"Entry 43 resource keys: {list(entry43['resource'].keys())}")
print(f"\nEntry 43 JSON length: {len(json.dumps(entry43))}")

# Check if there's an entry 44
print(f"\nTotal entries: {len(bundle['entry'])}")
if len(bundle['entry']) > 44:
    print("There IS an entry 44")
else:
    print("Entry 43 is the LAST entry")
