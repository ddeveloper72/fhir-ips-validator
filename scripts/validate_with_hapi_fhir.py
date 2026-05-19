"""
Validate FHIR resources using public HAPI FHIR server.

This script validates FHIR resources using the public HAPI FHIR test server's
$validate operation. No authentication required.

Public Test Server: http://hapi.fhir.org/baseR4
Note: This is a public test server, not for production use with real patient data.
"""

import os
import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional


# Public HAPI FHIR server endpoint
HAPI_FHIR_BASE_URL = 'http://hapi.fhir.org/baseR4'


def validate_with_hapi_fhir(bundle_path: str, profile: Optional[str] = None, timeout: int = 60) -> Optional[Dict[str, Any]]:
    """
    Validate a FHIR resource using public HAPI FHIR server.
    
    Args:
        bundle_path: Path to FHIR resource JSON file
        profile: Optional profile URL to validate against
        timeout: Request timeout in seconds
        
    Returns:
        Dict with validation results or None on error
    """
    
    # Load resource
    bundle_file = Path(bundle_path)
    if not bundle_file.exists():
        print(f"❌ File not found: {bundle_path}")
        return None
    
    with open(bundle_file, 'r', encoding='utf-8') as f:
        resource_json = f.read()
    
    try:
        resource_data = json.loads(resource_json)
        resource_type = resource_data.get('resourceType', 'Unknown')
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return None
    
    print(f"\n{'='*70}")
    print(f"🔍 VALIDATING: {bundle_file.name}")
    print(f"{'='*70}")
    print(f"Resource Type: {resource_type}")
    print(f"Size: {len(resource_json):,} bytes")
    print(f"Server: {HAPI_FHIR_BASE_URL} (Public)")
    
    if resource_type == 'Bundle':
        entry_count = len(resource_data.get('entry', []))
        print(f"Entries: {entry_count}")
    
    # Prepare validation endpoint
    if resource_type and resource_type != 'Unknown':
        validate_url = f"{HAPI_FHIR_BASE_URL}/{resource_type}/$validate"
    else:
        validate_url = f"{HAPI_FHIR_BASE_URL}/$validate"
    
    print(f"\n🚀 Validation endpoint: {validate_url}")
    
    if profile:
        print(f"📋 Profile: {profile}")
        validate_url += f"?profile={profile}"
    
    # Prepare request (no authentication needed for public server)
    headers = {
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json',
    }
    
    # Submit validation request
    try:
        print("⏳ Submitting to HAPI FHIR public server...")
        response = requests.post(
            validate_url,
            data=resource_json,
            headers=headers,
            timeout=timeout
        )
        
        print(f"📥 Response: {response.status_code}")
        
        if response.status_code in [200, 201]:
            # Parse OperationOutcome
            try:
                operation_outcome = response.json()
                return parse_operation_outcome(operation_outcome, bundle_file.name)
            except:
                print(f"⚠️  Response is not JSON")
                print(response.text[:500])
                return None
                
        elif response.status_code == 400:
            # Validation errors returned as OperationOutcome
            try:
                operation_outcome = response.json()
                return parse_operation_outcome(operation_outcome, bundle_file.name)
            except:
                print(f"❌ Validation failed (400) - could not parse response")
                print(response.text[:500])
                return None
        else:
            print(f"❌ Unexpected response code: {response.status_code}")
            print(response.text[:500])
            return None
            
    except requests.Timeout:
        print(f"❌ Request timed out after {timeout} seconds")
        print("   The HAPI FHIR public server may be slow or unavailable")
        return None
    except requests.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


def parse_operation_outcome(operation_outcome: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """Parse FHIR OperationOutcome and return structured results."""
    
    if operation_outcome.get('resourceType') != 'OperationOutcome':
        return {
            'success': False,
            'filename': filename,
            'error': f"Unexpected response type: {operation_outcome.get('resourceType')}",
            'errors': [],
            'warnings': [],
            'information': []
        }
    
    issues = operation_outcome.get('issue', [])
    
    errors = []
    warnings = []
    information = []
    
    for issue in issues:
        severity = issue.get('severity', 'unknown')
        
        issue_data = {
            'severity': severity,
            'code': issue.get('code', 'unknown'),
            'diagnostics': issue.get('diagnostics', 'No message'),
            'location': issue.get('location', []),
            'expression': issue.get('expression', [])
        }
        
        if severity in ['error', 'fatal']:
            errors.append(issue_data)
        elif severity == 'warning':
            warnings.append(issue_data)
        else:  # information
            information.append(issue_data)
    
    return {
        'success': True,
        'filename': filename,
        'errors': errors,
        'warnings': warnings,
        'information': information,
        'raw_response': operation_outcome
    }


def print_validation_results(result: Dict[str, Any]):
    """Print validation results in readable format."""
    
    if not result:
        return
    
    if not result.get('success'):
        print(f"\n❌ Validation Error: {result.get('error')}")
        return
    
    print(f"\n{'='*70}")
    print("📊 VALIDATION RESULTS")
    print(f"{'='*70}")
    
    errors = result.get('errors', [])
    warnings = result.get('warnings', [])
    information = result.get('information', [])
    
    print(f"\n❌ Errors: {len(errors)}")
    print(f"⚠️  Warnings: {len(warnings)}")
    print(f"ℹ️  Information: {len(information)}")
    
    if errors:
        print(f"\n{'─'*70}")
        print("❌ ERRORS:")
        print(f"{'─'*70}")
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error.get('diagnostics')}")
            if error.get('expression'):
                print(f"   Location: {', '.join(error.get('expression'))}")
    
    if warnings:
        print(f"\n{'─'*70}")
        print("⚠️  WARNINGS:")
        print(f"{'─'*70}")
        for i, warning in enumerate(warnings, 1):
            print(f"\n{i}. {warning.get('diagnostics')}")
            if warning.get('expression'):
                print(f"   Location: {', '.join(warning.get('expression'))}")
    
    if information and not errors:  # Only show info if no errors
        print(f"\n{'─'*70}")
        print("ℹ️  INFORMATION:")
        print(f"{'─'*70}")
        for i, info in enumerate(information[:5], 1):  # Limit to 5
            print(f"\n{i}. {info.get('diagnostics')}")


def main():
    """Main entry point."""
    
    # Default bundles
    bundles = [
        'examples/Diana_Ferreira_bundle.json',
        'examples/Patrick_Murphy_bundle.json',
    ]
    
    # Allow command line override
    if len(sys.argv) > 1:
        bundles = sys.argv[1:]
    
    print("\n" + "="*70)
    print("🩺 HAPI FHIR PUBLIC VALIDATION SERVICE")
    print("="*70)
    print(f"Server: {HAPI_FHIR_BASE_URL}")
    print("⚠️  Public test server - not for production data!")
    print("="*70)
    
    results = []
    for bundle_path in bundles:
        result = validate_with_hapi_fhir(bundle_path)
        if result:
            results.append(result)
            print_validation_results(result)
    
    # Summary
    if results:
        print(f"\n{'='*70}")
        print(f"📊 SUMMARY: {len(results)} files validated")
        print(f"{'='*70}")
        
        for result in results:
            status = "✅ PASS" if not result.get('errors') else "❌ FAIL"
            error_count = len(result.get('errors', []))
            warning_count = len(result.get('warnings', []))
            print(f"{status} {result['filename']}: {error_count} errors, {warning_count} warnings")
        
        return 0 if all(not r.get('errors') for r in results) else 1
    else:
        print("\n❌ No files validated successfully")
        return 1


if __name__ == '__main__':
    sys.exit(main())
