"""
Discover FHIR R4 Validators on eHDSI Gazelle Platform (Matchbox)

Based on evidence from https://gazelle.ehdsi.eu/evs/default/allLogs.seam?standard=28
showing that eHDSI uses Matchbox for FHIR R4 validation.

Matchbox is a FHIR validation engine that validates against FHIR StructureDefinitions.
"""

import re
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
import json

load_dotenv()

EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')
EVS_API_KEY = os.getenv('EVS_API_KEY')

print(f"""
{'='*80}
eHDSI Gazelle FHIR R4 Validator Discovery (Matchbox)
{'='*80}
Base URL: {EVS_BASE_URL}
API Key: {'✓ Loaded' if EVS_API_KEY else '✗ Missing'}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
""")

# Potential Matchbox endpoints
POTENTIAL_MATCHBOX_ENDPOINTS = [
    f"{EVS_BASE_URL}/matchbox",
    f"{EVS_BASE_URL}/matchbox/fhir",
    f"{EVS_BASE_URL}/matchbox/fhir/r4",
    f"{EVS_BASE_URL}/fhir/r4",
    f"{EVS_BASE_URL}/evs/fhir",
    f"{EVS_BASE_URL}/evs/fhir/r4",
]

# Potential REST API endpoints for FHIR validation
POTENTIAL_FHIR_VALIDATION_ENDPOINTS = [
    f"{EVS_BASE_URL}/evs/rest/fhir/validate",
    f"{EVS_BASE_URL}/evs/rest/validations/fhir",
    f"{EVS_BASE_URL}/matchbox/fhir/$validate",
    f"{EVS_BASE_URL}/fhir/r4/$validate",
]

# Known FHIR R4 StructureDefinitions from the screenshot
KNOWN_FHIR_VALIDATORS = [
    "http://hl7.org/fhir/StructureDefinition/AuditEvent",
    "http://hl7.org/fhir/StructureDefinition/Patient",
    "http://hl7.org/fhir/StructureDefinition/Observation",
    "http://hl7.org/fhir/StructureDefinition/Condition",
    "http://hl7.org/fhir/StructureDefinition/MedicationStatement",
    "http://hl7.org/fhir/StructureDefinition/AllergyIntolerance",
    "http://hl7.org/fhir/StructureDefinition/Procedure",
    "http://hl7.org/fhir/StructureDefinition/Immunization",
    "http://hl7.org/fhir/StructureDefinition/Composition",
    "http://hl7.org/fhir/StructureDefinition/Bundle",
]

discovered_endpoints = []
discovered_validators = []


def test_fhir_endpoint(url):
    """Test if an endpoint responds as a FHIR server"""
    print(f"\n{'─'*80}")
    print(f"Testing: {url}")
    print(f"{'─'*80}")
    
    headers = {
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json'
    }
    
    if EVS_API_KEY:
        headers['Authorization'] = f'GazelleAPIKey {EVS_API_KEY}'
    
    try:
        # Try to get CapabilityStatement (FHIR metadata endpoint)
        metadata_url = f"{url}/metadata"
        response = requests.get(metadata_url, headers=headers, timeout=10, verify=True)
        
        print(f"  GET {metadata_url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if data.get('resourceType') == 'CapabilityStatement':
                    print(f"✓ FHIR Server found!")
                    print(f"  FHIR Version: {data.get('fhirVersion')}")
                    print(f"  Software: {data.get('software', {}).get('name', 'Unknown')}")
                    
                    return {
                        'url': url,
                        'type': 'FHIR Server',
                        'fhir_version': data.get('fhirVersion'),
                        'software': data.get('software', {}),
                        'accessible': True
                    }
            except Exception as e:
                print(f"  Response is not FHIR CapabilityStatement: {str(e)[:50]}")
        
        # Try as validation endpoint
        elif response.status_code in [400, 404, 405]:
            # Endpoint exists but requires different method/parameters
            return {
                'url': url,
                'type': 'Possible endpoint',
                'status': response.status_code,
                'accessible': True
            }
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {str(e)[:100]}")
        
    return None


def test_validation_endpoint(url):
    """Test a FHIR validation endpoint"""
    print(f"\n{'─'*80}")
    print(f"Testing validation: {url}")
    print(f"{'─'*80}")
    
    headers = {
        'Accept': 'application/fhir+json',
        'Content-Type': 'application/fhir+json'
    }
    
    if EVS_API_KEY:
        headers['Authorization'] = f'GazelleAPIKey {EVS_API_KEY}'
    
    # Simple FHIR Patient resource for testing
    test_patient = {
        "resourceType": "Patient",
        "id": "test-patient",
        "name": [{"family": "Test", "given": ["Patient"]}]
    }
    
    try:
        # Try POST for $validate operation
        response = requests.post(url, json=test_patient, headers=headers, timeout=10, verify=True)
        
        print(f"  POST {url}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code in [200, 201, 400]:
            try:
                data = response.json()
                if data.get('resourceType') == 'OperationOutcome':
                    print(f"✓ FHIR Validation endpoint found!")
                    print(f"  Response: OperationOutcome")
                    
                    return {
                        'url': url,
                        'type': 'FHIR Validation',
                        'method': 'POST',
                        'accessible': True
                    }
            except Exception as e:
                print(f"  Response parsing error: {str(e)[:50]}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {str(e)[:100]}")
    
    return None


def scrape_validator_page():
    """Try to scrape the validator page for available validators"""
    print(f"\n{'─'*80}")
    print(f"Scraping validator page")
    print(f"{'─'*80}")
    
    validator_page = f"{EVS_BASE_URL}/evs/default/validator.seam?standard=28"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(validator_page, headers=headers, timeout=10, verify=True)
        print(f"  GET {validator_page}")
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            # Look for select options, validator names, etc.
            html = response.text
            
            # Try to find validator select options
            validator_pattern = r'<option[^>]*value="([^"]*)"[^>]*>([^<]*)</option>'
            matches = re.findall(validator_pattern, html)
            
            if matches:
                print(f"\n✓ Found {len(matches)} validator options:")
                validators = []
                for value, text in matches:
                    if value and text and text.strip() != "Please select...":
                        print(f"  - {text} ({value})")
                        validators.append({'value': value, 'name': text})
                
                return validators
            
            # Try to find StructureDefinition URLs
            sd_pattern = r'http://hl7\.org/fhir/StructureDefinition/[A-Za-z]+'
            sd_matches = re.findall(sd_pattern, html)
            
            if sd_matches:
                print(f"\n✓ Found {len(set(sd_matches))} StructureDefinition references:")
                for sd in sorted(set(sd_matches)):
                    print(f"  - {sd}")
                
                return [{'url': sd, 'type': 'StructureDefinition'} for sd in set(sd_matches)]
        
    except Exception as e:
        print(f"✗ Error: {str(e)[:100]}")
    
    return []


def main():
    """Main discovery process"""
    
    print("\n" + "="*80)
    print("PHASE 1: Testing Matchbox/FHIR Endpoints")
    print("="*80)
    
    for endpoint in POTENTIAL_MATCHBOX_ENDPOINTS:
        result = test_fhir_endpoint(endpoint)
        if result:
            discovered_endpoints.append(result)
    
    print("\n" + "="*80)
    print("PHASE 2: Testing Validation Endpoints")
    print("="*80)
    
    for endpoint in POTENTIAL_FHIR_VALIDATION_ENDPOINTS:
        result = test_validation_endpoint(endpoint)
        if result:
            discovered_endpoints.append(result)
    
    print("\n" + "="*80)
    print("PHASE 3: Scraping Validator Page")
    print("="*80)
    
    validators = scrape_validator_page()
    if validators:
        discovered_validators.extend(validators)
    
    # Print summary
    print("\n" + "="*80)
    print("DISCOVERY SUMMARY")
    print("="*80)
    
    if discovered_endpoints:
        print(f"\n✓ Found {len(discovered_endpoints)} accessible endpoint(s):")
        for i, endpoint in enumerate(discovered_endpoints, 1):
            print(f"\n{i}. {endpoint['url']}")
            print(f"   Type: {endpoint.get('type', 'Unknown')}")
            if endpoint.get('fhir_version'):
                print(f"   FHIR Version: {endpoint['fhir_version']}")
    else:
        print("\n✗ No accessible endpoints found")
    
    if discovered_validators:
        print(f"\n✓ Found {len(discovered_validators)} validator(s):")
        for validator in discovered_validators:
            if 'url' in validator:
                print(f"  - {validator['url']}")
            else:
                print(f"  - {validator.get('name', '')} ({validator.get('value', '')})")
    else:
        print("\n⚠️  No validators discovered via scraping")
        print("\nKnown FHIR R4 Core StructureDefinitions (from documentation):")
        for sd in KNOWN_FHIR_VALIDATORS:
            print(f"  - {sd}")
    
    # Save results
    output_file = 'fhir_r4_discovery_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'base_url': EVS_BASE_URL,
            'discovered_endpoints': discovered_endpoints,
            'discovered_validators': discovered_validators,
            'known_fhir_validators': KNOWN_FHIR_VALIDATORS
        }, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    print("\nBased on the screenshot evidence, eHDSI Gazelle uses Matchbox for FHIR R4 validation.")
    print("\nMatchbox validates against FHIR StructureDefinitions, including:")
    print("  • FHIR R4 Core resources (Patient, Observation, etc.)")
    print("  • IPS (International Patient Summary) profiles")
    print("  • Custom Implementation Guides")
    print("\nTo use FHIR R4 validation on eHDSI:")
    print("  1. Access via web UI: https://gazelle.ehdsi.eu/evs/default/validator.seam?standard=28")
    print("  2. Or find the Matchbox REST API endpoint")
    print("  3. Validate your IPS bundles directly (no CDA conversion needed!)")
    
    print("="*80)


if __name__ == '__main__':
    main()
