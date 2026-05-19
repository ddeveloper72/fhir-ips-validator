"""
EHDS Gazelle Platform API Explorer

This script explores the EHDS Gazelle platform to discover available validators
for FHIR and CDA documents.

Key Standards:
- Standard 12: International Patient Summary (IPS)
- Standard 15: HL7 EU - Patient Summary (EU-EPS)
- Standard 17: HL7 EU - Base and Core

Usage:
    python scripts/explore_ehds_gazelle.py
    python scripts/explore_ehds_gazelle.py --standard 12
    python scripts/explore_ehds_gazelle.py --list-all
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Load environment
load_dotenv()

# EHDS Gazelle Configuration
EHDS_BASE_URL = os.getenv('EHDS_GAZELLE_BASE_URL', 'https://ehds.gazelle-platform.net')
EHDS_API_KEY = os.getenv('EHDS_GAZELLE_API_KEY')

# Known validator endpoints
VALIDATOR_STANDARDS = {
    12: {
        'name': 'International Patient Summary (IPS)',
        'url': f'{EHDS_BASE_URL}/evs/default/validator.seam?standard=12',
        'formats': ['FHIR', 'CDA'],
        'description': 'Validate International Patient Summary objects'
    },
    15: {
        'name': 'HL7 EU - Patient Summary (EU-EPS)',
        'url': f'{EHDS_BASE_URL}/evs/default/validator.seam?standard=15',
        'formats': ['FHIR', 'CDA'],
        'description': 'Validate HL7 EU Patient Summary objects'
    },
    17: {
        'name': 'HL7 EU - Base and Core',
        'url': f'{EHDS_BASE_URL}/evs/default/validator.seam?standard=17',
        'formats': ['FHIR'],
        'description': 'Validate HL7 EU Base and Core objects'
    }
}


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{title:^80}")
    print(f"{'='*80}\n")


def print_section(title):
    """Print formatted section"""
    print(f"\n{'─'*80}")
    print(f"  {title}")
    print(f"{'─'*80}")


def check_api_configuration():
    """Verify API configuration is valid"""
    print_section("API Configuration Check")
    
    if not EHDS_API_KEY:
        print("✗ EHDS_GAZELLE_API_KEY not found in .env")
        print("\nPlease add your API key to .env:")
        print("EHDS_GAZELLE_API_KEY=your_key_here")
        return False
    
    print(f"✓ Base URL: {EHDS_BASE_URL}")
    print(f"✓ API Key: {EHDS_API_KEY[:20]}...{EHDS_API_KEY[-10:]}")
    
    # Check API key expiry
    expiry = os.getenv('EHDS_GAZELLE_API_KEY_EXPIRY_DATE')
    if expiry:
        print(f"✓ Key Expires: {expiry}")
    
    return True


def discover_api_endpoints():
    """
    Try to discover API endpoints by examining the platform
    
    The EHDS Gazelle platform may have:
    - REST API endpoints
    - SOAP/WSDL services
    - GraphQL endpoints
    """
    print_section("Discovering API Endpoints")
    
    # Common API path patterns to try
    api_paths = [
        '/evs/api/v1/validators',
        '/evs/api/validators',
        '/api/evs/validators',
        '/api/v1/validators',
        '/rest/validators',
        '/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        '/evs/rest/validators',
    ]
    
    headers = {
        'User-Agent': 'EHDS-Gazelle-Explorer/1.0',
        'Accept': 'application/json, application/xml, text/html',
    }
    
    # Try with API key in different formats
    auth_variants = [
        {'X-API-Key': EHDS_API_KEY},
        {'Authorization': f'Bearer {EHDS_API_KEY}'},
        {'Authorization': f'ApiKey {EHDS_API_KEY}'},
        {'api_key': EHDS_API_KEY},
    ]
    
    discovered = []
    
    for path in api_paths:
        url = f"{EHDS_BASE_URL}{path}"
        print(f"\n→ Trying: {url}")
        
        for auth_header in auth_variants:
            try:
                test_headers = {**headers, **auth_header}
                response = requests.get(url, headers=test_headers, timeout=10, allow_redirects=True)
                
                print(f"  Status: {response.status_code} | Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                
                if response.status_code == 200:
                    discovered.append({
                        'url': url,
                        'auth': list(auth_header.keys())[0],
                        'content_type': response.headers.get('Content-Type'),
                        'response_size': len(response.content)
                    })
                    print(f"  ✓ Success with {list(auth_header.keys())[0]}")
                    
                    # Save response for analysis
                    save_response(url, response, f"discovery_{path.replace('/', '_')}")
                    break
                    
            except requests.exceptions.RequestException as e:
                print(f"  ✗ Error: {str(e)[:60]}")
                continue
    
    if discovered:
        print_section("Discovered Endpoints")
        for endpoint in discovered:
            print(f"\n✓ {endpoint['url']}")
            print(f"  Auth: {endpoint['auth']}")
            print(f"  Type: {endpoint['content_type']}")
            print(f"  Size: {endpoint['response_size']} bytes")
    else:
        print("\n⚠ No API endpoints discovered via simple HTTP requests")
        print("  The platform may require:")
        print("  - Session-based authentication (web login)")
        print("  - SOAP/WSDL service calls")
        print("  - Specific API documentation")
    
    return discovered


def explore_validator_standard(standard_id):
    """
    Explore a specific validator standard
    
    Args:
        standard_id: Standard number (12, 15, 17, etc.)
    """
    if standard_id not in VALIDATOR_STANDARDS:
        print(f"✗ Unknown standard: {standard_id}")
        return
    
    standard = VALIDATOR_STANDARDS[standard_id]
    print_section(f"Standard {standard_id}: {standard['name']}")
    
    print(f"\nDescription: {standard['description']}")
    print(f"Formats: {', '.join(standard['formats'])}")
    print(f"URL: {standard['url']}")
    
    # Try to access the validator page
    headers = {
        'User-Agent': 'EHDS-Gazelle-Explorer/1.0',
        'Accept': 'text/html,application/json',
        'X-API-Key': EHDS_API_KEY,
    }
    
    try:
        print(f"\n→ Attempting to access validator page...")
        response = requests.get(standard['url'], headers=headers, timeout=15, allow_redirects=False)
        
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        if response.status_code == 302 or response.status_code == 301:
            redirect = response.headers.get('Location', 'unknown')
            print(f"  Redirect: {redirect}")
            
            if 'login' in redirect.lower() or 'signin' in redirect.lower():
                print("\n  ⚠ Requires web-based authentication")
                print("  → API key alone may not be sufficient")
                print("  → May need session cookies or OAuth flow")
        
        elif response.status_code == 200:
            print("  ✓ Page accessible")
            save_response(standard['url'], response, f"standard_{standard_id}")
            
            # Try to parse HTML for validator information
            if 'text/html' in response.headers.get('Content-Type', ''):
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for validator options, forms, etc.
                forms = soup.find_all('form')
                selects = soup.find_all('select')
                
                print(f"\n  Found {len(forms)} forms, {len(selects)} dropdown menus")
                
                for select in selects:
                    options = select.find_all('option')
                    if len(options) > 0:
                        print(f"\n  Dropdown: {select.get('name', 'unnamed')}")
                        for opt in options[:5]:  # Show first 5
                            print(f"    - {opt.text.strip()}")
                        if len(options) > 5:
                            print(f"    ... and {len(options)-5} more")
        
        elif response.status_code == 401:
            print("  ✗ Unauthorized - API key may be invalid")
        
        elif response.status_code == 403:
            print("  ✗ Forbidden - API key may lack permissions")
            
    except requests.exceptions.RequestException as e:
        print(f"  ✗ Error: {str(e)}")


def save_response(url, response, prefix="response"):
    """Save HTTP response for later analysis"""
    logs_dir = "logs/ehds_api_exploration"
    os.makedirs(logs_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Sanitize prefix to remove invalid filename characters
    prefix = prefix.replace('/', '_').replace('\\', '_').replace('?', '_').replace(':', '_').replace('*', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    # Determine file extension
    content_type = response.headers.get('Content-Type', '')
    if 'json' in content_type:
        ext = 'json'
    elif 'xml' in content_type:
        ext = 'xml'
    elif 'html' in content_type:
        ext = 'html'
    else:
        ext = 'txt'
    
    filename = f"{logs_dir}/{prefix}_{timestamp}.{ext}"
    
    with open(filename, 'wb') as f:
        f.write(response.content)
    
    print(f"  💾 Saved to: {filename}")


def try_soap_wsdl():
    """
    Try to discover SOAP/WSDL services similar to the old Gazelle platform
    """
    print_section("SOAP/WSDL Discovery")
    
    wsdl_paths = [
        '/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        '/XDStarClient-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        '/evs/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
        '/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl',
    ]
    
    for path in wsdl_paths:
        url = f"{EHDS_BASE_URL}{path}"
        print(f"\n→ Trying WSDL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200 and 'xml' in response.headers.get('Content-Type', '').lower():
                print("  ✓ WSDL found!")
                
                # Check if it's valid WSDL
                if b'wsdl:definitions' in response.content or b'definitions' in response.content:
                    print("  ✓ Valid WSDL document")
                    save_response(url, response, f"wsdl{path.replace('/', '_')}")
                    
                    # Try to use zeep to parse
                    try:
                        from zeep import Client
                        client = Client(url)
                        
                        # List available operations
                        print("\n  Available operations:")
                        for service in client.wsdl.services.values():
                            for port in service.ports.values():
                                for operation in port.binding._operations.values():
                                    print(f"    - {operation.name}")
                    except ImportError:
                        print("  ⚠ zeep not available for WSDL parsing")
                    except Exception as e:
                        print(f"  ⚠ WSDL parsing error: {str(e)[:60]}")
                        
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:60]}")


def list_all_standards():
    """List all known validator standards"""
    print_section("Known Validator Standards")
    
    for std_id, info in VALIDATOR_STANDARDS.items():
        print(f"\n[Standard {std_id}] {info['name']}")
        print(f"  Formats: {', '.join(info['formats'])}")
        print(f"  Description: {info['description']}")
        print(f"  URL: {info['url']}")


def main():
    parser = argparse.ArgumentParser(
        description='Explore EHDS Gazelle platform validators',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--standard', type=int, choices=[12, 15, 17],
                       help='Explore specific standard (12=IPS, 15=EU-EPS, 17=Base)')
    parser.add_argument('--list-all', action='store_true',
                       help='List all known standards')
    parser.add_argument('--discover', action='store_true',
                       help='Attempt to discover API endpoints')
    parser.add_argument('--soap', action='store_true',
                       help='Try to discover SOAP/WSDL services')
    
    args = parser.parse_args()
    
    print_header("EHDS Gazelle Platform Explorer")
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check configuration
    if not check_api_configuration():
        sys.exit(1)
    
    # Execute requested actions
    if args.list_all:
        list_all_standards()
    
    if args.standard:
        explore_validator_standard(args.standard)
    
    if args.discover:
        discover_api_endpoints()
    
    if args.soap:
        try_soap_wsdl()
    
    # Default: run basic exploration
    if not any([args.list_all, args.standard, args.discover, args.soap]):
        print("\n💡 Running default exploration...")
        list_all_standards()
        print("\n")
        discover_api_endpoints()
        print("\n")
        try_soap_wsdl()
        print("\n")
        for std_id in [12, 15, 17]:
            explore_validator_standard(std_id)
    
    print("\n" + "="*80)
    print("Exploration complete!")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()
