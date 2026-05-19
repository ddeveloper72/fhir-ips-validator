# Gazelle Validation Metadata & Report Links

## Overview
The Streamlit UI now displays validation metadata from Gazelle and provides links to the web interface for obtaining persistent report URLs.

## What's New

### 📋 **Validation Details Section**
After each Gazelle validation, you'll now see detailed metadata:

```
📋 Validation Details
┌─────────────────────────────────┬─────────────────────────────────┐
│ 📅 Date: 2026, 05 17           │ 🔧 Engine: Gazelle CDA Validation │
│ 🕐 Time: 06:43:22              │ 📌 Version: 3.1.1               │
└─────────────────────────────────┴─────────────────────────────────┘
🎯 Validator: HL7 - CDA Release 2
```

### 🌐 **Persistent Report Link**
Below the validation details, you'll see information about getting a permanent report:

```
🌐 Want a persistent report?

This SOAP validation provides instant results but doesn't generate a 
permanent web report. To get a shareable report URL, visit the Gazelle 
web interface:

👉 [EHDS Gazelle Validator](https://ehds.gazelle-platform.net/evs/home.seam)

Upload your document there to receive a permanent report link like:
https://ehds.gazelle-platform.net/evs/report.seam?oid=...
```

---

## Why This Matters

### 🔍 **Understanding SOAP vs Web Validation**

| Feature | SOAP API (Our App) | Web Interface |
|---------|-------------------|---------------|
| **Speed** | ✅ Instant (10-30 sec) | ✅ Fast (10-30 sec) |
| **Results** | ✅ Full validation details | ✅ Full validation details |
| **Persistent Report URL** | ❌ No | ✅ Yes |
| **Shareable Link** | ❌ No | ✅ Yes |
| **Automation** | ✅ Yes | ❌ Manual |

### 📊 **When to Use Each**

**Use Our Streamlit App (SOAP API) When:**
- ✅ You want instant validation
- ✅ You're validating multiple documents
- ✅ You need automation
- ✅ You don't need to share results with others
- ✅ You're testing/debugging during development

**Use Gazelle Web Interface When:**
- ✅ You need a permanent report URL
- ✅ You want to share results with colleagues
- ✅ You're preparing for certification/submission
- ✅ You need to reference validation results later
- ✅ You want to cite validation in documentation

---

## Metadata Extracted

The following metadata is now captured from each Gazelle validation:

| Field | Description | Example |
|-------|-------------|---------|
| **ValidationDate** | Date of validation | `2026, 05 17` |
| **ValidationTime** | Time of validation | `06:43:22` |
| **ValidationEngine** | Validation engine name | `Gazelle CDA Validation` |
| **ValidationEngineVersion** | Engine version | `3.1.1` |
| **ValidationServiceName** | Validator used | `HL7 - CDA Release 2` |
| **ValidationServiceVersion** | Validator version | `N/A` or version number |
| **ValidationTestResult** | Overall result | `PASSED` or `FAILED` |

---

## Technical Implementation

### Changes to `test_evs_validation.py`

#### 1. Added Metadata Extraction
```python
# Extract ValidationResultsOverview metadata
overview = root.find('.//ValidationResultsOverview')
if overview is not None:
    metadata = {}
    
    # Extract all fields from overview
    for child in overview:
        metadata[child.tag] = child.text
    
    results['metadata'] = metadata
    
    # Update status from overview if available
    if 'ValidationTestResult' in metadata:
        results['status'] = metadata['ValidationTestResult']
```

#### 2. Added Gazelle Web URL
```python
# Determine base URL from WSDL
if 'ehds.gazelle-platform.net' in wsdl_url:
    gazelle_web_url = 'https://ehds.gazelle-platform.net/evs/home.seam'
else:
    gazelle_web_url = 'https://gazelle.ehdsi.eu/evs/home.seam'

parsed_results['gazelle_web_url'] = gazelle_web_url
parsed_results['validator_name'] = validator_name
```

### Changes to `streamlit_app.py`

#### 1. Display Validation Metadata
```python
if result.get('metadata'):
    metadata = result['metadata']
    
    st.subheader("📋 Validation Details")
    
    col_meta1, col_meta2 = st.columns(2)
    
    with col_meta1:
        if metadata.get('ValidationDate'):
            st.metric("📅 Date", metadata['ValidationDate'])
        if metadata.get('ValidationTime'):
            st.metric("🕐 Time", metadata['ValidationTime'])
    
    with col_meta2:
        if metadata.get('ValidationEngine'):
            st.metric("🔧 Engine", metadata['ValidationEngine'])
        if metadata.get('ValidationEngineVersion'):
            st.metric("📌 Version", metadata['ValidationEngineVersion'])
    
    st.caption(f"🎯 Validator: **{result.get('validator_name', 'Unknown')}**")
```

#### 2. Show Gazelle Web Link
```python
if result.get('gazelle_web_url'):
    st.info(f"""
    🌐 **Want a persistent report?**
    
    This SOAP validation provides instant results but doesn't generate 
    a permanent web report. To get a shareable report URL, visit the 
    Gazelle web interface:
    
    👉 [{platform_name} Validator]({result['gazelle_web_url']})
    
    Upload your document there to receive a permanent report link like:
    `https://{result['gazelle_web_url'].split('//')[1].split('/')[0]}/evs/report.seam?oid=...`
    """)
```

---

## Gazelle Web Interface URLs

### eHDSI Gazelle (Original Platform)
**Validator Home:** https://gazelle.ehdsi.eu/evs/home.seam
**Report Format:** https://gazelle.ehdsi.eu/evs/report.seam?oid=1.3.6.1.4.1.12559.11.30.4.XXXXX

**Features:**
- Wave 7-10 validators
- eHDSI L1/L3 compliance
- Cross-border eHealth (NCPeH)

### EHDS Gazelle (New Platform)
**Validator Home:** https://ehds.gazelle-platform.net/evs/home.seam
**Report Format:** https://ehds.gazelle-platform.net/evs/report.seam?oid=1.3.6.1.4.1.12559.11.55.1.13.XXXX

**Features:**
- HL7 EU standards (IPS, EU-EPS)
- EU Base & Core profiles
- epSOS validators
- Modern FHIR validation

---

## User Workflow

### Complete Validation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Quick Validation (Streamlit App)                            │
├─────────────────────────────────────────────────────────────────┤
│ • Upload document to Streamlit                                  │
│ • Get instant validation results                                │
│ • Review errors/warnings/info                                   │
│ • See validation metadata                                       │
│ • Note: Results are temporary                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ 2. Get Persistent Report (Gazelle Web)                         │
├─────────────────────────────────────────────────────────────────┤
│ • Click "EHDS Gazelle Validator" link                          │
│ • Upload same document to Gazelle web                          │
│ • Get permanent report URL                                      │
│ • Share with colleagues/certification body                      │
│ • Reference in documentation                                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Example Report URLs

These are real examples from previous validations:

### eHDSI Gazelle Reports
```
✅ PASSED (Wave 7)
https://gazelle.ehdsi.eu/evs/report.seam?oid=1.3.6.1.4.1.12559.11.30.4.71007

❌ FAILED (Wave 9)
https://gazelle.ehdsi.eu/evs/report.seam?oid=1.3.6.1.4.1.12559.11.30.4.71009
```

### EHDS Gazelle Reports
```
✅ PASSED (Matchbox IPS)
https://ehds.gazelle-platform.net/evs/report.seam?oid=1.3.6.1.4.1.12559.11.55.1.13.1930

❌ FAILED (epSOS Pivot)
https://ehds.gazelle-platform.net/evs/report.seam?oid=1.3.6.1.4.1.12559.11.55.1.13.1925
```

---

## Benefits

1. **✅ Instant Validation** - Get results in seconds via SOAP API
2. **📋 Rich Metadata** - See exactly when, how, and with what version validation was performed
3. **🌐 Path to Persistence** - Clear guidance on getting shareable report URLs
4. **🔄 Best of Both Worlds** - Use automation for speed, web UI for permanence
5. **📊 Full Transparency** - Understand the validation engine and versions used

---

## Future Enhancements

Possible improvements:
1. **Automatic Web Submission** - Submit documents to Gazelle web API automatically to get report URLs
2. **Report History** - Store previous validation results locally
3. **Report Comparison** - Compare validation results between sessions
4. **One-Click Share** - Generate validation summary with link to web report

---

## Related Documentation
- [VALIDATION_MODE_GUIDE.md](VALIDATION_MODE_GUIDE.md) - Strict vs Permissive modes
- [AUTO_SWITCHING_FEATURE.md](AUTO_SWITCHING_FEATURE.md) - Smart validator selection
- [EHDS_GAZELLE_INTEGRATION.md](EHDS_GAZELLE_INTEGRATION.md) - Platform comparison
