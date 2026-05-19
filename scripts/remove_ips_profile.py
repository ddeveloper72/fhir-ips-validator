"""
Remove IPS profile declarations from FHIR bundles for Azure FHIR validation.
Azure FHIR doesn't have IPS IG installed, so we validate as generic R4 bundles.
"""

import json
import sys
from pathlib import Path

def remove_ips_profiles(bundle_data):
    """Remove IPS profile references from bundle and all resources."""
    # Remove Bundle-level profile
    if 'meta' in bundle_data and 'profile' in bundle_data['meta']:
        bundle_data['meta']['profile'] = [
            p for p in bundle_data['meta']['profile'] 
            if 'uv/ips' not in p
        ]
        if not bundle_data['meta']['profile']:
            del bundle_data['meta']['profile']
        if not bundle_data['meta']:
            del bundle_data['meta']
    
    # Remove profiles from all entries
    if 'entry' in bundle_data:
        for entry in bundle_data['entry']:
            if 'resource' in entry:
                resource = entry['resource']
                if 'meta' in resource and 'profile' in resource['meta']:
                    resource['meta']['profile'] = [
                        p for p in resource['meta']['profile']
                        if 'uv/ips' not in p
                    ]
                    if not resource['meta']['profile']:
                        del resource['meta']['profile']
                    if not resource['meta']:
                        del resource['meta']
    
    return bundle_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python remove_ips_profile.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else input_file.parent / f"{input_file.stem}_no_profile.json"
    
    print(f"📖 Reading: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        bundle = json.load(f)
    
    print(f"🔧 Removing IPS profile references...")
    bundle = remove_ips_profiles(bundle)
    
    print(f"💾 Writing: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bundle, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Done! Created: {output_file}")

if __name__ == "__main__":
    main()
