"""
Test FHIR R4 validation via eHDSI Matchbox web UI form submission.

This script tests validation by submitting FHIR resources to the Matchbox
validator web interface on the eHDSI platform.

Usage:
    python test_matchbox_web_validation.py <fhir_file_path>
    
Example:
    python test_matchbox_web_validation.py examples/Diana_Ferreira_bundle.json
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

# Load environment variables
load_dotenv()

EVS_API_KEY = os.getenv('EVS_API_KEY')
EVS_BASE_URL = os.getenv('EVS_BASE_URL', 'https://gazelle.ehdsi.eu')

# Matchbox validator page for FHIR R4 (standard=28)
VALIDATOR_PAGE_URL = f"{EVS_BASE_URL}/evs/default/validator.seam?standard=28"

class MatchboxWebValidator:
    """Client for validating FHIR resources via Matchbox web UI."""
    
    def __init__(self, api_key=None, base_url=None):
        """Initialize the validator client.
        
        Args:
            api_key: EVS API key for authentication
            base_url: Base URL for eHDSI platform
        """
        self.api_key = api_key or EVS_API_KEY
        self.base_url = base_url or EVS_BASE_URL
        self.validator_url = f"{self.base_url}/evs/default/validator.seam?standard=28"
        
        # Create persistent session for cookies
        self.session = Session()
        self.session.headers.update({
            'User-Agent': 'HL7-EU-Gazelle-Validator/1.0',
            'Accept': 'text/html,application/json,application/xhtml+xml,application/xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        
        # Add API key if available
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'X-API-Key': self.api_key,
            })
    
    def get_validator_page(self):
        """Fetch the validator page to extract form parameters.
        
        Returns:
            tuple: (page_html, form_action, form_params)
        """
        print(f"📄 Fetching validator page: {self.validator_url}")
        
        try:
            response = self.session.get(self.validator_url, timeout=30)
            response.raise_for_status()
            
            print(f"✅ Page loaded (status: {response.status_code})")
            print(f"   Cookies: {list(self.session.cookies.keys())}")
            
            # Parse HTML to find form
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for validation form
            forms = soup.find_all('form')
            print(f"   Found {len(forms)} form(s)")
            
            # Extract form parameters
            form_params = {}
            form_action = None
            
            for form in forms:
                # Look for file upload or validation forms
                if form.find('input', {'type': 'file'}) or 'validat' in str(form).lower():
                    form_action = form.get('action')
                    print(f"   Form action: {form_action}")
                    
                    # Extract all input fields
                    for input_field in form.find_all('input'):
                        name = input_field.get('name')
                        value = input_field.get('value', '')
                        input_type = input_field.get('type', 'text')
                        
                        if name:
                            form_params[name] = value
                            print(f"   Input: {name} = {value} (type: {input_type})")
            
            return response.text, form_action, form_params
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching validator page: {e}")
            return None, None, None
    
    def validate_fhir_resource(self, fhir_file_path, profile=None):
        """Validate a FHIR resource via web form submission.
        
        Args:
            fhir_file_path: Path to FHIR JSON or XML file
            profile: Optional StructureDefinition URL to validate against
            
        Returns:
            dict: Validation results
        """
        # Load FHIR resource
        fhir_path = Path(fhir_file_path)
        if not fhir_path.exists():
            return {
                'success': False,
                'error': f'File not found: {fhir_file_path}'
            }
        
        with open(fhir_path, 'r', encoding='utf-8') as f:
            fhir_content = f.read()
        
        # Detect format
        is_json = fhir_path.suffix.lower() == '.json'
        content_type = 'application/fhir+json' if is_json else 'application/fhir+xml'
        
        print(f"\n🔍 Validating: {fhir_path.name}")
        print(f"   Format: {'JSON' if is_json else 'XML'}")
        print(f"   Size: {len(fhir_content)} bytes")
        
        if profile:
            print(f"   Profile: {profile}")
        
        # Get validator page and form params
        page_html, form_action, form_params = self.get_validator_page()
        
        if not page_html:
            return {
                'success': False,
                'error': 'Could not load validator page'
            }
        
        # Try different validation endpoints
        validation_endpoints = [
            f"{self.base_url}/evs/default/validator.seam",
            f"{self.base_url}/evs/default/validate",
            f"{self.base_url}/evs/validator/validate",
            f"{self.base_url}/matchbox/fhir/$validate",
            form_action if form_action else None,
        ]
        
        for endpoint in validation_endpoints:
            if not endpoint:
                continue
            
            # Make endpoint absolute if relative
            if endpoint.startswith('/'):
                endpoint = f"{self.base_url}{endpoint}"
            
            print(f"\n🚀 Trying endpoint: {endpoint}")
            
            # Try multipart form upload
            result = self._try_form_upload(endpoint, fhir_path, fhir_content, form_params, profile)
            if result.get('success'):
                return result
            
            # Try direct POST
            result = self._try_direct_post(endpoint, fhir_content, content_type, profile)
            if result.get('success'):
                return result
        
        return {
            'success': False,
            'error': 'Could not find working validation endpoint',
            'tried_endpoints': [e for e in validation_endpoints if e]
        }
    
    def _try_form_upload(self, endpoint, fhir_path, fhir_content, form_params, profile):
        """Try validation via multipart form upload."""
        try:
            # Prepare multipart form data
            files = {
                'file': (fhir_path.name, fhir_content, 'application/json'),
            }
            
            # Add form parameters
            data = form_params.copy()
            if profile:
                data['profile'] = profile
            data['standard'] = '28'  # FHIR R4
            
            print(f"   Method: Multipart form upload")
            print(f"   Data: {list(data.keys())}")
            
            response = self.session.post(
                endpoint,
                files=files,
                data=data,
                timeout=60,
                allow_redirects=True
            )
            
            print(f"   Response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                # Parse response
                return self._parse_validation_response(response)
            elif response.status_code == 302:
                print(f"   Redirect: {response.headers.get('Location')}")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        return {'success': False}
    
    def _try_direct_post(self, endpoint, fhir_content, content_type, profile):
        """Try validation via direct POST."""
        try:
            headers = {
                'Content-Type': content_type,
            }
            
            params = {'standard': '28'}  # FHIR R4
            if profile:
                params['profile'] = profile
            
            print(f"   Method: Direct POST")
            print(f"   Content-Type: {content_type}")
            
            response = self.session.post(
                endpoint,
                data=fhir_content,
                headers=headers,
                params=params,
                timeout=60,
                allow_redirects=True
            )
            
            print(f"   Response: {response.status_code}")
            
            if response.status_code in [200, 201]:
                # Parse response
                return self._parse_validation_response(response)
                
        except Exception as e:
            print(f"   Error: {e}")
        
        return {'success': False}
    
    def _parse_validation_response(self, response):
        """Parse validation response (HTML or JSON).
        
        Args:
            response: requests.Response object
            
        Returns:
            dict: Parsed validation results
        """
        content_type = response.headers.get('Content-Type', '').lower()
        
        # Try JSON response (OperationOutcome)
        if 'json' in content_type:
            try:
                operation_outcome = response.json()
                if operation_outcome.get('resourceType') == 'OperationOutcome':
                    return self._parse_operation_outcome(operation_outcome)
            except:
                pass
        
        # Try HTML response
        if 'html' in content_type or '<html' in response.text[:100].lower():
            return self._parse_html_response(response.text)
        
        # Unknown format
        return {
            'success': True,
            'content_type': content_type,
            'raw_response': response.text[:500]
        }
    
    def _parse_operation_outcome(self, operation_outcome):
        """Parse FHIR OperationOutcome resource."""
        issues = operation_outcome.get('issue', [])
        
        errors = [i for i in issues if i.get('severity') == 'error']
        warnings = [i for i in issues if i.get('severity') == 'warning']
        info = [i for i in issues if i.get('severity') == 'information']
        
        return {
            'success': True,
            'format': 'OperationOutcome',
            'is_valid': len(errors) == 0,
            'error_count': len(errors),
            'warning_count': len(warnings),
            'info_count': len(info),
            'issues': issues
        }
    
    def _parse_html_response(self, html):
        """Parse HTML validation results page."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for validation results
        results = {
            'success': True,
            'format': 'HTML',
            'raw_html': html[:1000]
        }
        
        # Common patterns in validation result pages
        result_patterns = [
            ('success', r'validation.*success', re.IGNORECASE),
            ('valid', r'resource.*valid', re.IGNORECASE),
            ('passed', r'validation.*passed', re.IGNORECASE),
            ('error', r'validation.*error', re.IGNORECASE),
            ('failed', r'validation.*failed', re.IGNORECASE),
            ('invalid', r'resource.*invalid', re.IGNORECASE),
        ]
        
        text = soup.get_text()
        for key, pattern, flags in result_patterns:
            if re.search(pattern, text, flags):
                results[f'found_{key}'] = True
        
        # Extract error/warning divs
        for severity in ['error', 'warning', 'info', 'success']:
            elements = soup.find_all(class_=re.compile(severity, re.I))
            if elements:
                results[f'{severity}_elements'] = len(elements)
                results[f'{severity}_text'] = [e.get_text(strip=True) for e in elements[:5]]
        
        return results


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python test_matchbox_web_validation.py <fhir_file_path> [profile]")
        print("\nExamples:")
        print("  python test_matchbox_web_validation.py examples/Diana_Ferreira_bundle.json")
        print("  python test_matchbox_web_validation.py examples/Patrick_Murphy_bundle.json")
        print("  python test_matchbox_web_validation.py examples/patient_bundle_complete.json")
        sys.exit(1)
    
    fhir_file = sys.argv[1]
    profile = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check environment
    if not EVS_API_KEY:
        print("⚠️  Warning: EVS_API_KEY not set in .env")
        print("   Some features may require authentication")
    
    # Create validator
    validator = MatchboxWebValidator()
    
    # Validate resource
    result = validator.validate_fhir_resource(fhir_file, profile)
    
    # Display results
    print("\n" + "="*70)
    print("VALIDATION RESULTS")
    print("="*70)
    print(json.dumps(result, indent=2))
    print("="*70)
    
    # Summary
    if result.get('success'):
        if result.get('is_valid'):
            print("\n✅ VALIDATION PASSED")
        elif result.get('error_count'):
            print(f"\n❌ VALIDATION FAILED: {result['error_count']} error(s)")
        else:
            print("\n✅ Request successful (check results above)")
    else:
        print(f"\n❌ VALIDATION REQUEST FAILED: {result.get('error')}")
    
    return 0 if result.get('success') else 1


if __name__ == '__main__':
    sys.exit(main())
