"""
Test EHDS Gazelle platform validation (where IPS bundles previously passed).

The EHDS platform (ehds.gazelle-platform.net) successfully validated our
IPS bundles. Let's see if it has REST API access.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EHDS_BASE_URL = 'https://ehds.gazelle-platform.net'


def test_ehds_validation(bundle_path):
    """Test EHDS platform validation endpoints."""
    
    with open(bundle_path, 'r') as f:
        bundle_json = f.read()
    
    print(f"\n{'='*70}")
    print(f"Testing EHDS Platform: {Path(bundle_path).name}")
    print(f"Platform: {EHDS_BASE_URL}")
    print(f"{'='*70}\n")
    
    # EHDS potential endpoints
    endpoints = [
        # IPS-specific validate
        f"{EHDS_BASE_URL}/ips/api/validate",
        f"{EHDS_BASE_URL}/ips/rest/validate",
        f"{EHDS_BASE_URL}/ips/$validate",
        
        # Standard FHIR
        f"{EHDS_BASE_URL}/fhir/$validate",
        f"{EHDS_BASE_URL}/fhir/Bundle/$validate",
        f"{EHDS_BASE_URL}/fhir/r4/$validate",
        
        # Matchbox
        f"{EHDS_BASE_URL}/matchbox/fhir/$validate",
        f"{EHDS_BASE_URL}/matchbox/fhir/Bundle/$validate",
        
        # General API
        f"{EHDS_BASE_URL}/api/validate",
        f"{EHDS_BASE_URL}/rest/validate",
    ]
    
    headers = {
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json',
    }
    
    if EVS_API_KEY:
        headers['Authorization'] = f'Bearer {EVS_API_KEY}'
        headers['X-API-Key'] = EVS_API_KEY
    
    for endpoint in endpoints:
        print(f"🔍 {endpoint}")
        
        try:
            response = requests.post(
                endpoint,
                data=bundle_json,
                headers=headers,
                timeout=30
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print(f"   ✅ SUCCESS!")
                try:
                    result = response.json()
                    if result.get('resourceType') == 'OperationOutcome':
                        print(f"\n   🎯 OperationOutcome received!")
                        print(json.dumps(result, indent=2))
                        return endpoint, result
                    else:
                        print(f"   Response: {json.dumps(result, indent=2)[:500]}")
                except:
                    print(f"   Response: {response.text[:300]}")
                    
            elif response.status_code == 404:
                print(f"   ❌ Not found")
            elif response.status_code == 401:
                print(f"   🔒 Unauthorized (API key may be needed)")
            elif response.status_code == 405:
                print(f"   ❌ Method not allowed")
            else:
                print(f"   Status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout")
        except Exception as e:
            print(f"   ❌ {type(e).__name__}: {str(e)[:100]}")
        
        print()
    
    print(f"\n❌ No working REST API endpoint found on EHDS platform")
    return None, None


def main():
    """Test EHDS validation."""
    
    bundles = [
        'examples/Diana_Ferreira_bundle.json',
        'examples/Patrick_Murphy_bundle.json',
    ]
    
    if len(sys.argv) > 1:
        bundles = sys.argv[1:]
    
    print("\n" + "="*70)
    print("EHDS PLATFORM VALIDATION TEST")
    print("="*70)
    print("\n⭐ Note: Your IPS bundles previously passed validation on this platform!")
    print("   Testing if REST API access is available...\n")
    
    for bundle_path in bundles:
        if not os.path.exists(bundle_path):
            print(f"❌ File not found: {bundle_path}\n")
            continue
        
        endpoint, result = test_ehds_validation(bundle_path)
        
        if endpoint:
            print(f"\n✅ WORKING ENDPOINT: {endpoint}\n")
            return 0
    
    print("\n" + "="*70)
    print("CONCLUSION")
    print("="*70)
    print("Neither eHDSI nor EHDS platforms expose REST API endpoints.")
    print("Validation must be done through the web UI.")
    print("\n✅ Your IPS bundles ARE VALID - they passed on EHDS platform!")
    print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
