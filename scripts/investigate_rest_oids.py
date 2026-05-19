"""
Investigate REST API OIDs for CDA Validators
Goal: Map SOAP validator names to REST API OIDs
"""

import requests
import base64
import os
import json
from zeep import Client
from zeep.exceptions import Fault
from dotenv import load_dotenv

load_dotenv()

# Configuration
PLATFORMS = {
    'eHDSI': {
        'base_url': 'https://gazelle.ehdsi.eu',
        'wsdl': 'https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        'api_key': os.getenv('EVS_API_KEY', '')
    },
    'EHDS': {
        'base_url': 'https://ehds.gazelle-platform.net',
        'wsdl': 'https://ehds.gazelle-platform.net/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        'api_key': os.getenv('EHDS_GAZELLE_API_KEY', '')
    }
}

def get_soap_validators(wsdl_url):
    """Get validator list from SOAP API"""
    print(f"\n📋 Getting validators from SOAP: {wsdl_url}")
    try:
        client = Client(wsdl_url)
        validators = client.service.getListOfValidators()
        return validators
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def explore_rest_endpoints(base_url, api_key):
    """Explore REST API endpoints to find validator information"""
    print(f"\n🔍 Exploring REST endpoints: {base_url}")
    
    endpoints_to_try = [
        '/evs/rest/validators',
        '/evs/rest/validationServices',
        '/evs/rest/services',
        '/evs/rest/standards',
        '/evs/rest/configurations',
        '/CDAGenerator-ejb/rest/validators',
        '/api/validators',
        '/rest/validators'
    ]
    
    results = {}
    
    for endpoint in endpoints_to_try:
        url = f"{base_url}{endpoint}"
        print(f"\n  Testing: {endpoint}")
        
        # Try with and without authentication
        for use_auth in [True, False]:
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            if use_auth:
                headers['Authorization'] = f'GazelleAPIKey {api_key}'
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                auth_str = "with auth" if use_auth else "no auth"
                
                if response.status_code == 200:
                    print(f"    ✅ {response.status_code} ({auth_str})")
                    try:
                        data = response.json()
                        results[endpoint] = data
                        print(f"    📄 Got JSON data ({len(str(data))} chars)")
                        # Print first few items
                        if isinstance(data, list) and len(data) > 0:
                            print(f"    First item: {json.dumps(data[0], indent=2)[:200]}")
                        elif isinstance(data, dict):
                            print(f"    Keys: {list(data.keys())}")
                    except:
                        print(f"    📄 Got response ({len(response.text)} bytes)")
                        print(f"    Preview: {response.text[:200]}")
                    break  # Found working endpoint
                elif response.status_code in [401, 403]:
                    if use_auth:
                        print(f"    ⚠️ {response.status_code} even with auth")
                elif response.status_code == 404:
                    if use_auth:
                        print(f"    ❌ 404")
                        break  # No point trying without auth
                elif response.status_code == 405:
                    print(f"    ⚠️ 405 - Method not allowed (GET)")
                    break
                else:
                    print(f"    ⚠️ {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"    ⏱️ Timeout")
                break
            except Exception as e:
                print(f"    ❌ Error: {str(e)[:100]}")
                break
    
    return results

def try_rest_submission_with_name(base_url, api_key, file_path, validator_name):
    """Try REST submission using validator name instead of OID"""
    print(f"\n🧪 Testing REST with validator NAME")
    print(f"   Validator: {validator_name}")
    
    with open(file_path, 'rb') as f:
        xml_content = f.read()
    
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    
    # Try payload with name instead of OID
    payload = {
        "objects": [{
            "originalFileName": os.path.basename(file_path),
            "content": base64_content
        }],
        "validationService": {
            "name": validator_name,
            "validator": validator_name  # Try name in validator field
        }
    }
    
    rest_endpoint = f"{base_url}/evs/rest/validations"
    
    try:
        response = requests.post(
            rest_endpoint,
            json=payload,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'GazelleAPIKey {api_key}'
            },
            timeout=30
        )
        
        print(f"   Response: {response.status_code}")
        
        if response.status_code == 201:
            location = response.headers.get('Location', '')
            print(f"   ✅ SUCCESS! Location: {location}")
            return location
        elif response.status_code == 400:
            print(f"   ❌ Bad Request")
            # Try to parse error message
            try:
                error_data = response.json()
                print(f"   Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   Response: {response.text[:500]}")
        else:
            print(f"   Response: {response.text[:500]}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return None

def try_common_oid_patterns(base_url, api_key, file_path):
    """Try common OID patterns for CDA validators"""
    print(f"\n🔬 Testing common OID patterns")
    
    with open(file_path, 'rb') as f:
        xml_content = f.read()
    
    base64_content = base64.b64encode(xml_content).decode('utf-8')
    
    # Common OID patterns based on HL7v2 structure
    oid_patterns = [
        # Generic CDA validators
        '1.3.6.1.4.1.12559.11.1.1.1',  # Generic CDA R2
        '1.3.6.1.4.1.12559.11.1.2.1',  # CDA variant
        
        # epSOS patterns (based on eHDSI standards)
        '1.3.6.1.4.1.12559.11.10.1.3.1.1.3',  # epSOS PS
        '1.3.6.1.4.1.19376.1.5.3.1.1.1',  # IHE PCC
        
        # Try sequential numbers
        '1.3.6.1.4.1.12559.11.1.1.2',
        '1.3.6.1.4.1.12559.11.1.1.3',
        '1.3.6.1.4.1.12559.11.1.1.4',
        '1.3.6.1.4.1.12559.11.1.1.5',
    ]
    
    rest_endpoint = f"{base_url}/evs/rest/validations"
    
    for oid in oid_patterns:
        print(f"\n  Testing OID: {oid}")
        
        payload = {
            "objects": [{
                "originalFileName": os.path.basename(file_path),
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
                    'Authorization': f'GazelleAPIKey {api_key}'
                },
                timeout=30
            )
            
            if response.status_code == 201:
                location = response.headers.get('Location', '')
                print(f"    ✅ SUCCESS! Location: {location}")
                return oid, location
            elif response.status_code == 400:
                print(f"    ❌ 400 Bad Request")
            elif response.status_code == 404:
                print(f"    ❌ 404 Not Found")
            else:
                print(f"    ⚠️ {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
    
    return None, None

def analyze_validator_names(validators):
    """Analyze validator names to find patterns"""
    print(f"\n📊 Analyzing {len(validators)} validator names:")
    
    patterns = {}
    for validator in validators:
        # Look for common keywords
        keywords = ['Wave', 'epSOS', 'CDA', 'PIVOT', 'FRIENDLY', 'Patient Summary', 'PS']
        found_keywords = [kw for kw in keywords if kw in validator]
        
        if found_keywords:
            pattern_key = ', '.join(found_keywords)
            if pattern_key not in patterns:
                patterns[pattern_key] = []
            patterns[pattern_key].append(validator)
    
    for pattern, validators_list in patterns.items():
        print(f"\n  Pattern: {pattern}")
        for v in validators_list[:3]:  # Show first 3
            print(f"    - {v}")
        if len(validators_list) > 3:
            print(f"    ... and {len(validators_list) - 3} more")

def main():
    print("=" * 80)
    print("🔬 INVESTIGATING REST API OIDS FOR CDA VALIDATORS")
    print("=" * 80)
    
    test_file = 'examples/2-5678-W7_PS.xml'
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    # Test each platform
    for platform_name, config in PLATFORMS.items():
        print(f"\n{'='*80}")
        print(f"Platform: {platform_name}")
        print(f"{'='*80}")
        
        if not config['api_key']:
            print(f"⚠️ No API key found for {platform_name}")
            continue
        
        # 1. Get SOAP validators
        validators = get_soap_validators(config['wsdl'])
        if validators:
            print(f"\n✅ Found {len(validators)} validators via SOAP")
            print(f"   First 5:")
            for v in validators[:5]:
                print(f"   - {v}")
            
            # Analyze patterns
            analyze_validator_names(validators)
        
        # 2. Explore REST endpoints
        print(f"\n{'─'*80}")
        print("Exploring REST Endpoints")
        print(f"{'─'*80}")
        rest_results = explore_rest_endpoints(config['base_url'], config['api_key'])
        
        if rest_results:
            print(f"\n✅ Found {len(rest_results)} working REST endpoints!")
            for endpoint, data in rest_results.items():
                print(f"\n  {endpoint}:")
                print(f"    Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"    Count: {len(data)}")
                elif isinstance(data, dict):
                    print(f"    Keys: {list(data.keys())}")
        
        # 3. Try REST submission with validator name
        if validators:
            print(f"\n{'─'*80}")
            print("Testing REST API with Validator Names")
            print(f"{'─'*80}")
            
            # Try with first CDA Release 2 validator
            cda_r2_validators = [v for v in validators if 'CDA Release 2' in v or 'CDA R2' in v]
            if cda_r2_validators:
                location = try_rest_submission_with_name(
                    config['base_url'],
                    config['api_key'],
                    test_file,
                    cda_r2_validators[0]
                )
        
        # 4. Try common OID patterns
        print(f"\n{'─'*80}")
        print("Testing Common OID Patterns")
        print(f"{'─'*80}")
        
        working_oid, location = try_common_oid_patterns(
            config['base_url'],
            config['api_key'],
            test_file
        )
        
        if working_oid:
            print(f"\n{'='*80}")
            print(f"🎉 FOUND WORKING OID: {working_oid}")
            print(f"Location: {location}")
            print(f"{'='*80}")
            
            # Parse location to get report URL
            if location:
                oid_with_key = location.split('validations/')[-1]
                oid_parts = oid_with_key.split('?')
                oid = oid_parts[0]
                privacy_key = oid_parts[1].split('=')[-1] if len(oid_parts) > 1 else ''
                
                report_url = f"{config['base_url']}/evs/report.seam?oid={oid}"
                if privacy_key:
                    report_url += f"&privacyKey={privacy_key}"
                
                print(f"\n🌐 Report URL: {report_url}")
    
    print(f"\n{'='*80}")
    print("Investigation Complete!")
    print(f"{'='*80}")

if __name__ == '__main__':
    main()
