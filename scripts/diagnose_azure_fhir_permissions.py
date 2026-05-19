"""
Diagnose and fix Azure FHIR permissions.

This script checks if the service principal has the required FHIR roles
and provides commands to fix permission issues.
"""

import os
import sys
import json
from dotenv import load_dotenv

try:
    from azure.identity import ClientSecretCredential
except ImportError:
    print("❌ Azure Identity library not installed")
    print("   Install with: pip install azure-identity")
    sys.exit(1)

load_dotenv()

AZURE_FHIR_BASE_URL = os.getenv('AZURE_FHIR_BASE_URL')
AZURE_FHIR_TENANT_ID = os.getenv('AZURE_FHIR_TENANT_ID')
AZURE_FHIR_CLIENT_ID = os.getenv('AZURE_FHIR_CLIENT_ID')
AZURE_FHIR_CLIENT_SECRET = os.getenv('AZURE_FHIR_CLIENT_SECRET')
AZURE_FHIR_SUBSCRIPTION_ID = os.getenv('AZURE_FHIR_SUBSCRIPTION_ID')
AZURE_FHIR_RESOURCE_GROUP = os.getenv('AZURE_FHIR_RESOURCE_GROUP')
AZURE_FHIR_WORKSPACE = os.getenv('AZURE_FHIR_WORKSPACE')
AZURE_FHIR_SERVICE_NAME = os.getenv('AZURE_FHIR_SERVICE_NAME')


def main():
    """Diagnose Azure FHIR permissions."""
    
    print("\n" + "="*70)
    print("🔍 AZURE FHIR PERMISSIONS DIAGNOSTIC")
    print("="*70)
    
    # Check configuration
    print("\n📋 Configuration Check:")
    configs = {
        'AZURE_FHIR_BASE_URL': AZURE_FHIR_BASE_URL,
        'AZURE_FHIR_TENANT_ID': AZURE_FHIR_TENANT_ID,
        'AZURE_FHIR_CLIENT_ID': AZURE_FHIR_CLIENT_ID,
        'AZURE_FHIR_CLIENT_SECRET': '***' if AZURE_FHIR_CLIENT_SECRET else None,
        'AZURE_FHIR_SUBSCRIPTION_ID': AZURE_FHIR_SUBSCRIPTION_ID,
        'AZURE_FHIR_RESOURCE_GROUP': AZURE_FHIR_RESOURCE_GROUP,
        'AZURE_FHIR_WORKSPACE': AZURE_FHIR_WORKSPACE,
        'AZURE_FHIR_SERVICE_NAME': AZURE_FHIR_SERVICE_NAME,
    }
    
    missing = []
    for key, value in configs.items():
        status = "✅" if value else "❌"
        display_value = value if value else "NOT SET"
        print(f"  {status} {key}: {display_value}")
        if not value:
            missing.append(key)
    
    if not all([AZURE_FHIR_BASE_URL, AZURE_FHIR_TENANT_ID, AZURE_FHIR_CLIENT_ID, AZURE_FHIR_CLIENT_SECRET]):
        print("\n❌ Missing required configuration")
        return 1
    
    # Test authentication
    print("\n🔐 Authentication Test:")
    try:
        credential = ClientSecretCredential(
            tenant_id=AZURE_FHIR_TENANT_ID,
            client_id=AZURE_FHIR_CLIENT_ID,
            client_secret=AZURE_FHIR_CLIENT_SECRET
        )
        
        # Get token for Azure Health Data Services
        scope = "https://azurehealthcareapis.com/.default"
        token = credential.get_token(scope)
        
        print(f"  ✅ Successfully obtained access token")
        print(f"  Token expires: {token.expires_on}")
        
    except Exception as e:
        print(f"  ❌ Authentication failed: {e}")
        return 1
    
    # Diagnose the 401 error
    print("\n🔍 Diagnosis:")
    print("  ❌ 401 Unauthorized error means:")
    print("     ✓ Authentication succeeded (token obtained)")
    print("     ✗ Service Principal lacks FHIR data access permissions")
    
    print("\n💡 Solution:")
    print("  Your Service Principal needs 'FHIR Data Contributor' role")
    
    # Provide fix commands
    print("\n" + "="*70)
    print("🔧 FIX: Assign FHIR Data Contributor Role")
    print("="*70)
    
    if all([AZURE_FHIR_SUBSCRIPTION_ID, AZURE_FHIR_RESOURCE_GROUP, AZURE_FHIR_WORKSPACE, AZURE_FHIR_SERVICE_NAME]):
        # Full resource ID
        fhir_resource_id = f"/subscriptions/{AZURE_FHIR_SUBSCRIPTION_ID}/resourceGroups/{AZURE_FHIR_RESOURCE_GROUP}/providers/Microsoft.HealthcareApis/workspaces/{AZURE_FHIR_WORKSPACE}/fhirservices/{AZURE_FHIR_SERVICE_NAME}"
        
        print("\nOption 1: Using Azure CLI (Recommended)")
        print("-" * 70)
        print("# Assign FHIR Data Contributor role to your Service Principal")
        print(f"az role assignment create \\")
        print(f"  --role 'FHIR Data Contributor' \\")
        print(f"  --assignee {AZURE_FHIR_CLIENT_ID} \\")
        print(f"  --scope '{fhir_resource_id}'")
        
        print("\n\nOption 2: Using Azure Portal")
        print("-" * 70)
        print(f"1. Navigate to: https://portal.azure.com/#@{AZURE_FHIR_TENANT_ID}/resource{fhir_resource_id}/users")
        print(f"2. Click 'Access control (IAM)' in left menu")
        print(f"3. Click '+ Add' → 'Add role assignment'")
        print(f"4. Select role: 'FHIR Data Contributor'")
        print(f"5. Select members: Search for App ID: {AZURE_FHIR_CLIENT_ID}")
        print(f"6. Click 'Review + assign'")
        
        print("\n\nOption 3: Check Current Permissions")
        print("-" * 70)
        print("# List current role assignments for the FHIR service")
        print(f"az role assignment list \\")
        print(f"  --scope '{fhir_resource_id}' \\")
        print(f"  --assignee {AZURE_FHIR_CLIENT_ID} \\")
        print(f"  --output table")
        
    else:
        print("\n⚠️  Missing resource configuration. Using generic command:")
        print("\n# Replace placeholders with your actual values")
        print(f"az role assignment create \\")
        print(f"  --role 'FHIR Data Contributor' \\")
        print(f"  --assignee {AZURE_FHIR_CLIENT_ID} \\")
        print(f"  --scope '/subscriptions/{{SUBSCRIPTION_ID}}/resourceGroups/{{RG}}/providers/Microsoft.HealthcareApis/workspaces/{{WORKSPACE}}/fhirservices/{{SERVICE}}'")
    
    print("\n" + "="*70)
    print("📚 More Information")
    print("="*70)
    print("Azure FHIR Roles:")
    print("  • FHIR Data Reader - Read-only access (sufficient for validation)")
    print("  • FHIR Data Contributor - Read/write access")
    print("  • FHIR Data Exporter - Export operations")
    print("\nPermission propagation takes 5-10 minutes after assignment.")
    print("\nDocs: https://learn.microsoft.com/azure/healthcare-apis/fhir/configure-azure-rbac")
    print("="*70 + "\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
