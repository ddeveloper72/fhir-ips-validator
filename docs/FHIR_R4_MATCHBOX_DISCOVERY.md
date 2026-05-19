# FHIR R4 Matchbox Validation Discovery

## Overview

eHDSI Gazelle platform uses **Matchbox** (a FHIR validation engine) to provide FHIR R4 validation services. This document summarizes the discovery findings for integrating with Matchbox on the eHDSI platform.

**Discovery Date:** 2026-03-28  
**Base URL:** https://gazelle.ehdsi.eu  
**Web UI:** https://gazelle.ehdsi.eu/evs/default/validator.seam?standard=28  
**Discovered Validators:** 527 FHIR R4 StructureDefinitions

---

## Key Findings

### ✅ What Was Discovered

1. **527 FHIR R4 StructureDefinitions** available for validation
   - All core FHIR R4 resources (Patient, Bundle, Composition, Observation, etc.)
   - Extended profiles (vitalsigns, bodyweight, bp, etc.)
   - IPS-relevant resources and profiles

2. **Web UI Access**
   - Validator page: https://gazelle.ehdsi.eu/evs/default/validator.seam?standard=28
   - Shows "FHIR R4 Core validations" with validation logs
   - Form-based upload interface for FHIR resources

3. **IPS Bundle Support**
   - Our test IPS bundles (Diana Ferreira, Patrick Murphy) contain resources that match available validators
   - No CDA conversion needed - direct FHIR validation possible

### ❌ What Was NOT Found

1. **No Working REST API Endpoint**
   - Tested endpoints all returned 404:
     - `https://gazelle.ehdsi.eu/matchbox`
     - `https://gazelle.ehdsi.eu/matchbox/fhir`
     - `https://gazelle.ehdsi.eu/matchbox/fhir/r4`
     - `https://gazelle.ehdsi.eu/fhir/r4`
     - `https://gazelle.ehdsi.eu/evs/fhir`
     - `https://gazelle.ehdsi.eu/evs/fhir/r4`

2. **No FHIR Metadata Endpoint**
   - Standard FHIR endpoints (`/metadata`, `/$validate`) not accessible
   - CapabilityStatement not available via REST

3. **Validation API Pattern Unclear**
   - May require session-based authentication
   - May only be accessible via web form submission
   - May use non-standard FHIR REST patterns

---

## Discovered FHIR R4 Validators

### Core IPS Resources

The following core IPS resources are available for validation:

| Resource Type | StructureDefinition URL |
|--------------|-------------------------|
| **Patient** | `http://hl7.org/fhir/StructureDefinition/Patient` |
| **Bundle** | `http://hl7.org/fhir/StructureDefinition/Bundle` |
| **Composition** | `http://hl7.org/fhir/StructureDefinition/Composition` |
| **Observation** | `http://hl7.org/fhir/StructureDefinition/Observation` |
| **Condition** | `http://hl7.org/fhir/StructureDefinition/Condition` |
| **MedicationStatement** | `http://hl7.org/fhir/StructureDefinition/MedicationStatement` |
| **AllergyIntolerance** | `http://hl7.org/fhir/StructureDefinition/AllergyIntolerance` |
| **Procedure** | `http://hl7.org/fhir/StructureDefinition/Procedure` |
| **Immunization** | `http://hl7.org/fhir/StructureDefinition/Immunization` |
| **AuditEvent** | `http://hl7.org/fhir/StructureDefinition/AuditEvent` |

### Vital Signs Profiles

Extended observation profiles for vital signs:

- `http://hl7.org/fhir/StructureDefinition/vitalsigns` - Base vital signs profile
- `http://hl7.org/fhir/StructureDefinition/bp` - Blood pressure
- `http://hl7.org/fhir/StructureDefinition/bodyweight` - Body weight
- `http://hl7.org/fhir/StructureDefinition/bodyheight` - Body height
- `http://hl7.org/fhir/StructureDefinition/bodytemp` - Body temperature
- `http://hl7.org/fhir/StructureDefinition/heartrate` - Heart rate
- `http://hl7.org/fhir/StructureDefinition/resprate` - Respiratory rate
- `http://hl7.org/fhir/StructureDefinition/oxygensat` - Oxygen saturation
- `http://hl7.org/fhir/StructureDefinition/bmi` - Body mass index
- `http://hl7.org/fhir/StructureDefinition/headcircum` - Head circumference

### Laboratory Profiles

- `http://hl7.org/fhir/StructureDefinition/cholesterol` - Cholesterol
- `http://hl7.org/fhir/StructureDefinition/hdlcholesterol` - HDL cholesterol
- `http://hl7.org/fhir/StructureDefinition/ldlcholesterol` - LDL cholesterol
- `http://hl7.org/fhir/StructureDefinition/triglyceride` - Triglyceride
- `http://hl7.org/fhir/StructureDefinition/lipidprofile` - Lipid profile

### Clinical Document Profiles

- `http://hl7.org/fhir/StructureDefinition/clinicaldocument` - Clinical document
- `http://hl7.org/fhir/StructureDefinition/example-composition` - Example composition
- `http://hl7.org/fhir/StructureDefinition/example-section-library` - Example section library

### Genetics Profiles

- `http://hl7.org/fhir/StructureDefinition/observation-genetics` - Genetics observation
- `http://hl7.org/fhir/StructureDefinition/diagnosticreport-genetics` - Genetics diagnostic report
- `http://hl7.org/fhir/StructureDefinition/familymemberhistory-genetic` - Genetic family member history
- `http://hl7.org/fhir/StructureDefinition/servicerequest-genetics` - Genetics service request
- `http://hl7.org/fhir/StructureDefinition/hlaresult` - HLA result

### All 527 Validators

See `fhir_r4_discovery_results.json` for the complete list of all 527 discovered StructureDefinitions.

---

## Integration Approaches

### Option 1: Web UI Form Submission (Recommended for Testing)

**Pros:**
- Known to work (visible in screenshot)
- No API endpoint discovery needed
- Can test immediately

**Cons:**
- Requires HTTP session management
- Form parsing and CSRF token handling
- Not ideal for automation

**Implementation:**
1. Start authenticated session with EVS_API_KEY
2. GET the validator page to extract form parameters
3. POST FHIR resource to form endpoint
4. Parse HTML response for validation results

### Option 2: REST API Discovery (If Available)

**Status:** Not yet found

**Next Steps:**
1. Inspect network traffic in browser when using web UI
2. Check for hidden API endpoints in JavaScript
3. Contact eHDSI support for API documentation
4. Look for Matchbox-specific endpoints in EVS documentation

### Option 3: Alternative Platforms

**EHDS Platform:** https://ehds.gazelle-platform.net
- Our IPS bundles already validated successfully here
- May have different API access patterns
- Could be used as reference implementation

---

## Testing Our IPS Bundles

### Test Files Available

1. **Diana Ferreira IPS Bundle** (`examples/Diana_Ferreira_bundle.json`)
   - Comprehensive 15-section IPS
   - Portuguese patient
   - ~22KB, 36 entries
   - ✅ Validated on EHDS platform

2. **Patrick Murphy IPS Bundle** (`examples/Patrick_Murphy_bundle.json`)
   - Focused 4-section IPS
   - Irish patient
   - ~7KB, 9 entries
   - ✅ Validated on EHDS platform

### Validation Strategy

1. **Phase 1:** Test via web UI form submission
   - Validate both IPS bundles
   - Document any eHDSI-specific validation errors
   - Compare results with EHDS platform

2. **Phase 2:** Discover REST API (if available)
   - Monitor network traffic during web UI submission
   - Test discovered endpoint with API key
   - Create automated validation script

3. **Phase 3:** Profile-specific validation
   - Test individual resources against specific profiles
   - Validate against IPS-specific StructureDefinitions (if available)
   - Test custom profiles

---

## Comparison: CDA vs FHIR R4 Validation

| Aspect | CDA Validation (SOAP) | FHIR R4 Validation (Matchbox) |
|--------|----------------------|-------------------------------|
| **Protocol** | SOAP/WSDL | REST/HTTP (expected) |
| **Endpoint** | ✅ Found (WSDL accessible) | ❌ Not found (404 on all endpoints) |
| **Validators** | 49 CDA validators | 527 FHIR StructureDefinitions |
| **Our Data Format** | ❌ Would need conversion | ✅ Already FHIR format |
| **Web UI** | Available | ✅ Accessible |
| **Use Case** | CDA document validation | ⭐ IPS bundle validation (preferred) |

**Decision:** Focus on FHIR R4 Matchbox validation (no conversion needed, matches our data format).

---

## Next Steps

### Immediate (Testing)

1. ✅ Discovery completed (527 validators found)
2. ⏳ Create web UI form submission script
3. ⏳ Test Diana Ferreira IPS bundle
4. ⏳ Test Patrick Murphy IPS bundle
5. ⏳ Document validation results

### Short-term (API Access)

1. Inspect browser network traffic during validation
2. Reverse-engineer form submission endpoint
3. Test with Python requests + sessions
4. Create automated validation script

### Long-term (Production Integration)

1. Contact eHDSI support for official API documentation
2. Request Matchbox REST API access
3. Implement OperationOutcome parsing
4. Add to `api_client.py` module

---

## References

- **eHDSI Validator Page:** https://gazelle.ehdsi.eu/evs/default/validator.seam?standard=28
- **Matchbox Project:** https://github.com/ahdis/matchbox
- **FHIR R4 Specification:** http://hl7.org/fhir/R4/
- **IPS Implementation Guide:** http://hl7.org/fhir/uv/ips/
- **Discovery Script:** `scripts/discover_fhir_r4_validators.py`
- **Discovery Results:** `fhir_r4_discovery_results.json` (527 validators)

---

## Validator Page Structure

The web UI shows:
- Standard selection dropdown (FHIR R4)
- File upload field for FHIR resources
- Validation log display
- Historical validations list

### Example Validation Workflow

```
1. User navigates to validator page
2. Selects "FHIR R4" standard (standard=28)
3. Uploads FHIR resource (JSON or XML)
4. Clicks "Validate"
5. Server processes with Matchbox
6. Returns OperationOutcome
7. Displays validation results
```

---

## Technical Notes

### Session Management

The eHDSI platform uses:
- JSESSIONID cookies
- Form-based authentication
- CSRF tokens (likely)
- EVS_API_KEY header or parameter

### Expected Response Format

Matchbox validation should return a FHIR **OperationOutcome** resource:

```json
{
  "resourceType": "OperationOutcome",
  "issue": [
    {
      "severity": "error" | "warning" | "information",
      "code": "invalid" | "structure" | ...,
      "diagnostics": "Human-readable message",
      "location": ["FHIRPath expression"]
    }
  ]
}
```

### HTTP Client Requirements

```python
import requests
from requests.sessions import Session

# Maintain session for cookies
session = Session()
session.headers.update({
    'Authorization': f'Bearer {EVS_API_KEY}',
    'Accept': 'application/json, text/html',
    'Content-Type': 'multipart/form-data'  # for file upload
})
```

---

## Conclusion

The eHDSI platform provides **comprehensive FHIR R4 validation** via Matchbox with 527 available StructureDefinitions, including all resources needed for IPS bundle validation. While direct REST API access was not found, the web UI is accessible and can be used for validation via form submission.

**Our IPS bundles (Diana Ferreira, Patrick Murphy) are ready for validation** without any conversion - they are already in FHIR format and match the available validators.

Next priority: Create a script to submit validation requests via the web UI form, then test both IPS bundles.
