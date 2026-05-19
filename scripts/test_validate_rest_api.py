"""
Test Matchbox FHIR $validate operation via REST API.

Try different potential REST API endpoints for validation.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')


def test_validate_endpoints(bundle_path):
    """Test various potential $validate endpoints."""
    
    # Load bundle
    with open(bundle_path, 'r') as f:
        bundle_json = f.read()
    
    bundle_data = json.loads(bundle_json)
    
    print(f"\n{'='*70}")
    print(f"Testing $validate endpoints for: {Path(bundle_path).name}")
    print(f"{'='*70}\n")
    
    # Potential Matchbox endpoints
    endpoints = [
        # Standard FHIR $validate operation endpoints
        f"{EVS_BASE_URL}/fhir/$validate",
        f"{EVS_BASE_URL}/fhir/r4/$validate",
        f"{EVS_BASE_URL}/fhir/Bundle/$validate",
        
        # Matchbox-specific endpoints
        f"{EVS_BASE_URL}/matchbox/fhir/$validate",
        f"{EVS_BASE_URL}/matchbox/fhir/r4/$validate",
        f"{EVS_BASE_URL}/matchbox/fhir/Bundle/$validate",
        f"{EVS_BASE_URL}/matchbox/$validate",
        
        # EVS-specific endpoints
        f"{EVS_BASE_URL}/evs/fhir/$validate",
        f"{EVS_BASE_URL}/evs/fhir/r4/$validate",
        f"{EVS_BASE_URL}/evs/rest/validate",
        f"{EVS_BASE_URL}/evs/api/validate",
        
        # Try validator endpoint with REST
        f"{EVS_BASE_URL}/evs/default/api/validate",
        f"{EVS_BASE_URL}/evs/default/rest/validate",
    ]
    
    headers_json = {
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json',
    }
    
    if EVS_API_KEY:
        headers_json['Authorization'] = f'Bearer {EVS_API_KEY}'
        headers_json['X-API-Key'] = EVS_API_KEY
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        print(f"   Method: POST")
        
        # Try POST with bundle in body
        try:
            response = requests.post(
                endpoint,
                data=bundle_json,
                headers=headers_json,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS!")
                print(f"   Response preview: {response.text[:500]}")
                
                # Try to parse as JSON
                try:
                    result = response.json()
                    if result.get('resourceType') == 'OperationOutcome':
                        print(f"\n   🎯 Got OperationOutcome!")
                        print(json.dumps(result, indent=2))
                        return endpoint, result
                except:
                    pass
                
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 405:
                print(f"   ❌ Method not allowed")
            else:
                print(f"   ⚠️  Other status")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}")
    
    # Try with profile parameter
    print(f"\n\n🔍 Testing with ?profile= parameter...")
    
    profile_endpoints = [
        f"{EVS_BASE_URL}/matchbox/fhir/Bundle/$validate?profile=http://hl7.org/fhir/StructureDefinition/Bundle",
        f"{EVS_BASE_URL}/fhir/Bundle/$validate?profile=http://hl7.org/fhir/StructureDefinition/Bundle",
    ]
    
    for endpoint in profile_endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        
        try:
            response = requests.post(
                endpoint,
                data=bundle_json,
                headers=headers_json,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS!")
                try:
                    result = response.json()
                    if result.get('resourceType') == 'OperationOutcome':
                        print(f"\n   🎯 Got OperationOutcome!")
                        print(json.dumps(result, indent=2)[:1000])
                        return endpoint, result
                except:
                    pass
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}")
    
    print(f"\n\n❌ No working $validate endpoint found")
    return None, None


def main():
    """Test validation endpoints."""
    
    bundle_path = sys.argv[1] if len(sys.argv) > 1 else 'examples/Diana_Ferreira_bundle.json'
    
    if not os.path.exists(bundle_path):
        print(f"❌ File not found: {bundle_path}")
        return 1
    
    endpoint, result = test_validate_endpoints(bundle_path)
    
    if endpoint:
        print(f"\n\n{'='*70}")
        print(f"✅ WORKING ENDPOINT FOUND!")
        print(f"{'='*70}")
        print(f"Endpoint: {endpoint}")
        print(f"\nSave this endpoint for future validation!")
        print(f"{'='*70}\n")
        return 0
    else:
        print(f"\n\n{'='*70}")
        print(f"❌ NO WORKING ENDPOINT FOUND")
        print(f"{'='*70}")
        print(f"Web UI validation may be the only option.")
        print(f"Consider contacting eHDSI support for API documentation.")
        print(f"{'='*70}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
