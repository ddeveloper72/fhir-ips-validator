# EHDS Gazelle Platform Integration Guide

## Overview

The **EHDS Gazelle Platform** (https://ehds.gazelle-platform.net/) is a newer validation platform that complements the original eHDSI Gazelle (https://gazelle.ehdsi.eu/). It provides validators specifically for:

- **International Patient Summary (IPS)** - HL7 FHIR standard
- **HL7 EU Patient Summary (EU-EPS)** - European adaptation of IPS  
- **HL7 EU Base and Core** - Foundational EU healthcare standards

---

## Key Differences from eHDSI Gazelle

| Feature | eHDSI Gazelle | EHDS Gazelle |
|---------|---------------|--------------|
| **URL** | gazelle.ehdsi.eu | ehds.gazelle-platform.net |
| **Focus** | Cross-border eHealth (eHDSI Wave 7-10) | Modern HL7 EU standards |
| **CDA Support** | ✅ Primary focus | ✅ Supported |
| **FHIR Support** | ⚠️ Limited | ✅ Primary focus |
| **API Access** | SOAP/WSDL | REST API + Web UI |
| **Authentication** | API Key | API Key + Session Auth |

---

## API Configuration

### Environment Variables (.env)

```bash
# EHDS Gazelle Platform
EHDS_GAZELLE_BASE_URL=https://ehds.gazelle-platform.net
EHDS_GAZELLE_API_KEY=your_api_key_here
EHDS_GAZELLE_API_KEY_CREATION_DATE=5/17/26 5:12:34 PM (CEST GMT+0200)
EHDS_GAZELLE_API_KEY_EXPIRY_DATE=6/16/26 12:00:00 AM (CEST GMT+0200)

# Original eHDSI Gazelle (keep both for compatibility)
EVS_BASE_URL=https://gazelle.ehdsi.eu
EVS_API_KEY=your_original_key_here
```

### Getting an API Key

1. **Register:** https://ehds.gazelle-platform.net/gazelle/user-management/registration
2. **Login:** https://ehds.gazelle-platform.net/
3. **Generate Key:** https://ehds.gazelle-platform.net/evs/administration/apiKeyManagement.seam
4. **Copy key** to your `.env` file

---

## Available Validator Standards

### Standard 12: International Patient Summary (IPS)

**URL:** https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=12

**Purpose:** Validate HL7 FHIR International Patient Summary documents

**Formats:**
- ✅ FHIR R4 Bundle (IPS profile)
- ✅ CDA R2 (IPS-based)

**Use Cases:**
- Global interoperability
- Cross-border patient summaries
- International healthcare data exchange

**Example Documents:**
- `examples/Diana_Ferreira_bundle.json` (FHIR IPS)
- `examples/Patrick_Murphy_bundle.json` (FHIR IPS)

**Validation Command:**
```bash
# Via web UI
curl -X POST "https://ehds.gazelle-platform.net/evs/api/validate" \
  -H "X-API-Key: $EHDS_GAZELLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/Diana_Ferreira_bundle.json \
  --data-urlencode "standard=12"
```

---

### Standard 15: HL7 EU - Patient Summary (EU-EPS)

**URL:** https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=15

**Purpose:** Validate HL7 EU Patient Summary (European adaptation of IPS)

**Formats:**
- ✅ FHIR R4 EU-EPS profile
- ✅ CDA R2 EU-EPS

**Key Differences from IPS:**
- EU-specific terminology bindings
- Additional EU regulatory requirements
- EHDS compliance features
- Member state extensions

**Use Cases:**
- European Health Data Space (EHDS) compliance
- EU cross-border healthcare
- MyHealth@EU infrastructure
- National Contact Point implementations

**Validation Command:**
```bash
# Example for EU-EPS validation
curl -X POST "https://ehds.gazelle-platform.net/evs/api/validate" \
  -H "X-API-Key: $EHDS_GAZELLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/eu_patient_summary.json \
  --data-urlencode "standard=15"
```

---

### Standard 17: HL7 EU - Base and Core

**URL:** https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=17

**Purpose:** Validate HL7 EU Base and Core foundational profiles

**Formats:**
- ✅ FHIR R4 (EU Base profiles)

**Covered Profiles:**
- Patient (EU Base Patient)
- Organization (EU Base Organization)
- Practitioner (EU Base Practitioner)
- Condition (EU Base Condition)
- Medication (EU Base Medication)
- Observation (EU Base Observation)

**Use Cases:**
- Building EU-compliant FHIR resources
- Validating individual resource profiles
- Testing EU extensions and terminology
- Development of EU-specific implementations

**Example:**
```bash
# Validate a single Patient resource
curl -X POST "https://ehds.gazelle-platform.net/evs/api/validate" \
  -H "X-API-Key: $EHDS_GAZELLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/eu_base_patient.json \
  --data-urlencode "standard=17"
```

---

## API Integration Approaches

### Option 1: REST API (Preferred)

**Discovery Needed:** The exact REST API endpoints need to be documented by Gazelle. Common patterns:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

EHDS_BASE_URL = os.getenv('EHDS_GAZELLE_BASE_URL')
EHDS_API_KEY = os.getenv('EHDS_GAZELLE_API_KEY')

def validate_with_ehds(document_content, standard_id, format_type='json'):
    """
    Validate document against EHDS Gazelle
    
    Args:
        document_content: JSON or XML content
        standard_id: 12 (IPS), 15 (EU-EPS), 17 (Base)
        format_type: 'json' or 'xml'
    """
    # Try common API endpoint patterns
    possible_endpoints = [
        f"{EHDS_BASE_URL}/evs/api/v1/validate",
        f"{EHDS_BASE_URL}/evs/api/validate",
        f"{EHDS_BASE_URL}/api/evs/validate",
        f"{EHDS_BASE_URL}/api/validate",
    ]
    
    headers = {
        'X-API-Key': EHDS_API_KEY,
        'Content-Type': f'application/{format_type}',
        'Accept': 'application/json'
    }
    
    params = {
        'standard': standard_id
    }
    
    for endpoint in possible_endpoints:
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                params=params,
                data=document_content,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return response.json()
                
        except Exception as e:
            continue
    
    raise Exception("No working API endpoint found")
```

### Option 2: SOAP/WSDL (If Available)

Check if EHDS provides WSDL services similar to eHDSI:

```python
from zeep import Client

# Try common WSDL paths
wsdl_url = f"{EHDS_BASE_URL}/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl"

try:
    client = Client(wsdl_url)
    validators = client.service.getListOfValidators()
    print(f"Found {len(validators)} validators")
except Exception as e:
    print(f"WSDL not available: {e}")
```

### Option 3: Web Automation (Fallback)

If REST/SOAP aren't available, use Selenium or similar:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get(f"{EHDS_BASE_URL}/evs/default/validator.seam?standard=12")

# Login with API key or credentials
# Upload document
# Submit validation
# Parse results
```

---

## Exploration Script Usage

We've created `scripts/explore_ehds_gazelle.py` to discover available endpoints:

### Run Full Exploration

```bash
# Activate virtual environment
.venv\Scripts\activate

# Run explorer
python scripts/explore_ehds_gazelle.py
```

This will:
1. ✅ Check API configuration
2. 🔍 Discover REST API endpoints
3. 🔍 Try SOAP/WSDL services
4. 📋 Explore each standard (12, 15, 17)
5. 💾 Save responses to `logs/ehds_api_exploration/`

### Explore Specific Standard

```bash
# IPS validators
python scripts/explore_ehds_gazelle.py --standard 12

# EU-EPS validators
python scripts/explore_ehds_gazelle.py --standard 15

# EU Base validators
python scripts/explore_ehds_gazelle.py --standard 17
```

### List All Standards

```bash
python scripts/explore_ehds_gazelle.py --list-all
```

### Discover API Endpoints Only

```bash
python scripts/explore_ehds_gazelle.py --discover
```

### Try SOAP/WSDL Discovery

```bash
python scripts/explore_ehds_gazelle.py --soap
```

---

## Expected Validation Response Format

### Success Response

```json
{
  "status": "PASSED",
  "validationDate": "2026-05-17T17:30:00Z",
  "standard": "HL7 EU - Patient Summary (EU-EPS)",
  "standardId": 15,
  "documentType": "FHIR Bundle",
  "profile": "http://hl7.eu/fhir/StructureDefinition/Bundle-eu-ips",
  "results": {
    "errors": [],
    "warnings": [
      {
        "severity": "warning",
        "message": "Optional element recommended but not present",
        "location": "Bundle.entry[2].resource",
        "code": "optional-element"
      }
    ],
    "info": []
  },
  "summary": {
    "errorCount": 0,
    "warningCount": 1,
    "infoCount": 0
  }
}
```

### Error Response

```json
{
  "status": "FAILED",
  "validationDate": "2026-05-17T17:30:00Z",
  "standard": "HL7 EU - Patient Summary (EU-EPS)",
  "standardId": 15,
  "results": {
    "errors": [
      {
        "severity": "error",
        "message": "Required element missing: Patient.identifier",
        "location": "Bundle.entry[0].resource.Patient",
        "code": "required-element",
        "expression": "Patient.identifier.exists()"
      }
    ],
    "warnings": [],
    "info": []
  },
  "summary": {
    "errorCount": 1,
    "warningCount": 0,
    "infoCount": 0
  }
}
```

---

## Integration Roadmap

### Phase 1: Discovery (Current)
- [x] Add EHDS endpoints to `.env`
- [x] Create exploration script
- [ ] Run discovery to find API endpoints
- [ ] Document actual API structure

### Phase 2: Basic Integration
- [ ] Create `validate_with_ehds.py` script
- [ ] Implement REST API calls (if available)
- [ ] Handle authentication (API key + session)
- [ ] Parse validation responses

### Phase 3: Streamlit Integration
- [ ] Add EHDS validator option to UI
- [ ] Create dropdown for standards (12, 15, 17)
- [ ] Display validation results
- [ ] Compare eHDSI vs EHDS results

### Phase 4: Advanced Features
- [ ] Batch validation support
- [ ] Validator auto-selection (IPS → Standard 12)
- [ ] Side-by-side comparison (eHDSI vs EHDS)
- [ ] Validation history and trends

---

## Use Case Examples

### Use Case 1: Validate FHIR IPS Bundle

**Scenario:** You have a FHIR IPS bundle and want to ensure it's valid for international exchange

**Standard:** 12 (IPS)

**Steps:**
1. Load `examples/Diana_Ferreira_bundle.json`
2. Select "EHDS Gazelle" validator
3. Choose "Standard 12: IPS"
4. Submit validation
5. Review results

**Expected Result:** Pass with 0-1 warnings

---

### Use Case 2: Validate EU Patient Summary (FHIR)

**Scenario:** Building an EU-compliant patient summary for MyHealth@EU

**Standard:** 15 (EU-EPS)

**Steps:**
1. Create FHIR bundle with EU-specific profiles
2. Validate against Standard 15
3. Fix EU-specific terminology issues
4. Re-validate until clean

**Expected Result:** Pass with EU extensions validated

---

### Use Case 3: Validate EU Base Resources

**Scenario:** Developing individual FHIR resources for EU implementation

**Standard:** 17 (Base & Core)

**Steps:**
1. Create single Patient resource
2. Validate against Standard 17
3. Ensure EU base profile compliance
4. Test extensions and identifiers

**Expected Result:** Pass with EU base profile requirements met

---

### Use Case 4: Compare IPS vs EU-EPS

**Scenario:** Understanding differences between international and EU standards

**Standards:** 12 (IPS) and 15 (EU-EPS)

**Steps:**
1. Take same clinical content
2. Validate as IPS (Standard 12)
3. Validate as EU-EPS (Standard 15)
4. Compare validation results
5. Identify EU-specific requirements

**Expected Result:** EU-EPS has additional requirements for terminology, identifiers, extensions

---

## Troubleshooting

### API Key Not Working

**Problem:** 401 Unauthorized or 403 Forbidden

**Solutions:**
1. Check key in `.env` matches generated key
2. Verify key hasn't expired (check expiry date)
3. Regenerate key at: https://ehds.gazelle-platform.net/evs/administration/apiKeyManagement.seam
4. Try different auth header formats (X-API-Key vs Authorization Bearer)

### Endpoint Not Found

**Problem:** 404 Not Found on API calls

**Solutions:**
1. Run exploration script to discover actual endpoints
2. Check if web-based authentication is required
3. Contact Gazelle support for API documentation
4. Try SOAP/WSDL approach instead of REST

### Session Authentication Required

**Problem:** Redirects to login page despite API key

**Solutions:**
1. May need to combine API key with session cookies
2. Use Selenium/Playwright for web automation
3. Request API-only access from Gazelle team
4. Use web UI manually for now

---

## Next Steps

1. **Run Exploration Script:**
   ```bash
   .venv\Scripts\activate
   python scripts/explore_ehds_gazelle.py
   ```

2. **Review Discovery Results:**
   - Check `logs/ehds_api_exploration/` for saved responses
   - Identify working API endpoints
   - Document authentication requirements

3. **Implement Validator:**
   - Create `scripts/validate_with_ehds.py`
   - Implement working API pattern
   - Add error handling

4. **Update Streamlit App:**
   - Add "EHDS Gazelle" validator option
   - Create standard selector (12, 15, 17)
   - Integrate validation calls

5. **Document Findings:**
   - Update this guide with actual API structure
   - Add example requests/responses
   - Create comparison table with eHDSI Gazelle

---

## Resources

- **EHDS Gazelle Platform:** https://ehds.gazelle-platform.net/
- **API Key Management:** https://ehds.gazelle-platform.net/evs/administration/apiKeyManagement.seam
- **User Registration:** https://ehds.gazelle-platform.net/gazelle/user-management/registration
- **HL7 EU IG:** http://hl7.eu/fhir/
- **IPS Implementation Guide:** http://hl7.org/fhir/uv/ips/
- **EHDS Regulation:** https://health.ec.europa.eu/ehealth-digital-health-and-care/european-health-data-space_en

---

## Appendix: Validator Standards Comparison

| Feature | Standard 12 (IPS) | Standard 15 (EU-EPS) | Standard 17 (Base) |
|---------|-------------------|----------------------|--------------------|
| **Focus** | International | European | EU Foundational |
| **Scope** | Full PS document | Full PS document | Individual resources |
| **Terminology** | LOINC, SNOMED CT | EU-specific bindings | EU core value sets |
| **Identifiers** | Global systems | EU eHDSI identifiers | EU base identifiers |
| **Extensions** | Minimal | EU regulatory | EU base extensions |
| **Use Case** | Global exchange | EU cross-border | EU development |
| **Strictness** | Moderate | Strict | Moderate |
| **Target Users** | International orgs | EU Member States | EU implementers |
