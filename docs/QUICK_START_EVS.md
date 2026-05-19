# eHDSI Gazelle EVS Integration - Quick Start Guide

## 🎉 Discovery Complete!

We've successfully discovered and documented the eHDSI Gazelle EVS API endpoints and validators.

---

##  Discovered Resources

### Primary Endpoint for CDA Validation

**WSDL:** `https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl`

**Validators Found:** 49 validators including:
- 18 eHDSI-specific validators (Waves 7-9)
- 13 epSOS validators
- Multiple IHE, HL7, and national validators

### Additional Endpoints

- **XDS/XDR/XCA Metadata:** 83 validators for document sharing
- **SAML Assertions (XUA):** 12 validators for identity assertions  
- **ATNA Audit Messages:** Available (authentication required)

---

## 📁 New Files Created

### Documentation
- **[docs/EVS_API_DISCOVERY.md](docs/EVS_API_DISCOVERY.md)** - Comprehensive API discovery guide with all endpoints and validators
- **[docs/QUICK_START_EVS.md](docs/QUICK_START_EVS.md)** - This file

### Scripts
- **[scripts/discover_evs_endpoints.py](scripts/discover_evs_endpoints.py)** - Endpoint discovery tool
- **[scripts/test_evs_validation.py](scripts/test_evs_validation.py)** - Validation testing script

### Results
- **[evs_discovery_results.json](evs_discovery_results.json)** - Machine-readable discovery results

---

## 🚀 Quick Start: Testing Validation

### 1. List Available Validators

```bash
python scripts/test_evs_validation.py --list-validators
```

**Output:** 49 validators from CDA service

### 2. Test Service Connectivity

```bash
python scripts/test_evs_validation.py
```

**Verifies:** Service is accessible and responding

### 3. Validate a CDA Document

```bash
# Using latest eHDSI validator (Wave 9.1.0)
python scripts/test_evs_validation.py \
    --document examples/patient_summary_cda.xml \
    --validator "eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)"

# Using basic CDA R2 validator
python scripts/test_evs_validation.py \
    -d examples/patient_summary_cda.xml \
    -v "HL7 - CDA Release 2"
```

---

## 🔍 Recommended Validators for Your IPS Bundles

Your Diana Ferreira and Patrick Murphy IPS bundles validated successfully on the **EHDS platform** (ehds.gazelle-platform.net).

To validate on **eHDSI platform** (gazelle.ehdsi.eu):

### Option 1: Convert FHIR IPS → CDA
Then validate with:
- `eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)` - Latest comprehensive
- `eHDSI - PIVOT CDA (L1) validation - Wave 9 (V9.1.0)` - Structure only

### Option 2: Use epSOS Validators  
If your documents match epSOS Patient Summary format:
- `epSOS - Patient Summary Pivot`
- `epSOS - Patient Summary Friendly`

---

## 🔄 Comparison: EHDS vs eHDSI Platforms

| Aspect | ehds.gazelle-platform.net | gazelle.ehdsi.eu |
|--------|---------------------------|------------------|
| **Purpose** | European Health Data Space | eHealth Digital Service Infrastructure |
| **Your Access** | ❌ No API key | ✅ Valid API key |
| **API Type** | REST + Web UI | SOAP Web Services (WSDL) |
| **Validators** | IPS validators | CDA, XDS, ATNA, SAML validators |
| **Your Test Results** | ✅ Diana & Patrick passed | ✅ Endpoints discovered |
| **Document Format** | FHIR IPS Bundles | CDA documents (XML) |

**Key Insight:** The two platforms serve different purposes:
- **EHDS** (ehds.gazelle-platform.net): Focused on IPS/FHIR validation
- **eHDSI** (gazelle.ehdsi.eu): Focused on CDA/HL7 document validation

---

## 📊 API Integration Pattern

### SOAP Web Service (Python with zeep)

```python
from zeep import Client
import base64

# Connect to service
wsdl = 'https://gazelle.ehdsi.eu/CDAGenerator-ejb/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl'
client = Client(wsdl)

# List validators
validators = client.service.getListOfValidators()
print(f"Found {len(validators)} validators")

# Read CDA document
with open('patient_summary.xml', 'rb') as f:
    xml_content = f.read()

# Encode to base64
base64_content = base64.b64encode(xml_content).decode('utf-8')

# Validate
result = client.service.validateBase64Document(
    base64Document=base64_content,
    validator='eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)'
)

print(result)
```

---

## 🎯 Next Steps

### Immediate Actions

1. **✅ DONE** - Discover EVS endpoints
2. **✅ DONE** - List available validators
3. **✅ DONE** - Create test scripts
4. **✅ DONE** - Document integration

### Future Work

1. **Convert FHIR → CDA**
   - Implement FHIR IPS to CDA conversion
   - Or use existing FHIR-to-CDA transformation tools

2. **Update API Client**
   - Modify `src/validator/api_client.py` to use WSDL endpoints
   - Implement SOAP client instead of REST client
   - Parse XML validation responses

3. **Integrate with CLI**
   - Update `src/cli.py` to support CDA validation
   - Add validator selection options
   - Format validation reports

4. **Test with Your Data**
   - Convert Diana Ferreira IPS → CDA
   - Convert Patrick Murphy IPS → CDA
   - Validate both documents
   - Compare results with EHDS validation

---

## 📚 Documentation Links

- **API Discovery:** [docs/EVS_API_DISCOVERY.md](docs/EVS_API_DISCOVERY.md)
- **EVS Documentation:** https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html
- **CDA Generator:** https://gazelle.ehdsi.eu/gazelle-documentation/CDA-Generator/user.html
- **eHDSI Portal:** https://gazelle.ehdsi.eu/evs/home.seam

---

## 🔐 API Key Information

**Platform:** gazelle.ehdsi.eu  
**API Key:** Loaded from `.env`  
**Created:** March 28, 2026 08:45 AM (CET)  
**Expires:** April 27, 2026 (30 days)  

**Note:** SOAP services may not require API key for basic validation operations. Further testing needed for authentication requirements.

---

## 🤝 Comparison with HL7_v2 Project Pattern

Your HL7_v2 project used:
1. **REST API** at testing.ehealthireland.ie
2. **Trial and error** to find working validators
3. **API key** in Authorization header

This FHIR project discovered:
1. **SOAP Web Services** at gazelle.ehdsi.eu
2. **Systematic discovery** using WSDL introspection
3. **49+ validators** automatically enumerated
4. **Service-specific endpoints** for different document types

**Key Learning:** The Gazelle platform provides WSDL endpoints with self-documenting APIs (via `getListOfValidators()`), making discovery more systematic than trial-and-error REST API testing.

---

## ✨ Success Indicators

✅ **Service Connectivity:** WSDL accessible, `about()` working  
✅ **Validator Discovery:** 49 CDA validators enumerated  
✅ **Test Script:** Functional validation testing tool  
✅ **Documentation:** Comprehensive guides created  
✅ **Integration Pattern:** SOAP client pattern established  

**STATUS:** Ready to validate CDA documents! 🎉

---

## 💡 Tips

1. **Use Latest Validators:** Wave 9 (V9.1.0 or V9.0.0) for most recent validation rules
2. **Start with L1:** Test structure first (`L1 validation`) before full content (`L3 validation`)
3. **Check epSOS:** If your documents match epSOS Patient Summary format
4. **Save Results:** Validation responses contain detailed error/warning information
5. **API Key:** May not be needed for basic validation; test without first

---

## 🐛 Troubleshooting

**Problem:** "Service unavailable" error  
**Solution:** Check network connection, verify WSDL URL hasn't changed

**Problem:** "Invalid validator name" error  
**Solution:** Run `--list-validators` to get exact validator names (case-sensitive)

**Problem:** "Could not parse validation result"  
**Solution:** Save raw XML result and inspect manually, structure varies by validator

**Problem:** IPS bundle validation fails  
**Solution:** eHDSI expects CDA format, convert FHIR IPS to CDA first

---

*Last Updated: March 28, 2026*  
*Discovery Results: [evs_discovery_results.json](evs_discovery_results.json)*
