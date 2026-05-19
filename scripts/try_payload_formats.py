"""
Try different REST API payload formats for CDA validation
Based on trial-and-error to find the correct format
"""

import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://ehds.gazelle-platform.net'
API_KEY = os.getenv('EHDS_GAZELLE_API_KEY', '')
TEST_FILE = 'examples/2-5678-W7_PS.xml'

def test_payload_variant(variant_name, payload, description=""):
    """Test a specific payload format"""
    print(f"\n{'─'*80}")
    print(f"Variant: {variant_name}")
    if description:
        print(f"Description: {description}")
    print(f"{'─'*80}")
    
    print(f"Payload structure:")
    print(f"  Keys: {list(payload.keys())}")
    if 'objects' in payload and isinstance(payload['objects'], list) and len(payload['objects']) > 0:
        print(f"  objects[0] keys: {list(payload['objects'][0].keys())}")
    if 'validationService' in payload:
        print(f"  validationService keys: {list(payload['validationService'].keys())}")
    
    rest_endpoint = f"{BASE_URL}/evs/rest/validations"
    
    try:
        response = requests.post(
            rest_endpoint,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'GazelleAPIKey {API_KEY}'
            },
            timeout=30
        )
        
        print(f"\nResponse: {response.status_code}")
        
        if response.status_code == 201:
            location = response.headers.get('Location', '')
            print(f"✅ SUCCESS!")
            print(f"Location: {location}")
            print(f"\nAll headers:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            return True
        elif response.status_code == 400:
            print(f"❌ 400 Bad Request")
            # Try to get more details
            content_type = response.headers.get('Content-Type', '')
            print(f"Content-Type: {content_type}")
            
            if 'json' in content_type:
                try:
                    error_data = response.json()
                    print(f"Error JSON: {error_data}")
                except:
                    pass
            else:
                # Show more of the HTML response
                print(f"Response preview: {response.text[:1000]}")
        else:
            print(f"⚠️ Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def main():
    print("=" * 80)
    print("🧪 TESTING DIFFERENT REST API PAYLOAD FORMATS")
    print("=" * 80)
    
    if not os.path.exists(TEST_FILE):
        print(f"❌ Test file not found: {TEST_FILE}")
        return
    
    # Read and encode file
    with open(TEST_FILE, 'rb') as f:
        xml_content = f.read()
    
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    filename = os.path.basename(TEST_FILE)
    
    # Variant 1: Original format from HL7v2 project
    payload_1 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle CDA validator",
            "validator": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "1. HL7v2 Format",
        payload_1,
        "Same format used in HL7_v2 project with generic CDA OID"
    )
    
    # Variant 2: Without name field
    payload_2 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "validator": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "2. Without Name Field",
        payload_2,
        "Only validator OID, no name"
    )
    
    # Variant 3: Different validator OID structure
    payload_3 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "name": "HL7 - CDA Release 2",
            "validator": "HL7 - CDA Release 2"
        }
    }
    test_payload_variant(
        "3. Validator Name Instead of OID",
        payload_3,
        "Using SOAP validator name in both fields"
    )
    
    # Variant 4: Single object without array
    payload_4 = {
        "object": {
            "originalFileName": filename,
            "content": base64_content
        },
        "validationService": {
            "name": "Gazelle CDA validator",
            "validator": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "4. Single Object (not array)",
        payload_4,
        "object instead of objects array"
    )
    
    # Variant 5: Different key names
    payload_5 = {
        "files": [{
            "filename": filename,
            "content": base64_content
        }],
        "validator": {
            "name": "Gazelle CDA validator",
            "oid": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "5. Different Key Names",
        payload_5,
        "files/filename/oid instead of objects/originalFileName/validator"
    )
    
    # Variant 6: Minimal format
    payload_6 = {
        "content": base64_content,
        "validator": "1.3.6.1.4.1.12559.11.1.1.1"
    }
    test_payload_variant(
        "6. Minimal Format",
        payload_6,
        "Just content and validator OID"
    )
    
    # Variant 7: With validation type
    payload_7 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content,
            "type": "CDA"
        }],
        "validationService": {
            "name": "Gazelle CDA validator",
            "validator": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "7. With Document Type",
        payload_7,
        "Added type: CDA to object"
    )
    
    # Variant 8: With encoding specified
    payload_8 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content,
            "encoding": "base64"
        }],
        "validationService": {
            "name": "Gazelle CDA validator",
            "validator": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "8. With Encoding Field",
        payload_8,
        "Added encoding: base64"
    )
    
    # Variant 9: HL7v2 OID from working project
    payload_9 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle HL7v2.x validator",
            "validator": "1.3.6.1.4.1.12559.11.35.10.1.12"  # ORU^R01 from HL7v2
        }
    }
    test_payload_variant(
        "9. HL7v2 OID (from working project)",
        payload_9,
        "Using known working OID from HL7v2 project to test format"
    )
    
    # Variant 10: Try with validatorOid key
    payload_10 = {
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle CDA validator",
            "validatorOid": "1.3.6.1.4.1.12559.11.1.1.1"
        }
    }
    test_payload_variant(
        "10. validatorOid Key",
        payload_10,
        "Using validatorOid instead of validator"
    )
    
    print(f"\n{'='*80}")
    print("Testing Complete!")
    print(f"{'='*80}")
    print("""
If none of these work, the REST API might:
1. Not support CDA documents (only HL7v2)
2. Require different authentication
3. Be disabled for these Gazelle instances
4. Have a different endpoint path for CDA

Next steps:
- Check Gazelle documentation
- Contact Gazelle support
- Inspect network traffic from web UI
- Try the eHealth Ireland instance which we know works for HL7v2
    """)

if __name__ == '__main__':
    main()
