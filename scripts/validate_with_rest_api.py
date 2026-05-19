"""
Gazelle EVS REST API Validator
Submits documents via REST API to get permanent report URLs
"""

import requests
import base64
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def submit_document_rest(file_path, validator_oid, base_url, api_key):
    """
    Submit document via REST API and get report URL
    
    Args:
        file_path: Path to XML document
        validator_oid: OID of validator (e.g., from list_available_validators)
        base_url: Base URL (e.g., 'https://gazelle.ehdsi.eu')
        api_key: API key for authentication
    
    Returns:
        dict with validation results including report_url
    """
    print(f"\n{'='*80}")
    print(f"Submitting via REST API")
    print(f"{'='*80}")
    print(f"File: {os.path.basename(file_path)}")
    print(f"Validator OID: {validator_oid}")
    print(f"Platform: {base_url}")
    
    # Read file
    with open(file_path, 'rb') as f:
        xml_content = f.read()
    
    # Encode to base64
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    
    # Prepare payload (based on HL7_v2 project structure)
    payload = {
        "objects": [{
            "originalFileName": os.path.basename(file_path),
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle CDA validator",
            "validator": validator_oid
        }
    }
    
    # Submit validation
    rest_endpoint = f"{base_url}/evs/rest/validations"
    
    print(f"\n⏳ Submitting to {rest_endpoint}...")
    
    try:
        response = requests.post(
            rest_endpoint,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'GazelleAPIKey {api_key}'
            },
            timeout=30,
            verify=True
        )
        
        print(f"Response: {response.status_code}")
        
        if response.status_code == 201:
            # Success! Extract location from header
            location = response.headers.get('Location', '')
            print(f"✅ Validation submitted successfully!")
            print(f"Location: {location}")
            
            # Parse location to get OID and construct report URL
            if location:
                # Extract OID and privacy key from location
                # Format: /evs/rest/validations/{oid}?privacyKey={key}
                oid_with_key = location.split('validations/')[-1]
                oid_parts = oid_with_key.split('?')
                oid = oid_parts[0]
                privacy_key = oid_parts[1].split('=')[-1] if len(oid_parts) > 1 else ''
                
                # Construct web report URL
                report_url = f"{base_url}/evs/report.seam?oid={oid}"
                if privacy_key:
                    report_url += f"&privacyKey={privacy_key}"
                
                print(f"\n🌐 Report URL: {report_url}")
                
                return {
                    'status': 'success',
                    'location': location,
                    'oid': oid,
                    'privacy_key': privacy_key,
                    'report_url': report_url,
                    'file': file_path,
                    'validator_oid': validator_oid,
                    'platform': base_url
                }
            else:
                print("⚠️ No Location header returned")
                return {
                    'status': 'success_no_location',
                    'file': file_path
                }
        
        elif response.status_code == 401:
            print(f"❌ Authentication failed - check API key")
            return {
                'status': 'auth_failed',
                'error': 'Invalid API key'
            }
        
        elif response.status_code == 400:
            print(f"❌ Bad request")
            print(f"Response: {response.text[:500]}")
            return {
                'status': 'bad_request',
                'error': response.text
            }
        
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return {
                'status': 'error',
                'http_status': response.status_code,
                'error': response.text
            }
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {
            'status': 'exception',
            'error': str(e)
        }


def test_rest_submission():
    """Test REST API submission"""
    # Test with EHDS Gazelle
    base_url = 'https://ehds.gazelle-platform.net'
    api_key = os.getenv('EHDS_GAZELLE_API_KEY', '')
    file_path = 'examples/2-5678-W7_PS.xml'
    
    # We need a validator OID - let's use a CDA validator OID
    # Note: We need to find the correct OID from the validator list
    # For now, we'll try a generic one
    validator_oid = '1.3.6.1.4.1.12559.11.1.1.1'  # Generic CDA validator OID (may need to adjust)
    
    if not api_key:
        print("❌ EHDS_GAZELLE_API_KEY not found in .env")
        return
    
    result = submit_document_rest(file_path, validator_oid, base_url, api_key)
    
    if result['status'] == 'success':
        print(f"\n{'='*80}")
        print("SUCCESS!")
        print(f"{'='*80}")
        print(f"\n🌐 Report URL: {result['report_url']}")
        print(f"📋 OID: {result['oid']}")
        print(f"🔑 Privacy Key: {result.get('privacy_key', 'None')}")
    else:
        print(f"\n{'='*80}")
        print(f"Status: {result['status']}")
        if 'error' in result:
            print(f"Error: {result['error'][:500]}")


if __name__ == '__main__':
    test_rest_submission()
