"""
Retrieve validated CDA documents from Gazelle EVS logs using API credentials.

This script queries your Gazelle EVS test history to find CDA documents that:
1. Belong to your account (using your API key)
2. Passed validation
3. Can be downloaded as example documents

Usage:
    python scripts/retrieve_gazelle_cda_examples.py
    python scripts/retrieve_gazelle_cda_examples.py --limit 10
    python scripts/retrieve_gazelle_cda_examples.py --validator "eHDSI - PIVOT CDA (L3) validation"
"""

import os
import sys
import json
import requests
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import xml.etree.ElementTree as ET

# Load environment
load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')

# Potential API endpoints for test results/logs
TEST_RESULT_ENDPOINTS = [
    '/evs/rest/tests',
    '/evs/rest/validation/history',
    '/evs/rest/validation/results',
    '/evs/rest/my-tests',
    '/evs/rest/user/tests',
    '/evs/api/tests',
    '/evs/api/validation/history',
    '/api/tests',
    '/api/validation/history',
    '/rest/tests',
    '/rest/validation/history',
    '/gazelle-evs/rest/tests',
    '/gazelle-evs/rest/validation',
    '/CDAGenerator-ejb/rest/tests',
    '/CDAGenerator-ejb/rest/validation',
]


def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*80}")
    print(f"{title}")
    print(f"{'='*80}\n")


def print_section(title):
    """Print formatted section"""
    print(f"\n{'─'*80}")
    print(f"{title}")
    print(f"{'─'*80}")


def get_headers():
    """Get HTTP headers with API authentication"""
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    if EVS_API_KEY:
        # Try different authentication header formats
        headers['Authorization'] = f'GazelleAPIKey {EVS_API_KEY}'
        headers['X-API-Key'] = EVS_API_KEY
        headers['Api-Key'] = EVS_API_KEY
    
    return headers


def discover_test_endpoints():
    """Discover available REST API endpoints for test results"""
    print_header("Discovering Gazelle Test Result Endpoints")
    
    headers = get_headers()
    discovered = []
    
    for endpoint in TEST_RESULT_ENDPOINTS:
        url = f"{EVS_BASE_URL}{endpoint}"
        print(f"Trying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=True)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ SUCCESS! Endpoint found")
                discovered.append({
                    'url': url,
                    'endpoint': endpoint,
                    'response_preview': response.text[:200]
                })
            elif response.status_code == 401:
                print(f"  🔐 Requires authentication (endpoint exists!)")
                discovered.append({
                    'url': url,
                    'endpoint': endpoint,
                    'status': 'requires_auth'
                })
            elif response.status_code == 403:
                print(f"  🚫 Forbidden (endpoint exists, permissions issue)")
                discovered.append({
                    'url': url,
                    'endpoint': endpoint,
                    'status': 'forbidden'
                })
            elif response.status_code == 404:
                print(f"  ❌ Not found")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏱️  Timeout")
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}")
    
    return discovered


def query_test_results(endpoint_url):
    """Query test results from a discovered endpoint"""
    print_section(f"Querying test results from: {endpoint_url}")
    
    headers = get_headers()
    
    try:
        response = requests.get(endpoint_url, headers=headers, timeout=30, verify=True)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Retrieved {len(data) if isinstance(data, list) else 1} results")
                return data
            except json.JSONDecodeError:
                print(f"⚠️  Response is not JSON")
                print(f"Response preview: {response.text[:500]}")
                return None
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except Exception as e:
        print(f"❌ Error querying results: {e}")
        return None


def filter_passed_cda_tests(test_results):
    """Filter test results to find passed CDA validations"""
    print_section("Filtering for passed CDA tests")
    
    if not test_results:
        return []
    
    passed_tests = []
    
    # Handle both list and dict responses
    if isinstance(test_results, dict):
        test_results = [test_results]
    
    for test in test_results:
        # Look for common fields indicating CDA validation success
        test_type = test.get('type', '').lower()
        status = test.get('status', '').lower()
        validator = test.get('validator', '')
        
        is_cda = 'cda' in test_type or 'cda' in validator.lower()
        is_passed = 'pass' in status or 'success' in status or status == 'ok'
        
        if is_cda and is_passed:
            passed_tests.append(test)
            print(f"  ✅ Found: {test.get('id', 'unknown')} - {validator}")
    
    print(f"\nFound {len(passed_tests)} passed CDA tests")
    return passed_tests


def download_cda_document(test_result, output_dir='examples'):
    """Download CDA document from a test result"""
    print_section(f"Downloading CDA from test: {test_result.get('id', 'unknown')}")
    
    # Try to find document URL in test result
    possible_doc_keys = ['document_url', 'documentUrl', 'url', 'file', 'content', 'xml']
    
    doc_url = None
    doc_content = None
    
    for key in possible_doc_keys:
        if key in test_result:
            value = test_result[key]
            if isinstance(value, str) and (value.startswith('http') or value.startswith('/')):
                doc_url = value
                break
            elif isinstance(value, str) and value.strip().startswith('<?xml'):
                doc_content = value
                break
    
    # If we have inline content, save it directly
    if doc_content:
        print(f"  📄 Document content found inline")
        return save_cda_document(doc_content, test_result, output_dir)
    
    # If we have a URL, download it
    if doc_url:
        print(f"  🔗 Document URL: {doc_url}")
        
        if not doc_url.startswith('http'):
            doc_url = f"{EVS_BASE_URL}{doc_url}"
        
        headers = get_headers()
        
        try:
            response = requests.get(doc_url, headers=headers, timeout=30, verify=True)
            
            if response.status_code == 200:
                return save_cda_document(response.text, test_result, output_dir)
            else:
                print(f"  ❌ Failed to download: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Download error: {e}")
            return None
    
    print(f"  ⚠️  No document URL found in test result")
    print(f"  Available keys: {list(test_result.keys())}")
    return None


def save_cda_document(content, test_result, output_dir):
    """Save CDA document to file"""
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Generate filename from test result
    test_id = test_result.get('id', 'unknown')
    timestamp = test_result.get('timestamp', datetime.now().strftime('%Y%m%d'))
    validator = test_result.get('validator', 'cda')
    
    # Clean validator name for filename
    validator_clean = validator.replace(' ', '_').replace('-', '_').lower()
    validator_clean = ''.join(c for c in validator_clean if c.isalnum() or c == '_')[:30]
    
    filename = f"gazelle_{validator_clean}_{timestamp}_{test_id}.xml"
    filepath = output_path / filename
    
    # Save document
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Saved: {filepath}")
        
        # Try to extract basic info
        try:
            root = ET.fromstring(content)
            ns = {'cda': 'urn:hl7-org:v3'}
            
            title_elem = root.find('.//cda:title', ns)
            title = title_elem.text if title_elem is not None else 'Unknown'
            
            print(f"     Title: {title}")
            
        except:
            pass
        
        return str(filepath)
        
    except Exception as e:
        print(f"  ❌ Save error: {e}")
        return None


def try_gazelle_web_api():
    """Try Gazelle web interface API endpoints"""
    print_header("Trying Gazelle Web Interface API")
    
    headers = get_headers()
    
    # Common web API patterns
    web_endpoints = [
        '/evs/validation/validations.seam',
        '/evs/validation/validationsList.seam',
        '/gazelle/validation/myValidations.seam',
        '/gazelle-evs/validation/history',
    ]
    
    for endpoint in web_endpoints:
        url = f"{EVS_BASE_URL}{endpoint}"
        print(f"\nTrying: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=True)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ Endpoint accessible!")
                print(f"  Content-Type: {response.headers.get('Content-Type')}")
                print(f"  Preview: {response.text[:300]}")
                
        except Exception as e:
            print(f"  ❌ Error: {type(e).__name__}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Retrieve validated CDA documents from your Gazelle EVS test logs'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Maximum number of documents to retrieve'
    )
    parser.add_argument(
        '--validator',
        type=str,
        help='Filter by validator name (e.g., "eHDSI - PIVOT CDA")'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='examples',
        help='Output directory for downloaded documents'
    )
    
    args = parser.parse_args()
    
    if not EVS_API_KEY:
        print("❌ EVS_API_KEY not found in environment")
        print("Please set it in your .env file")
        return 1
    
    print_header("Gazelle EVS - Retrieve Validated CDA Documents")
    print(f"API Key: {EVS_API_KEY[:20]}...")
    print(f"Base URL: {EVS_BASE_URL}")
    print(f"Output: {args.output}")
    
    # Step 1: Discover available endpoints
    discovered = discover_test_endpoints()
    
    if not discovered:
        print("\n⚠️  No test result endpoints found via standard REST patterns")
        print("\nTrying alternative approaches...")
        try_gazelle_web_api()
        print("\n")
        print("="*80)
        print("SUGGESTION: Access Gazelle Web Interface")
        print("="*80)
        print(f"\n1. Go to: {EVS_BASE_URL}/evs/home.seam")
        print("2. Log in with your credentials")
        print("3. Navigate to: Validation > My Validations")
        print("4. Find passed CDA validations")
        print("5. Download the XML documents manually")
        print("\nOr, if you have specific CDA documents that passed validation,")
        print("place them in the 'examples/' directory and we can use them.")
        return 1
    
    # Step 2: Query test results from discovered endpoints
    all_results = []
    for discovered_endpoint in discovered:
        if discovered_endpoint.get('status') != 'requires_auth':
            results = query_test_results(discovered_endpoint['url'])
            if results:
                all_results.extend(results if isinstance(results, list) else [results])
    
    if not all_results:
        print("\n⚠️  No test results retrieved")
        return 1
    
    # Step 3: Filter for passed CDA tests
    passed_cda_tests = filter_passed_cda_tests(all_results)
    
    if not passed_cda_tests:
        print("\n⚠️  No passed CDA tests found")
        print("\nThis could mean:")
        print("1. The API endpoint structure is different than expected")
        print("2. Test history is not accessible via REST API")
        print("3. You need to access the web interface directly")
        return 1
    
    # Step 4: Download CDA documents
    print_section("Downloading CDA Documents")
    
    downloaded = []
    for i, test in enumerate(passed_cda_tests[:args.limit], 1):
        print(f"\n[{i}/{min(len(passed_cda_tests), args.limit)}]")
        
        # Filter by validator if specified
        if args.validator and args.validator.lower() not in test.get('validator', '').lower():
            print(f"  ⏭️  Skipping (validator doesn't match)")
            continue
        
        filepath = download_cda_document(test, args.output)
        if filepath:
            downloaded.append(filepath)
    
    # Summary
    print_header("Summary")
    print(f"✅ Downloaded {len(downloaded)} CDA documents")
    
    if downloaded:
        print("\nFiles saved to:")
        for filepath in downloaded:
            print(f"  - {filepath}")
        
        print(f"\n🎉 You can now use these validated CDA examples!")
        print(f"\nNext steps:")
        print(f"1. Review the documents in {args.output}/")
        print(f"2. Add them to your Streamlit UI example buttons")
        print(f"3. Validate them again to confirm they still pass")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
