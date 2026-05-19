"""Test FHIR validation on EHDS Gazelle Matchbox"""
import requests
import json

# Test with a minimal FHIR bundle
test_bundle = {
    'resourceType': 'Bundle',
    'type': 'document',
    'entry': [
        {
            'resource': {
                'resourceType': 'Patient',
                'id': 'test',
                'name': [{'family': 'Test', 'given': ['Test']}]
            }
        }
    ]
}

# Try different validation endpoints
urls_to_test = [
    'https://ehds.gazelle-platform.net/matchboxv3/fhir/Bundle/$validate',
    'https://ehds.gazelle-platform.net/matchboxv3/fhir/$validate',
    'https://ehds.gazelle-platform.net/matchboxv3/fhir',
]

for url in urls_to_test:
    print(f'Testing: {url}')
    print('-' * 80)
    
    try:
        # Try POST for $validate, GET for metadata
        if '$validate' in url:
            response = requests.post(
                url,
                json=test_bundle,
                headers={'Content-Type': 'application/fhir+json'},
                timeout=30
            )
        else:
            # Try as a create operation
            response = requests.post(
                url,
                json=test_bundle,
                headers={'Content-Type': 'application/fhir+json'},
                params={'_format': 'json'},
                timeout=30
            )
        
        print(f'Status: {response.status_code}')
        
        if response.status_code in [200, 201]:
            result = response.json()
            print(f'✅ SUCCESS! ResourceType: {result.get("resourceType")}')
            if result.get('issue'):
                print(f'Issues: {len(result["issue"])}')
                for i, issue in enumerate(result['issue'][:2], 1):
                    severity = issue.get('severity', 'unknown')
                    diagnostics = issue.get('diagnostics', 'No message')
                    print(f'  {i}. [{severity}] {diagnostics[:80]}')
        else:
            result = response.json() if response.headers.get('content-type', '').startswith('application') else None
            if result and result.get('issue'):
                diagnostics = result['issue'][0].get('diagnostics', 'Unknown error')
                print(f'❌ {diagnostics[:100]}')
            else:
                print(f'❌ {response.text[:150]}')
    except Exception as e:
        print(f'❌ Error: {e}')
    
    print()
