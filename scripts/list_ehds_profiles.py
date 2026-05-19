"""List available FHIR profiles on EHDS Gazelle Matchbox"""
import requests

url = 'https://ehds.gazelle-platform.net/matchboxv3/fhir/StructureDefinition'

print('Fetching available FHIR profiles...\n')

try:
    response = requests.get(
        url,
        params={'_summary': 'true', '_count': '100'},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        total = data.get('total', 0)
        entries = data.get('entry', [])
        
        print(f'Found {total} profiles total')
        print(f'Showing first {len(entries)} profiles:\n')
        
        ips_profiles = []
        other_profiles = []
        
        for entry in entries:
            resource = entry.get('resource', {})
            profile_id = resource.get('id', 'unknown')
            profile_name = resource.get('name', '')
            profile_url = resource.get('url', '')
            
            if 'ips' in profile_name.lower() or 'ips' in profile_url.lower():
                ips_profiles.append((profile_id, profile_name, profile_url))
            else:
                other_profiles.append((profile_id, profile_name, profile_url))
        
        if ips_profiles:
            print('📋 IPS-related profiles:')
            for i, (pid, name, url) in enumerate(ips_profiles, 1):
                print(f'{i:2d}. {pid}')
                print(f'    Name: {name}')
                print(f'    URL: {url}')
                print()
        
        if other_profiles:
            print(f'\n📄 Other profiles ({len(other_profiles)} found):')
            for i, (pid, name, url) in enumerate(other_profiles[:10], 1):
                print(f'{i:2d}. {pid} - {name}')
    else:
        print(f'Error: Status {response.status_code}')
        print(response.text[:500])
        
except Exception as e:
    print(f'Error: {e}')
