# Gazelle Report URL Investigation Summary

## What We Discovered

### ✅ REST API Exists on Both Platforms
- **eHDSI Gazelle:** `https://gazelle.ehdsi.eu/evs/rest/validations`
- **EHDS Gazelle:** `https://ehds.gazelle-platform.net/evs/rest/validations`

Both return **405 Method Not Allowed** for GET, confirming the endpoint exists and requires POST.

---

## How Your HL7_v2 Project Gets Report URLs

### Working Example from `HL7_v2_Message_Validator-Auto-Correct`

```python
# 1. Submit via REST API
response = requests.post(
    'https://testing.ehealthireland.ie/evs/rest/validations',
    json={
        "objects": [{
            "originalFileName": filename,
            "content": base64_content
        }],
        "validationService": {
            "name": "Gazelle HL7v2.x validator",
            "validator": validator_oid  # e.g., '1.3.6.1.4.1.12559.11.35.10.1.12'
        }
    },
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'GazelleAPIKey {api_key}'
    }
)

# 2. Extract Location header (201 response)
location = response.headers.get('Location')
# Example: /evs/rest/validations/1.3.6.1.4.1.12559.11.35.8.1.XXXX?privacyKey=YYYY

# 3. Parse to get OID and privacy key
oid_with_key = location.split('validations/')[-1]
oid = oid_with_key.split('?')[0]
privacy_key = oid_with_key.split('=')[-1]

# 4. Construct permanent report URL
report_url = f"https://testing.ehealthireland.ie/evs/report.seam?oid={oid}&privacyKey={privacy_key}"
```

---

## Challenge: CDA vs HL7v2

### HL7 v2 Messages (Your Other Project)
- ✅ Known validator OIDs (e.g., `1.3.6.1.4.1.12559.11.35.10.1.12` for ORU^R01)
- ✅ Documented in `Gazelle_Configuration_Data/hl7MessageProfiles.xml`
- ✅ REST API works with these OIDs

### CDA Documents (This Project)
- ❌ SOAP API returns validator **names**, not **OIDs**
  - Example: "epSOS - Patient Summary Pivot"
- ❌ No mapping between SOAP names and REST OIDs
- ❓ CDA validator OIDs not documented in same way as HL7v2

---

## Options to Get Report URLs

### Option 1: Hybrid SOAP + REST Approach ⚡ (Requires Research)
**Steps:**
1. Use SOAP `getListOfValidators()` to get validator names
2. Find/create mapping from names to OIDs
3. Submit via REST API using OIDs
4. Get report URL from Location header

**Pros:**
- ✅ Automated report URL generation
- ✅ Users get permanent links automatically

**Cons:**
- ❌ Need to discover CDA validator OIDs (not documented)
- ❌ May require trial-and-error or API documentation we don't have
- ❌ Different payload format might be needed for CDA

### Option 2: Web Upload with Guidance 📋 (Current Approach)
**Steps:**
1. Use SOAP for instant validation (what we have now)
2. Show validation results immediately
3. Provide link to Gazelle web interface
4. User manually uploads to get persistent report

**Pros:**
- ✅ Already implemented
- ✅ Works reliably
- ✅ No need for OID mapping

**Cons:**
- ❌ Manual step required for persistent reports
- ❌ Not fully automated

### Option 3: Discover OIDs via Trial & Error 🔬 (Risky)
**Steps:**
1. Try common CDA validator OID patterns
2. Test with REST API until we find working ones
3. Build mapping table

**Pros:**
- ✅ Could achieve full automation

**Cons:**
- ❌ Time-consuming
- ❌ May hit rate limits
- ❌ Might get different results than SOAP

---

## Recommended Approach

### Short-term: **Option 2** (Current Implementation)
Keep using SOAP with web UI guidance. This is:
- ✅ Reliable
- ✅ Fast to implement (already done!)
- ✅ Provides instant validation feedback
- ✅ Clear path to persistent reports

### Long-term: **Option 1** (If OID Mapping Found)
If we can discover/document CDA validator OIDs, implement REST API submission for automated report URLs.

---

## Key Insights from HL7_v2 Project

### Validator OID Structure
```
1.3.6.1.4.1.12559  = Gazelle base
.11.35             = HealthLink domain
.10.1.12           = Specific validator (ORU^R01 - Lab Results)
```

### CDA Validator OIDs (Unknown)
We'd need to find patterns like:
```
1.3.6.1.4.1.12559.11.X.Y.Z = CDA validator
                         ^
                         Different domain/numbering?
```

---

## What We Need to Proceed with REST API

1. **CDA Validator OIDs** - How to map SOAP validator names to OIDs?
2. **Payload Format** - Does CDA use same JSON structure as HL7v2?
3. **Platform Differences** - Do eHDSI and EHDS use different OID schemes?

---

## Current Implementation ✅

**What works now:**
1. SOAP validation with full error details
2. Validation metadata (date, time, engine, version)
3. Link to Gazelle web interface for persistent reports
4. Clear instructions for users

**User workflow:**
```
1. Upload document to Streamlit ⚡
   → Instant SOAP validation
   → See all errors/warnings immediately

2. Need persistent report? 🌐
   → Click link to Gazelle web
   → Upload document again
   → Get permanent report URL
```

This is a **solid, working solution** that gives users the best of both worlds!

---

## Decision Point

**Do you want to:**
1. ✅ Keep current approach (SOAP + web guidance) - **Recommended**
2. 🔬 Investigate REST API OIDs (time investment, uncertain outcome)
3. 📧 Contact Gazelle support for OID documentation

Let me know which path you prefer!
