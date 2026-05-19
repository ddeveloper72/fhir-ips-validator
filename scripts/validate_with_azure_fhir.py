"""
Validate IPS bundles using Azure FHIR API.

This script validates FHIR resources using Azure FHIR Service $validate operation.
Requires Azure authentication and FHIR service endpoint.

Prerequisites:
    pip install azure-identity

Environment Variables:
    AZURE_FHIR_URL - Your Azure FHIR service URL (e.g., https://my-fhir.azurehealthcareapis.com)
    AZURE_TENANT_ID - Azure AD tenant ID (optional, uses default credential chain)
    AZURE_CLIENT_ID - Service principal client ID (optional)
    AZURE_CLIENT_SECRET - Service principal secret (optional)
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

try:
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
except ImportError:
    print("❌ Azure Identity library not installed")
    print("   Install with: pip install azure-identity")
    sys.exit(1)

load_dotenv()

# Use environment variable names from Django project
AZURE_FHIR_URL = os.getenv('AZURE_FHIR_BASE_URL')
AZURE_TENANT_ID = os.getenv('AZURE_FHIR_TENANT_ID')
AZURE_CLIENT_ID = os.getenv('AZURE_FHIR_CLIENT_ID')
AZURE_CLIENT_SECRET = os.getenv('AZURE_FHIR_CLIENT_SECRET')


def get_azure_fhir_token():
    """Get Azure AD access token for FHIR API."""
    
    # Use FHIR service URL as audience (Azure Health Data Services pattern)
    # Try both the service-specific audience and the generic healthcare APIs scope
    if AZURE_FHIR_URL:
        # Primary: Use the FHIR service URL as the audience
        fhir_base = AZURE_FHIR_URL.rstrip('/')
        scope = f"{fhir_base}/.default"
    else:
        # Fallback: Generic Azure Healthcare APIs scope
        scope = "https://azurehealthcareapis.com/.default"
    
    try:
        # Use service principal if credentials provided
        if AZURE_TENANT_ID and AZURE_CLIENT_ID and AZURE_CLIENT_SECRET:
            print("🔐 Authenticating with Service Principal...")
            credential = ClientSecretCredential(
                tenant_id=AZURE_TENANT_ID,
                client_id=AZURE_CLIENT_ID,
                client_secret=AZURE_CLIENT_SECRET
            )
        else:
            print("🔐 Authenticating with Default Azure Credential...")
            credential = DefaultAzureCredential()
        
        print(f"   Token scope: {scope}")
        token = credential.get_token(scope)
        print(f"✅ Authentication successful")
        return token.token
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure you're logged in: az login")
        print("2. Or set service principal credentials in .env:")
        print("   AZURE_TENANT_ID=...")
        print("   AZURE_CLIENT_ID=...")
        print("   AZURE_CLIENT_SECRET=...")
        return None


def validate_with_azure_fhir(bundle_path, profile=None):
    """Validate a FHIR bundle using Azure FHIR $validate operation."""
    
    if not AZURE_FHIR_URL:
        print("❌ AZURE_FHIR_BASE_URL not set in .env")
        print("   Set to your Azure FHIR service URL:")
        print("   AZURE_FHIR_BASE_URL=https://my-fhir.azurehealthcareapis.com")
        return None
    
    # Load bundle
    bundle_file = Path(bundle_path)
    if not bundle_file.exists():
        print(f"❌ File not found: {bundle_path}")
        return None
    
    with open(bundle_file, 'r', encoding='utf-8') as f:
        bundle_json = f.read()
    
    bundle_data = json.loads(bundle_json)
    resource_type = bundle_data.get('resourceType', 'Unknown')
    
    print(f"\n{'='*70}")
    print(f"🔍 VALIDATING: {bundle_file.name}")
    print(f"{'='*70}")
    print(f"Resource Type: {resource_type}")
    print(f"Size: {len(bundle_json):,} bytes")
    
    if resource_type == 'Bundle':
        entry_count = len(bundle_data.get('entry', []))
        print(f"Entries: {entry_count}")
    
    # Get access token
    access_token = get_azure_fhir_token()
    if not access_token:
        return None
    
    # Prepare validation endpoint
    fhir_base = AZURE_FHIR_URL.rstrip('/')
    
    # Try resource-specific $validate first
    if resource_type:
        validate_url = f"{fhir_base}/{resource_type}/$validate"
    else:
        validate_url = f"{fhir_base}/$validate"
    
    print(f"\n🚀 Validation endpoint: {validate_url}")
    
    if profile:
        print(f"📋 Profile: {profile}")
        validate_url += f"?profile={profile}"
    
    # Prepare request
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/fhir+json',
        'Accept': 'application/fhir+json',
    }
    
    # Submit validation request
    try:
        print("⏳ Submitting to Azure FHIR...")
        response = requests.post(
            validate_url,
            data=bundle_json,
            headers=headers,
            timeout=120
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
                print(f"❌ Bad request: {response.text[:500]}")
                return None
                
        elif response.status_code == 401:
            print("❌ Unauthorized - check your Azure credentials")
            return None
            
        elif response.status_code == 404:
            print("❌ Endpoint not found - verify AZURE_FHIR_URL")
            print(f"   Current: {AZURE_FHIR_URL}")
            return None
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(response.text[:500])
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def parse_operation_outcome(operation_outcome, filename):
    """Parse FHIR OperationOutcome and return structured results."""
    
    if operation_outcome.get('resourceType') != 'OperationOutcome':
        print(f"⚠️  Expected OperationOutcome, got: {operation_outcome.get('resourceType')}")
        return None
    
    issues = operation_outcome.get('issue', [])
    
    result = {
        'filename': filename,
        'total_issues': len(issues),
        'errors': [],
        'warnings': [],
        'information': [],
        'operation_outcome': operation_outcome
    }
    
    for issue in issues:
        severity = issue.get('severity', 'unknown')
        code = issue.get('code', 'unknown')
        diagnostics = issue.get('diagnostics', '')
        location = issue.get('location', [])
        expression = issue.get('expression', [])
        details = issue.get('details', {})
        
        # Extract more detailed information
        details_text = details.get('text', '')
        details_coding = details.get('coding', [])
        
        # Build a cleaner diagnostics message
        clean_diagnostics = diagnostics
        
        # Remove the deprecation noise from diagnostics
        if ' // OperationOutcome.' in diagnostics:
            parts = diagnostics.split(' // OperationOutcome.')
            clean_diagnostics = parts[0]
        
        issue_detail = {
            'severity': severity,
            'code': code,
            'diagnostics': clean_diagnostics,
            'details_text': details_text,
            'details_coding': details_coding,
            'location': location,
            'expression': expression,
            'raw_diagnostics': diagnostics  # Keep original for reference
        }
        
        if severity == 'error':
            result['errors'].append(issue_detail)
        elif severity == 'warning':
            result['warnings'].append(issue_detail)
        else:
            result['information'].append(issue_detail)
    
    return result


def print_validation_results(result):
    """Print validation results in readable format."""
    
    if not result:
        return
    
    print(f"\n{'='*70}")
    print(f"📊 VALIDATION RESULTS: {result['filename']}")
    print(f"{'='*70}")
    
    error_count = len(result['errors'])
    warning_count = len(result['warnings'])
    info_count = len(result['information'])
    
    print(f"\n📈 Summary:")
    print(f"   Total Issues: {result['total_issues']}")
    print(f"   Errors: {error_count}")
    print(f"   Warnings: {warning_count}")
    print(f"   Information: {info_count}")
    
    if error_count == 0:
        print(f"\n✅ VALIDATION PASSED - No errors found!")
    else:
        print(f"\n❌ VALIDATION FAILED - {error_count} error(s) found")
    
    # Print errors
    if result['errors']:
        print(f"\n❌ ERRORS:")
        for i, error in enumerate(result['errors'], 1):
            print(f"\n  {i}. [{error['code']}]")
            print(f"     Message: {error['diagnostics']}")
            if error['location']:
                print(f"     Location: {error['location']}")
            if error['expression']:
                print(f"     Expression: {error['expression']}")
    
    # Print warnings
    if result['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for i, warning in enumerate(result['warnings'], 1):
            print(f"\n  {i}. [{warning['code']}]")
            print(f"     Message: {warning['diagnostics']}")
            if warning['location']:
                print(f"     Location: {warning['location']}")
            if warning['expression']:
                print(f"     Expression: {warning['expression']}")
    
    # Print information (if not too many)
    if info_count > 0 and info_count <= 5:
        print(f"\n💡 INFORMATION:")
        for i, info in enumerate(result['information'], 1):
            print(f"\n  {i}. [{info['code']}]")
            print(f"     Message: {info['diagnostics']}")
    
    # Save detailed results
    results_file = f"azure_validation_{result['filename'].replace('.json', '')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print(f"{'='*70}\n")


def main():
    """Main entry point - validate IPS bundles with Azure FHIR."""
    
    # Default bundles
    bundles = [
        'examples/Diana_Ferreira_bundle.json',
        'examples/Patrick_Murphy_bundle.json',
    ]
    
    # Allow command line override
    if len(sys.argv) > 1:
        bundles = sys.argv[1:]
    
    # Optional profile parameter
    profile = None
    if '--profile' in sys.argv:
        profile_idx = sys.argv.index('--profile')
        if profile_idx + 1 < len(sys.argv):
            profile = sys.argv[profile_idx + 1]
            bundles = [b for b in sys.argv[1:] if b not in ['--profile', profile]]
    
    print("\n" + "="*70)
    print("🩺 AZURE FHIR VALIDATION SERVICE")
    print("="*70)
    print(f"FHIR Endpoint: {AZURE_FHIR_URL or 'NOT SET'}")
    
    if not AZURE_FHIR_URL:
        print("\n❌ Please set AZURE_FHIR_BASE_URL in your .env file")
        print("Example: AZURE_FHIR_BASE_URL=https://my-fhir.azurehealthcareapis.com")
        return 1
    
    results = []
    
    for bundle_path in bundles:
        if not os.path.exists(bundle_path):
            print(f"\n❌ File not found: {bundle_path}")
            continue
        
        result = validate_with_azure_fhir(bundle_path, profile)
        if result:
            results.append(result)
            print_validation_results(result)
    
    # Final summary
    if results:
        print("\n" + "="*70)
        print("📊 VALIDATION SUMMARY")
        print("="*70)
        
        for result in results:
            error_count = len(result['errors'])
            warning_count = len(result['warnings'])
            
            if error_count == 0:
                status = "✅ PASSED"
            else:
                status = f"❌ FAILED ({error_count} errors)"
            
            print(f"{result['filename']}: {status} ({warning_count} warnings)")
        
        print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
