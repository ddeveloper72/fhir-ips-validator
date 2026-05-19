# Azure FHIR Validation Guide

## Why Azure FHIR is Better Than Gazelle for Validation

### ✅ Azure FHIR Advantages

1. **Full REST API Support**
   - Standard FHIR `$validate` operation
   - Programmatic access with authentication
   - Production-ready, scalable infrastructure

2. **Better Reliability**
   - Azure SLA (99.9% uptime)
   - Better than public HAPI FHIR (frequent downtime)
   - Enterprise-grade infrastructure

3. **Integration with Your Workflow**
   - Already part of your Azure environment
   - Use existing Azure authentication
   - Can integrate with CI/CD pipelines

4. **Comprehensive Validation**
   - OperationOutcome responses with detailed issues
   - Profile validation support
   - Terminology validation

### ❌ Gazelle Limitations

1. **No REST API** - Web UI only (JSF/RichFaces legacy architecture)
2. **Manual validation** - Cannot automate testing
3. **Session-based** - Requires browser interaction
4. **Free service** - Limited resources, no SLA

---

## Setup: Azure FHIR Validation

### 1. Prerequisites

Install Azure Identity library:
```bash
pip install azure-identity
```

### 2. Configure Environment

Add to `.env`:
```env
# Your Azure FHIR Service URL
AZURE_FHIR_URL=https://my-fhir-service.azurehealthcareapis.com

# Option A: Use Default Azure Credential (az login)
# No additional config needed - will use your Azure CLI login

# Option B: Use Service Principal
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
```

### 3. Azure Authentication Options

**Option A: Interactive Login (Recommended for Development)**
```bash
az login
```
The script will use your Azure CLI credentials automatically.

**Option B: Service Principal (Recommended for CI/CD)**
```bash
# Create service principal
az ad sp create-for-rbac --name "fhir-validator" --role "FHIR Data Contributor" --scopes /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.HealthcareApis/services/{fhir-service}

# Use output values in .env
```

### 4. Grant FHIR Permissions

Your identity needs **"FHIR Data Contributor"** or **"FHIR Data Reader"** role:

```bash
# Get your user object ID
az ad signed-in-user show --query id -o tsv

# Assign FHIR Data Contributor role
az role assignment create \
  --role "FHIR Data Contributor" \
  --assignee {user-object-id} \
  --scope /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.HealthcareApis/services/{fhir-service}
```

---

## Usage

### Validate Single Bundle

```bash
python scripts/validate_with_azure_fhir.py examples/Diana_Ferreira_bundle.json
```

### Validate Both IPS Bundles

```bash
python scripts/validate_with_azure_fhir.py
```

### Validate with Specific Profile

```bash
python scripts/validate_with_azure_fhir.py examples/Diana_Ferreira_bundle.json --profile http://hl7.org/fhir/uv/ips/StructureDefinition/Bundle-uv-ips
```

---

## Expected Output

```
======================================================================
🩺 AZURE FHIR VALIDATION SERVICE
======================================================================
FHIR Endpoint: https://my-fhir.azurehealthcareapis.com

======================================================================
🔍 VALIDATING: Diana_Ferreira_bundle.json
======================================================================
Resource Type: Bundle
Size: 86,579 bytes
Entries: 44

🔐 Authenticating with Default Azure Credential...
✅ Authentication successful

🚀 Validation endpoint: https://my-fhir.azurehealthcareapis.com/Bundle/$validate
⏳ Submitting to Azure FHIR...
📥 Response: 200

======================================================================
📊 VALIDATION RESULTS: Diana_Ferreira_bundle.json
======================================================================

📈 Summary:
   Total Issues: 2
   Errors: 0
   Warnings: 2
   Information: 0

✅ VALIDATION PASSED - No errors found!

⚠️  WARNINGS:

  1. [business-rule]
     Message: Patient.contact.name: minimum required = 1, but only found 0
     Location: Bundle.entry[0].resource.contact[0].name

  2. [incomplete]
     Message: Reference to Organization/hospital-001 could not be resolved
     Location: Bundle.entry[23].resource.managingOrganization

💾 Detailed results saved to: azure_validation_Diana_Ferreira_bundle.json
======================================================================
```

---

## Common Issues & Solutions

### Issue 1: "Unauthorized" Error

**Cause:** Missing FHIR permissions

**Solution:**
```bash
# Check your current role assignments
az role assignment list --scope /subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.HealthcareApis/services/{fhir}

# Add FHIR Data Contributor role
az role assignment create --role "FHIR Data Contributor" --assignee {object-id} --scope {fhir-resource-id}
```

### Issue 2: "Not Found" (404)

**Cause:** Incorrect AZURE_FHIR_URL

**Solution:**
```bash
# Get your FHIR service URL
az healthcareapis service show --resource-group {rg} --name {fhir-service} --query "properties.authenticationConfiguration.audience" -o tsv

# Expected format: https://{fhir-service}.azurehealthcareapis.com
```

### Issue 3: Authentication Timeout

**Cause:** Not logged in with Azure CLI

**Solution:**
```bash
az login
az account set --subscription {subscription-id}
```

### Issue 4: "$validate not supported"

**Cause:** Using Azure API for FHIR (older service)

**Solution:**
Azure API for FHIR supports `$validate` but may have limitations. Consider upgrading to **Azure Health Data Services FHIR service** (newer, better API support).

---

## Azure FHIR vs Other Validators

| Feature | Azure FHIR | Gazelle | HAPI FHIR (Public) | Local HAPI |
|---------|-----------|---------|-------------------|------------|
| **REST API** | ✅ Yes | ❌ No | ✅ Yes | ✅ Yes |
| **Reliability** | ✅ 99.9% SLA | ⚠️ No SLA | ❌ Frequent downtime | ✅ You control |
| **Authentication** | ✅ Azure AD | 🔓 None/API Key | 🔓 Often open | ✅ You control |
| **Profile Support** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Terminology** | ✅ Built-in | ✅ Built-in | ⚠️ Limited | ⚠️ Manual setup |
| **Cost** | 💰 Paid | ✅ Free | ✅ Free | 💻 Self-hosted |
| **Integration** | ✅ Azure ecosystem | ❌ Manual | ❌ Manual | ✅ Full control |

---

## Recommended Validation Strategy

### Development Workflow

1. **Local validation** with HL7 FHIR Validator (fast, offline)
   ```bash
   java -jar validator.jar bundle.json -version 4.0.1 -ig hl7.fhir.uv.ips
   ```

2. **Azure FHIR validation** (integrated, reliable)
   ```bash
   python scripts/validate_with_azure_fhir.py bundle.json
   ```

3. **Gazelle validation** (certification/conformance testing only)
   - Manual web UI validation
   - For official testing/certification

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Validate FHIR Resources
  run: |
    pip install azure-identity requests python-dotenv
    python scripts/validate_with_azure_fhir.py examples/*.json
  env:
    AZURE_FHIR_URL: ${{ secrets.AZURE_FHIR_URL }}
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
```

---

## Next Steps

1. **Update your environment:**
   ```bash
   # Add to .env
   echo "AZURE_FHIR_URL=https://your-fhir.azurehealthcareapis.com" >> .env
   
   # Install dependency
   pip install azure-identity
   
   # Update requirements.txt
   echo "azure-identity>=1.16.0" >> requirements.txt
   ```

2. **Test validation:**
   ```bash
   python scripts/validate_with_azure_fhir.py examples/Diana_Ferreira_bundle.json
   ```

3. **Review results:**
   - Check console output for errors/warnings
   - Review detailed JSON results file
   - Address any validation issues

4. **Integrate into workflow:**
   - Add to test suite
   - Integrate with CI/CD
   - Use for continuous validation

---

## References

- **Azure FHIR Service:** https://learn.microsoft.com/azure/healthcare-apis/fhir/
- **FHIR $validate Operation:** http://hl7.org/fhir/R4/resource-operation-validate.html
- **Azure Identity:** https://learn.microsoft.com/python/api/azure-identity/
- **IPS Implementation Guide:** http://hl7.org/fhir/uv/ips/

---

*You already have Azure FHIR - use it! It's more reliable and automation-friendly than Gazelle.*
