"""
Test if eHDSI/EHDS Gazelle platforms have REST API endpoints
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Test endpoints
platforms = {
    'eHDSI': 'https://gazelle.ehdsi.eu',
    'EHDS': 'https://ehds.gazelle-platform.net'
}

ehdsi_api_key = os.getenv('EVS_API_KEY', '')
ehds_api_key = os.getenv('EHDS_GAZELLE_API_KEY', '')

print("=" * 80)
print("Testing Gazelle REST API Endpoints")
print("=" * 80)

for name, base_url in platforms.items():
    print(f"\n{'─'*80}")
    print(f"{name}: {base_url}")
    print(f"{'─'*80}")
    
    # Try REST API endpoint
    rest_endpoint = f"{base_url}/evs/rest/validations"
    
    print(f"\n1. Testing REST API: {rest_endpoint}")
    try:
        # Try a simple GET first
        response = requests.get(rest_endpoint, timeout=10)
        print(f"   GET response: {response.status_code}")
        if response.status_code in [200, 201, 400, 401, 403, 405]:
            print(f"   ✅ REST API endpoint exists!")
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ❌ REST API may not exist")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Try OPTIONS to see what methods are supported
    print(f"\n2. Testing OPTIONS: {rest_endpoint}")
    try:
        response = requests.options(rest_endpoint, timeout=10)
        print(f"   OPTIONS response: {response.status_code}")
        if 'Allow' in response.headers:
            print(f"   Allowed methods: {response.headers['Allow']}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    # Check if we can access API docs
    api_docs_urls = [
        f"{base_url}/evs/rest",
        f"{base_url}/api",
        f"{base_url}/evs/api",
        f"{base_url}/swagger",
        f"{base_url}/api-docs"
    ]
    
    print(f"\n3. Testing API documentation endpoints:")
    for doc_url in api_docs_urls:
        try:
            response = requests.get(doc_url, timeout=5)
            if response.status_code == 200:
                print(f"   ✅ {doc_url} - Found!")
            else:
                print(f"   ❌ {doc_url} - {response.status_code}")
        except:
            print(f"   ❌ {doc_url} - Timeout/Error")

print("\n" + "=" * 80)
print("Analysis")
print("=" * 80)
print("""
If REST API exists, we can:
1. Submit validation via POST /evs/rest/validations
2. Get Location header with validation result URL
3. Extract OID and privacy key from Location
4. Construct report URL: {base_url}/evs/report.seam?oid={oid}&privacyKey={privacyKey}

This gives us the permanent web report URL!
""")
