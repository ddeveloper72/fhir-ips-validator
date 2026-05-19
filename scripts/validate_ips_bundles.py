"""
Validate IPS bundles using eHDSI Matchbox web validator.

This script properly submits FHIR resources by filling the textarea field
and selecting the appropriate validator.
"""

import os
import sys
import json
import requests
from requests.sessions import Session
from pathlib import Path
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re
import time

# Load environment variables
load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')
VALIDATOR_URL = f"{EVS_BASE_URL}/evs/default/validator.seam?standard=28"


def validate_ips_bundle(bundle_path):
    """Validate an IPS bundle using the Matchbox web validator."""
    
    # Load bundle
    bundle_file = Path(bundle_path)
    if not bundle_file.exists():
        print(f"❌ File not found: {bundle_path}")
        return None
    
    with open(bundle_file, 'r', encoding='utf-8') as f:
        bundle_json = f.read()
    
    print(f"\n{'='*70}")
    print(f"🔍 VALIDATING: {bundle_file.name}")
    print(f"{'='*70}")
    print(f"Size: {len(bundle_json):,} bytes")
    
    # Parse to get resource type
    try:
        bundle_data = json.loads(bundle_json)
        resource_type = bundle_data.get('resourceType', 'Unknown')
        print(f"Resource Type: {resource_type}")
        if resource_type == 'Bundle':
            entry_count = len(bundle_data.get('entry', []))
            print(f"Entries: {entry_count}")
    except:
        pass
    
    # Create session
    session = Session()
    session.headers.update({
        'User-Agent': 'HL7-EU-Gazelle-Validator/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9',
    })
    
    if EVS_API_KEY:
        session.headers.update({
            'Authorization': f'Bearer {EVS_API_KEY}',
            'X-API-Key': EVS_API_KEY,
        })
    
    # Step 1: Get validator page to establish session
    print(f"\n📄 Loading validator page...")
    response = session.get(VALIDATOR_URL, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Failed to load page: {response.status_code}")
        return None
    
    print(f"✅ Page loaded (cookies: {list(session.cookies.keys())})")
    
    # Parse form
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the main validation form
    form = None
    for f in soup.find_all('form'):
        if 'validateCDAButton' in str(f):
            form = f
            break
    
    if not form:
        print("❌ Could not find validation form")
        return None
    
    # Extract form fields
    form_data = {}
    
    # Get all hidden inputs
    for input_field in form.find_all('input', {'type': 'hidden'}):
        name = input_field.get('name')
        value = input_field.get('value', '')
        if name:
            form_data[name] = value
    
    # Find textarea name for message content
    textarea = soup.find('textarea', {'id': re.compile('messagearea')})
    if textarea:
        textarea_name = textarea.get('name')
        print(f"✅ Found textarea: {textarea_name}")
        form_data[textarea_name] = bundle_json
    else:
        print("⚠️  Textarea not found, will try form upload")
    
    # Find validator dropdown
    validator_select = soup.find('select', {'id': re.compile('validator|profile', re.I)})
    if validator_select:
        validator_name = validator_select.get('name')
        # Select Bundle validator
        form_data[validator_name] = 'http://hl7.org/fhir/StructureDefinition/Bundle'
        print(f"✅ Selected validator: Bundle")
    
    # Find validate button
    validate_button = soup.find('input', {'id': re.compile('validate', re.I), 'type': 'submit'})
    if validate_button:
        button_name = validate_button.get('name')
        button_value = validate_button.get('value', 'Validate')
        form_data[button_name] = button_value
        print(f"✅ Found button: {button_name}")
    
    # Get form action
    form_action = form.get('action', '/evs/default/validator.seam')
    if not form_action.startswith('http'):
        form_action = f"{EVS_BASE_URL}{form_action}"
    
    print(f"\n🚀 Submitting validation request...")
    print(f"Endpoint: {form_action}")
    print(f"Form fields: {list(form_data.keys())}")
    
    # Submit form
    try:
        response = session.post(
            form_action,
            data=form_data,
            timeout=120,
            allow_redirects=True
        )
        
        print(f"Response: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
        
        # Parse response
        result = parse_validation_response(response.text, bundle_file.name)
        
        return result
        
    except Exception as e:
        print(f"❌ Error submitting: {e}")
        return None


def parse_validation_response(html, filename):
    """Parse the validation result HTML."""
    
    soup = BeautifulSoup(html, 'html.parser')
    
    result = {
        'filename': filename,
        'errors': [],
        'warnings': [],
        'info': [],
        'success_indicators': [],
        'raw_text': ''
    }
    
    # Look for result indicators
    text = soup.get_text()
    result['raw_text'] = text
    
    # Check for success/failure patterns
    patterns = {
        'success': [
            r'validation.*?passed',
            r'successfully.*?validated',
            r'no.*?errors?.*?found',
            r'valid.*?resource',
        ],
        'failure': [
            r'validation.*?failed',
            r'\d+.*?errors?.*?found',
            r'invalid.*?resource',
            r'validation.*?errors?',
        ],
        'warning': [
            r'\d+.*?warnings?',
            r'potential.*?issues?',
        ]
    }
    
    for category, pattern_list in patterns.items():
        for pattern in pattern_list:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result['success_indicators'].append(f"{category}: {matches[0]}")
    
    # Look for error/warning divs or spans
    for severity in ['error', 'warning', 'info', 'success']:
        elements = soup.find_all(class_=re.compile(severity, re.I))
        for elem in elements:
            text = elem.get_text(strip=True)
            if text and len(text) > 10:  # Skip empty or very short elements
                if severity == 'error':
                    result['errors'].append(text)
                elif severity == 'warning':
                    result['warnings'].append(text)
                else:
                    result['info'].append(text)
    
    # Look for validation log content
    log_div = soup.find('div', {'id': re.compile('log|result|validation', re.I)})
    if log_div:
        result['validation_log'] = log_div.get_text(strip=True)[:2000]
    
    # Look for specific error messages in text
    error_patterns = [
        r'Error:([^\n]+)',
        r'ERROR:([^\n]+)',
        r'Invalid:([^\n]+)',
        r'Failed:([^\n]+)',
    ]
    
    for pattern in error_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.strip() not in result['errors']:
                result['errors'].append(match.strip())
    
    # Save full HTML for debugging
    debug_file = f"validation_response_{filename.replace('.json', '')}.html"
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(html)
    result['debug_file'] = debug_file
    
    return result


def print_validation_results(result):
    """Print validation results in a readable format."""
    
    if not result:
        print("❌ No results to display")
        return
    
    print(f"\n{'='*70}")
    print(f"VALIDATION RESULTS: {result['filename']}")
    print(f"{'='*70}")
    
    if result.get('success_indicators'):
        print(f"\n📊 Indicators Found:")
        for indicator in result['success_indicators']:
            print(f"  • {indicator}")
    
    if result.get('errors'):
        print(f"\n❌ ERRORS ({len(result['errors'])}):")
        for i, error in enumerate(result['errors'][:10], 1):
            print(f"  {i}. {error[:200]}")
    
    if result.get('warnings'):
        print(f"\n⚠️  WARNINGS ({len(result['warnings'])}):")
        for i, warning in enumerate(result['warnings'][:10], 1):
            print(f"  {i}. {warning[:200]}")
    
    if result.get('info'):
        print(f"\n💡 INFO ({len(result['info'])}):")
        for i, info in enumerate(result['info'][:5], 1):
            print(f"  {i}. {info[:200]}")
    
    if result.get('validation_log'):
        print(f"\n📝 Validation Log Preview:")
        print(result['validation_log'][:500])
    
    print(f"\n💾 Full response saved to: {result.get('debug_file', 'N/A')}")
    print(f"{'='*70}\n")


def main():
    """Main entry point - validate both IPS bundles."""
    
    # Default bundles to validate
    bundles = [
        'examples/Diana_Ferreira_bundle.json',
        'examples/Patrick_Murphy_bundle.json',
    ]
    
    # Allow command line override
    if len(sys.argv) > 1:
        bundles = sys.argv[1:]
    
    print("\n" + "="*70)
    print("IPS BUNDLE VALIDATION - eHDSI Matchbox Validator")
    print("="*70)
    
    if not EVS_API_KEY:
        print("⚠️  EVS_API_KEY not set - validation may have limited functionality")
    
    results = []
    
    for bundle_path in bundles:
        result = validate_ips_bundle(bundle_path)
        if result:
            results.append(result)
            print_validation_results(result)
        
        # Brief pause between validations
        if len(bundles) > 1:
            time.sleep(2)
    
    # Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    
    for result in results:
        error_count = len(result.get('errors', []))
        warning_count = len(result.get('warnings', []))
        
        status = "✅ CLEAN" if error_count == 0 else f"❌ {error_count} ERROR(S)"
        print(f"{result['filename']}: {status} ({warning_count} warnings)")
    
    print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
