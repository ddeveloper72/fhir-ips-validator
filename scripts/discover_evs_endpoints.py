"""
eHDSI Gazelle EVS API Endpoint Discovery Script

This script discovers and tests the EVS validation service endpoints on the
eHDSI Gazelle platform (https://gazelle.ehdsi.eu).

Based on the documentation at:
https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html

The EVS services use SOAP web services with WSDL endpoints.

Known validation services from EVS Client:
- Assertions (SAML)
- Audit Messages (ATNA)
- CDA content validation
- Certificates
- HL7V3 messages
- PDF validation
- XD* metadata validation (XDS/XDR/XCA)

Web Service API Methods:
- about(): Get information about the web service
- getListOfValidators(discriminator): Get list of validators
- validateDocument(document, validator): Validate XML document
- validateBase64Document(base64Document, validator): Validate base64 encoded document
"""

import os
import sys
import requests
from zeep import Client
from zeep.exceptions import Fault, TransportError
from dotenv import load_dotenv
from datetime import datetime
import json

# Load environment variables
load_dotenv()
EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')

print(f"""
{'='*80}
eHDSI Gazelle EVS API Endpoint Discovery
{'='*80}
Base URL: {EVS_BASE_URL}
API Key: {'✓ Loaded' if EVS_API_KEY else '✗ Missing'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
""")

# Potential WSDL endpoints based on IHE patterns and eHDSI services
POTENTIAL_WSDL_ENDPOINTS = [
    # CDA Validation (Primary for FHIR → CDA validation)
    f"{EVS_BASE_URL}/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    f"{EVS_BASE_URL}/evs/cda/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    f"{EVS_BASE_URL}/gazelle-cda-validator/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    
    # ATNA Audit Messages
    f"{EVS_BASE_URL}/gazelle-atna-ejb/AuditMessageValidationWSService/AuditMessageValidationWS?wsdl",
    f"{EVS_BASE_URL}/evs/atna/AuditMessageValidationWSService/AuditMessageValidationWS?wsdl",
    
    # XDS/XDR/XCA Metadata
    f"{EVS_BASE_URL}/XDStarClient-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    f"{EVS_BASE_URL}/evs/xds/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    
    # HL7v3 Messages
    f"{EVS_BASE_URL}/GazelleHL7v3Validator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    f"{EVS_BASE_URL}/evs/hl7v3/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    
    # SAML Assertions
    f"{EVS_BASE_URL}/gazelle-xua-jar/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    f"{EVS_BASE_URL}/evs/saml/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
    
    # Generic EVS endpoint
    f"{EVS_BASE_URL}/evs/ws/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl",
]

# Alternative REST API endpoints (if available)
POTENTIAL_REST_ENDPOINTS = [
    f"{EVS_BASE_URL}/evs/rest/validations",
    f"{EVS_BASE_URL}/api/evs/validations",
    f"{EVS_BASE_URL}/rest/evs/validations",
]

discovered_endpoints = []
discovered_validators = {}


def test_wsdl_endpoint(wsdl_url):
    """Test if a WSDL endpoint is accessible and functional"""
    print(f"\n{'─'*80}")
    print(f"Testing WSDL: {wsdl_url}")
    print(f"{'─'*80}")
    
    try:
        # Try to create SOAP client
        client = Client(wsdl_url)
        print("✓ WSDL accessible")
        
        # Test 'about' method if available
        try:
            if hasattr(client.service, 'about'):
                about_info = client.service.about()
                print(f"✓ about() method: {about_info}")
        except Exception as e:
            print(f"  about() method: {str(e)[:100]}")
        
        # Test 'getListOfValidators' method
        try:
            if hasattr(client.service, 'getListOfValidators'):
                print("\n  Attempting to list validators...")
                
                # Try without discriminator
                try:
                    validators = client.service.getListOfValidators()
                    if validators:
                        print(f"✓ Found {len(validators)} validators (no discriminator)")
                        return {
                            'url': wsdl_url,
                            'accessible': True,
                            'validators': validators,
                            'discriminator': None
                        }
                except Exception as e:
                    print(f"  Without discriminator: {str(e)[:100]}")
                
                # Try with common discriminators
                for discriminator in ['eHDSI', 'IHE', 'epSOS', '', 'eHealth']:
                    try:
                        validators = client.service.getListOfValidators(discriminator)
                        if validators:
                            print(f"✓ Found {len(validators)} validators (discriminator: '{discriminator}')")
                            return {
                                'url': wsdl_url,
                                'accessible': True,
                                'validators': validators,
                                'discriminator': discriminator
                            }
                    except Exception as e:
                        print(f"  discriminator '{discriminator}': {str(e)[:80]}")
        except Exception as e:
            print(f"  getListOfValidators() error: {str(e)[:100]}")
        
        # Even if we can't list validators, endpoint is accessible
        return {
            'url': wsdl_url,
            'accessible': True,
            'validators': None,
            'error': 'Could not retrieve validator list'
        }
        
    except TransportError as e:
        print(f"✗ Transport error: {str(e)[:100]}")
        return None
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")
        return None


def test_rest_endpoint(rest_url):
    """Test if a REST endpoint is accessible"""
    print(f"\n{'─'*80}")
    print(f"Testing REST: {rest_url}")
    print(f"{'─'*80}")
    
    headers = {'Accept': 'application/json'}
    
    if EVS_API_KEY:
        headers['Authorization'] = f'GazelleAPIKey {EVS_API_KEY}'
    
    try:
        # Try GET to see if endpoint exists
        response = requests.get(rest_url, headers=headers, timeout=10, verify=True)
        print(f"  GET response: {response.status_code}")
        
        if response.status_code in [200, 401, 403]:
            return {
                'url': rest_url,
                'accessible': True,
                'method': 'GET',
                'status': response.status_code
            }
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {str(e)[:100]}")
        return None


def main():
    """Main discovery process"""
    
    print("\n" + "="*80)
    print("PHASE 1: Testing WSDL Endpoints (SOAP Web Services)")
    print("="*80)
    
    for wsdl_url in POTENTIAL_WSDL_ENDPOINTS:
        result = test_wsdl_endpoint(wsdl_url)
        if result:
            discovered_endpoints.append(result)
            if result.get('validators'):
                service_name = wsdl_url.split('/')[3]  # Extract service name
                discovered_validators[service_name] = {
                    'url': wsdl_url,
                    'discriminator': result.get('discriminator'),
                    'validators': result['validators']
                }
    
    print("\n" + "="*80)
    print("PHASE 2: Testing REST Endpoints")
    print("="*80)
    
    for rest_url in POTENTIAL_REST_ENDPOINTS:
        result = test_rest_endpoint(rest_url)
        if result:
            discovered_endpoints.append(result)
    
    # Print summary
    print("\n" + "="*80)
    print("DISCOVERY SUMMARY")
    print("="*80)
    
    if discovered_endpoints:
        print(f"\n✓ Found {len(discovered_endpoints)} accessible endpoint(s):")
        for i, endpoint in enumerate(discovered_endpoints, 1):
            print(f"\n{i}. {endpoint['url']}")
            if endpoint.get('validators'):
                print(f"   Validators: {len(endpoint['validators'])}")
                if endpoint.get('discriminator'):
                    print(f"   Discriminator: '{endpoint['discriminator']}'")
    else:
        print("\n✗ No accessible endpoints found")
        print("\nPossible reasons:")
        print("  - Endpoints may require authentication")
        print("  - Endpoint URLs may have changed")
        print("  - Network/firewall restrictions")
        print("\nNext steps:")
        print("  1. Check API key configuration in .env")
        print("  2. Contact eHDSI Gazelle support for current endpoints")
        print("  3. Check https://gazelle.ehdsi.eu/evs/home.seam for documentation")
    
    # Print detailed validator information
    if discovered_validators:
        print("\n" + "="*80)
        print("AVAILABLE VALIDATORS")
        print("="*80)
        for service, info in discovered_validators.items():
            print(f"\nService: {service}")
            print(f"WSDL: {info['url']}")
            if info.get('discriminator'):
                print(f"Discriminator: '{info['discriminator']}'")
            print(f"Validators ({len(info['validators'])}):")
            for validator in info['validators']:
                print(f"  - {validator}")
    
    # Save results to file
    output_file = 'evs_discovery_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': EVS_BASE_URL,
            'discovered_endpoints': discovered_endpoints,
            'validators': discovered_validators
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    print("="*80)


if __name__ == '__main__':
    if not EVS_API_KEY:
        print("\n⚠️  WARNING: EVS_API_KEY not found in environment")
        print("   Some endpoints may require authentication")
        print("   Set your API key in .env file\n")
    
    main()
