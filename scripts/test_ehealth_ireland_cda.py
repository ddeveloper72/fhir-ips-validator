"""
Test if eHealth Ireland Gazelle supports CDA via REST API
(This is the instance that works for HL7v2)
"""

import requests
import base64
import os
from dotenv import load_dotenv
from zeep import Client

load_dotenv()

# eHealth Ireland Configuration
EHEALTH_BASE_URL = 'https://testing.ehealthireland.ie'
EHEALTH_WSDL = f'{EHEALTH_BASE_URL}/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
API_KEY = os.getenv('GAZELLE_API_KEY', '')  # Your original Gazelle key

TEST_FILE = 'examples/2-5678-W7_PS.xml'

def check_soap_validators():
    """Check if eHealth Ireland has CDA validators via SOAP"""
    print("=" * 80)
    print("Checking eHealth Ireland SOAP Validators")
    print("=" * 80)
    
    try:
        print(f"\nConnecting to: {EHEALTH_WSDL}")
        client = Client(EHEALTH_WSDL)
        validators = client.service.getListOfValidators()
        
        print(f"\n✅ Found {len(validators)} validators")
        
        # Look for CDA validators
        cda_validators = [v for v in validators if 'CDA' in v or 'cda' in v.lower()]
        epsos_validators = [v for v in validators if 'epSOS' in v or 'eHDSI' in v]
        
        print(f"\n📋 CDA-related validators: {len(cda_validators)}")
        for v in cda_validators[:10]:
            print(f"   - {v}")
        
        if epsos_validators:
            print(f"\n📋 epSOS/eHDSI validators: {len(epsos_validators)}")
            for v in epsos_validators[:5]:
                print(f"   - {v}")
        
        return validators
        
    except Exception as e:
        print(f"\n❌ Error connecting to SOAP: {e}")
        return []

def test_rest_with_hl7v2_oid():
    """Test REST API with known working HL7v2 OID"""
    print("\n" + "=" * 80)
    print("Testing REST API with Known Working HL7v2 OID")
    print("=" * 80)
    
    with open(TEST_FILE, 'rb') as f:
        xml_content = f.read()
    
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    
    # Use known working OID from HL7v2 project
    payload = {
        "objects": [{
            "originalFileName": os.path.basename(TEST_FILE),
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle HL7v2.x validator",
            "validator": "1.3.6.1.4.1.12559.11.35.10.1.12"  # ORU^R01
        }
    }
    
    rest_endpoint = f"{EHEALTH_BASE_URL}/evs/rest/validations"
    
    print(f"\nEndpoint: {rest_endpoint}")
    print(f"Validator OID: {payload['validationService']['validator']}")
    print(f"File: {os.path.basename(TEST_FILE)} (CDA document)")
    print(f"\nNote: Using HL7v2 OID with CDA document to test format...")
    
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
            print(f"✅ SUCCESS! (Payload format is correct)")
            print(f"Location: {location}")
            print("\n🎉 This confirms the payload format works!")
            print("Now we just need to find CDA validator OIDs...")
            return True
        elif response.status_code == 400:
            print(f"❌ 400 Bad Request")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text[:500]}")
        elif response.status_code == 422:
            print(f"⚠️ 422 Unprocessable Entity")
            print("This might mean the OID doesn't match the document type")
            try:
                error = response.json()
                print(f"Error: {error}")
            except:
                print(f"Response: {response.text[:500]}")
        else:
            print(f"⚠️ Status: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def try_cda_oids_on_ehealth():
    """Try various CDA OID patterns on eHealth Ireland"""
    print("\n" + "=" * 80)
    print("Testing CDA OID Patterns on eHealth Ireland")
    print("=" * 80)
    
    with open(TEST_FILE, 'rb') as f:
        xml_content = f.read()
    
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    rest_endpoint = f"{EHEALTH_BASE_URL}/evs/rest/validations"
    
    # Try different OID patterns
    oid_tests = [
        ('1.3.6.1.4.1.12559.11.1.1.1', 'Generic CDA R2'),
        ('1.3.6.1.4.1.12559.11.10.1.3.1.1.3', 'epSOS PS template OID'),
        ('1.3.6.1.4.1.19376.1.5.3.1.1.1', 'IHE PCC'),
        ('1.3.6.1.4.1.12559.11.35.1', 'Pattern variation'),
        ('1.3.6.1.4.1.12559.11.36.1', 'Pattern variation'),
        ('1.3.6.1.4.1.12559.11.40.1', 'Pattern variation'),
    ]
    
    for oid, description in oid_tests:
        print(f"\n  Testing: {oid} ({description})")
        
        payload = {
            "objects": [{
                "originalFileName": os.path.basename(TEST_FILE),
                "content": base64_content
            }],
            "validationService": {
                "name": "Gazelle CDA validator",
                "validator": oid
            }
        }
        
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
            
            if response.status_code == 201:
                location = response.headers.get('Location', '')
                print(f"    ✅ SUCCESS! Location: {location}")
                
                # Extract report URL
                oid_with_key = location.split('validations/')[-1]
                oid_parts = oid_with_key.split('?')
                result_oid = oid_parts[0]
                privacy_key = oid_parts[1].split('=')[-1] if len(oid_parts) > 1 else ''
                
                report_url = f"{EHEALTH_BASE_URL}/evs/report.seam?oid={result_oid}"
                if privacy_key:
                    report_url += f"&privacyKey={privacy_key}"
                
                print(f"    🌐 Report URL: {report_url}")
                return oid, report_url
            elif response.status_code == 400:
                print(f"    ❌ 400")
            elif response.status_code == 422:
                print(f"    ⚠️ 422 (validator/document mismatch?)")
            else:
                print(f"    ⚠️ {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:80]}")
    
    return None, None

def main():
    print("\n" + "=" * 80)
    print("🔬 INVESTIGATING EHEALTH IRELAND GAZELLE FOR CDA SUPPORT")
    print("=" * 80)
    
    if not API_KEY:
        print("\n❌ GAZELLE_API_KEY not found in .env")
        print("This is needed for eHealth Ireland instance")
        return
    
    if not os.path.exists(TEST_FILE):
        print(f"\n❌ Test file not found: {TEST_FILE}")
        return
    
    # 1. Check SOAP validators
    validators = check_soap_validators()
    
    # 2. Test REST with known working format
    format_works = test_rest_with_hl7v2_oid()
    
    # 3. Try CDA OIDs
    working_oid, report_url = try_cda_oids_on_ehealth()
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if validators:
        print(f"✅ eHealth Ireland SOAP: {len(validators)} validators available")
    else:
        print(f"❌ eHealth Ireland SOAP: No validators found or connection failed")
    
    if format_works:
        print(f"✅ REST API format: Correct (payload structure works)")
    else:
        print(f"❓ REST API format: Could not confirm")
    
    if working_oid:
        print(f"✅ CDA Validator OID: {working_oid}")
        print(f"🌐 Report URL: {report_url}")
        print("\n🎉 SUCCESS! We can use eHealth Ireland REST API for CDA!")
    else:
        print(f"❌ CDA Validator OID: Not found")
        print("\nConclusion:")
        print("- eHealth Ireland might not have CDA validators in REST API")
        print("- Or CDA validators use different OIDs not in our test list")
        print("- SOAP API remains the reliable option")

if __name__ == '__main__':
    main()
