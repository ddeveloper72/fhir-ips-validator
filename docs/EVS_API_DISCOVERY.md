# eHDSI Gazelle EVS API Integration Guide

## Discovery Summary

**Date:** March 28, 2026  
**Platform:** https://gazelle.ehdsi.eu  
**Status:** ✅ Successfully discovered working endpoints

---

## Discovered SOAP Web Service Endpoints

### 1. CDA Document Validation ⭐ PRIMARY

**WSDL Endpoint:**
```
https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl
```

**Available Validators:** 49 validators

#### eHDSI-Specific CDA Validators (Wave 7-9)

These validators are specifically for eHDSI testing across different waves and versions:

**PIVOT CDA (Level 1) - Structure Validation:**
- `eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.1.0)` ← Latest
- `eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.0.0)`
- `eHDSI - PIVOT CDA (L1) validation - Wave 8 (V8.1.0)`
- `eHDSI - PIVOT CDA (L1) validation - Wave 8 (V8.0.0)`
- `eHDSI - PIVOT CDA (L1) validation - Wave 7 (V7.2.0)`
- `eHDSI - PIVOT CDA (L1) validation - Wave 7 (V7.1.0)`

**PIVOT CDA (Level 3) - Full Content Validation:**
- `eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)` ← Latest
- `eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.0.0)`
- `eHDSI - PIVOT CDA (L3) validation - Wave 8 (V8.1.0)`
- `eHDSI - PIVOT CDA (L3) validation - Wave 8 (V8.0.0)`
- `eHDSI - PIVOT CDA (L3) validation - Wave 7 (V7.2.0)`
- `eHDSI - PIVOT CDA (L3) validation - Wave 7 (V7.1.0)`

**FRIENDLY CDA (Level 3) - National Extensions:**
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 9 (V9.1.0)` ← Latest
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 9 (V9.0.0)`
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 8 (V8.1.0)`
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 8 (V8.0.0)`
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 7 (V7.2.0)`
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 7 (V7.1.0)`

#### Other CDA Validators

**HL7 Base Standards:**
- `HL7 - CDA Release 2` - Standard CDA R2 validation
- `HL7 - CDA Release 2 (strict)` - Strict CDA R2 validation
- `HL7 - CCD` - Continuity of Care Document

**epSOS (European Patients Smart Open Services):**
- `epSOS - Patient Summary Pivot`
- `epSOS - Patient Summary Friendly`
- `epSOS - ePrescription Pivot`
- `epSOS - ePrescription Friendly`
- `epSOS - eDispensation Pivot`
- `epSOS - eDispensation Friendly`
- `epSOS - eConsent`
- `epSOS - HCER HealthCare Encounter Report`
- `epSOS - MRO Medication Related Overview`

**IHE Profiles:**
- `IHE - LAB - Sharing Laboratory Reports (XD-LAB) (old version)`
- `IHE - RAD - CDA document wrapper (XDS-I.b)`
- `IHE - ITI - Basic Patient Privacy Consent (BPPC)`
- `IHE - CARD - Cath Report Content (CRC)`
- `IHE - CARD - Registry Content Submission (RCS-C)`
- `IHE - CARD - Registry Content Submission - Electrophysiology (RCS-EP)`
- `IHE - PATH - Anatomic Pathology Structured Reports (APSR)`

**National Extensions:**
- `ASIP - CDA Structuration minimale` (France)
- `ASIP - Fiche de Réunion de Concertation Pluridisciplinaire (FRCP)` (France)
- `LUX - Header Specifications` (Luxembourg)
- `LUX - Body Level1 Specifications` (Luxembourg)
- `KSA - Header Specifications` (Saudi Arabia)
- `KSA - Basic Patient Privacy Consents`
- `KSA - XDS-I.b Displayable Radiology report`
- `KSA - Laboratory Report`
- `KSA - Laboratory Order`
- `KSA - XDS-I.b Basic Structured Radiology report`

**Research/Testing:**
- `EXPAND - CDA documents [informal testing - art-decor based requirements]`

---

### 2. XDS/XDR/XCA Metadata Validation

**WSDL Endpoint:**
```
https://gazelle.ehdsi.eu/XDStarClient-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl
```

**Available Validators:** 83 validators for document sharing metadata

**Key Validator Categories:**
- **IHE XDS.b** (ITI-18, ITI-41, ITI-42, ITI-43, ITI-61, ITI-62)
- **IHE XCA** (ITI-18, ITI-38, ITI-39) - Cross-Community Access
- **IHE XDR** (ITI-41) - Cross-enterprise Document Reliable Interchange
- **IHE XCA-I** (RAD-68, RAD-69, RAD-75) - Imaging Document Source
- **IHE XDS-I.b** (RAD-68, RAD-69) - Imaging Document Source
- **IHE XDM** (ITI-32) - Cross-enterprise Document Media Interchange
- **eHDSI Services:**
  - PatientService (list/retrieve)
  - OrderService (list/retrieve)
  - OrCDService (list/retrieve)
  - DispensationService (initialize/discard)
  - ConsentService (put/discard)
  - ProvideDataService

---

### 3. ATNA Audit Message Validation

**WSDL Endpoint:**
```
https://gazelle.ehdsi.eu/gazelle-atna-ejb/AuditMessageValidationWSService/AuditMessageValidationWS?wsdl
```

**Status:** Accessible but validator list retrieval requires authentication
**Purpose:** Validate IHE ATNA (Audit Trail and Node Authentication) audit messages

---

### 4. SAML Assertion Validation (XUA)

**WSDL Endpoint:**
```
https://gazelle.ehdsi.eu/gazelle-xua-jar/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl
```

**Available Validators:** 12 validators

**Key Validators:**
- `IHE - ITI - XUA` - Base XUA profile
- `IHE - ITI - XUA - Authz-Consent Option`
- `IHE - ITI - XUA - PurposeOfUse Option`
- `IHE - ITI - XUA - Subject-Role Option`
- `IHE - ITI - SeR - ITI-79` - Authorization Decisions Query (Request/Response)
- **eHDSI SAML Assertions:**
  - `eHDSI SAML - HCP Identity Assertion - v1` (Healthcare Professional)
  - `eHDSI SAML - NoK Identity Assertion - v1` (Next of Kin)
  - `eHDSI SAML - TRC Identity Assertion - v1` (Treatment Relationship Confirmation)
- **National Extensions:**
  - `CH - IHE - ITI - XUA` (Switzerland)
  - `IE - IHE - ITI - XUA` (Ireland)
  - `KSA - XUA` (Saudi Arabia)

---

## SOAP Web Service API Methods

All discovered endpoints implement the following standard methods:

### `about()`
Returns information about the validation service.

**Returns:** String with service description

**Example (Python with zeep):**
```python
from zeep import Client

client = Client('https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl')
info = client.service.about()
print(info)
```

---

### `getListOfValidators(discriminator)`
Returns list of available validators for the service.

**Parameters:**
- `discriminator` (string, optional): Filter validators by category (e.g., 'eHDSI', 'IHE', 'epSOS')

**Returns:** List of validator names

**Example:**
```python
from zeep import Client

client = Client('https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl')

# Get all validators
validators = client.service.getListOfValidators()
print(f"Found {len(validators)} validators")

# Filter by discriminator (if supported)
try:
    ehdsi_validators = client.service.getListOfValidators('eHDSI')
    print(f"Found {len(ehdsi_validators)} eHDSI validators")
except:
    pass
```

---

### `validateDocument(document, validator)`
Validates an XML document using the specified validator.

**Parameters:**
- `document` (string): XML document content
- `validator` (string): Name of the validator (must match one from getListOfValidators)

**Returns:** XML structure containing validation results

**Example:**
```python
from zeep import Client

client = Client('https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl')

with open('patient_summary.xml', 'r', encoding='utf-8') as f:
    xml_content = f.read()

result = client.service.validateDocument(
    document=xml_content,
    validator='eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)'
)

print(result)
```

---

### `validateBase64Document(base64Document, validator)`
Validates a base64-encoded XML document using the specified validator.

**Parameters:**
- `base64Document` (string): Base64-encoded XML document
- `validator` (string): Name of the validator

**Returns:** XML structure containing validation results

**Example:**
```python
import base64
from zeep import Client

client = Client('https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl')

with open('patient_summary.xml', 'rb') as f:
    xml_bytes = f.read()
    base64_content = base64.b64encode(xml_bytes).decode('utf-8')

result = client.service.validateBase64Document(
    base64Document=base64_content,
    validator='eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)'
)

print(result)
```

---

## FHIR to CDA Validation Workflow

Since the eHDSI platform validates CDA documents (not FHIR directly), you'll need to:

1. **Convert FHIR to CDA** (if not already CDA)
   - Use FHIR-to-CDA transformation tools
   - Or validate FHIR IPS as-is if targeting IPS validators

2. **Determine Appropriate Validator**
   - For Patient Summaries: Use `eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)`
   - For Prescriptions: Use `epSOS - ePrescription Pivot`
   - For Dispensations: Use `epSOS - eDispensation Pivot`

3. **Submit for Validation**
   ```python
   # Example workflow
   from zeep import Client
   
   # Initialize client
   wsdl = 'https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
   client = Client(wsdl)
   
   # Read CDA document
   with open('patient_summary_cda.xml', 'r') as f:
       cda_content = f.read()
   
   # Validate
   result = client.service.validateDocument(
       document=cda_content,
       validator='eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)'
   )
   
   # Parse results
   print(result)
   ```

---

## Recommended Validators for FHIR IPS Bundles

Your Diana Ferreira and Patrick Murphy IPS bundles should be validated against:

### Primary Validator
- **`eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)`** - Latest comprehensive validation

### Alternative Validators (by wave)
- `eHDSI - PIVOT CDA (L3) validation - Wave 8 (V8.1.0)` - Previous wave
- `eHDSI - FRIENDLY CDA (L3) validation - Wave 9 (V9.1.0)` - If using national extensions

### Structure-Only Validation (lighter)
- `eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.1.0)` - Structure without full content validation

---

## Authentication

Based on the discovery, most validation services appear to be:
1. **Publicly accessible** for basic validation queries
2. **May require API key** for advanced features or rate-limited access

Your API key from `.env`:
```
EVS_API_KEY=your_api_key_here
```

**Note:** SOAP web services may not use the API key the same way REST APIs do. Further testing needed to determine if/how API keys are passed in SOAP headers.

---

## Next Steps

1. **✅ Update `src/validator/api_client.py`** to use discovered WSDL endpoint
2. **✅ Implement validator selection** logic for eHDSI profiles
3. **✅ Create test script** to validate FHIR examples
4. **Test with your IPS bundles** (Diana Ferreira, Patrick Murphy)
5. **Implement FHIR → CDA conversion** (if needed)
6. **Parse XML validation responses** into structured reports

---

## References

- **Discovery Results:** `evs_discovery_results.json`
- **eHDSI EVS Portal:** https://gazelle.ehdsi.eu/evs/home.seam
- **EVS Documentation:** https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html
- **CDA Generator Docs:** https://gazelle.ehdsi.eu/gazelle-documentation/CDA-Generator/user.html
- **Your API Key Created:** 3/28/26 8:45:00 AM (CET)
- **API Key Expires:** 4/27/26 12:00:00 AM (CEST)

---

## Comparison with HL7_v2 Project

| Aspect | HL7_v2 Project | FHIR Validator Project |
|--------|----------------|----------------------|
| **Platform** | testing.ehealthireland.ie | gazelle.ehdsi.eu |
| **API Type** | REST API | SOAP Web Services (WSDL) |
| **Authentication** | GazelleAPIKey header | TBD (may not require for basic validation) |
| **Endpoint Discovery** | Trial and error | WSDL introspection + getListOfValidators() |
| **Document Format** | HL7 v2.x messages (XML) | CDA documents (XML) |
| **Validators Found** | 3 (manually discovered) | 49+ (CDA), 83+ (XDS), 12+ (SAML) |
| **Primary Use Case** | HL7 v2 messages validation | CDA/eHDSI document validation |
