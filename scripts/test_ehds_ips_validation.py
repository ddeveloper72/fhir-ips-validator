"""Test FHIR IPS validation on EHDS Gazelle Matchbox with profile parameter"""
import requests
import json
import sys

# Read example FHIR bundle
example_file = 'examples/Patrick_Murphy_bundle.json'
print(f'Loading: {example_file}\n')

with open(example_file, 'r', encoding='utf-8') as f:
    bundle = json.load(f)

# EHDS Gazelle Matchbox with IPS Bundle profile
url = 'https://ehds.gazelle-platform.net/matchboxv3/fhir/$validate'
profile = 'http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips'

print(f'Validating against: {profile}\n')

try:
    response = requests.post(
        url,
        params={'profile': profile},
        json=bundle,
        headers={'Content-Type': 'application/fhir+json'},
        timeout=60
    )
    
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('resourceType') == 'OperationOutcome':
            issues = result.get('issue', [])
            print(f'\n✅ Validation completed - {len(issues)} issues found:\n')
            
            # Count by severity
            errors = [i for i in issues if i.get('severity') == 'error']
            warnings = [i for i in issues if i.get('severity') == 'warning']
            info = [i for i in issues if i.get('severity') == 'information']
            
            print(f'  Errors: {len(errors)}')
            print(f'  Warnings: {len(warnings)}')
            print(f'  Information: {len(info)}')
            
            # Show first few issues
            print('\nFirst 5 issues:')
            for i, issue in enumerate(issues[:5], 1):
                severity = issue.get('severity', 'unknown')
                code = issue.get('code', 'unknown')
                diagnostics = issue.get('diagnostics', 'No message')
                location = issue.get('location', [''])[0] if issue.get('location') else ''
                
                print(f'\n{i}. [{severity.upper()}] {code}')
                print(f'   {diagnostics[:200]}')
                if location:
                    print(f'   Location: {location}')
    else:
        result = response.json() if 'application/json' in response.headers.get('content-type', '') else None
        if result and result.get('issue'):
            print(f'❌ Error: {result["issue"][0].get("diagnostics", "Unknown error")}')
        else:
            print(f'❌ {response.text[:200]}')
            
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
