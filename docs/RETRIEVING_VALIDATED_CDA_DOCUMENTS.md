# Retrieving Validated CDA Documents from Gazelle EVS

## Summary of What We Discovered

Your API key successfully authenticated with Gazelle EVS. We created three scripts that:

1. **`retrieve_gazelle_cda_examples.py`** - Attempted REST API discovery (no REST APIs found)
2. **`parse_gazelle_validation_history.py`** - Parses HTML pages with session authentication
3. **`fetch_gazelle_logs.py`** - Successfully extracted 13 PASSED validation entries from public logs
4. **`download_passed_cda_docs.py`** - Fetched validation reports (CDA documents require auth)

### ✅ What Worked
- Found 13 **PASSED** public validations from Gazelle logs
- Successfully retrieved validation report pages
- Identified OIDs for passed validations:
  - `1.3.6.1.4.1.12559.11.30.4.70999` (eHDSI - FRIENDLY CDA L3)
  - `1.3.6.1.4.1.12559.11.30.4.70998` (eHDSI - FRIENDLY CDA L3)
  - `1.3.6.1.4.1.12559.11.30.4.70997` (eHDSI - FRIENDLY CDA L3)
  - `1.3.6.1.4.1.12559.11.30.4.70991` (eHDSI - Patient Summary Wave 9)
  - `1.3.6.1.4.1.12559.11.30.4.70990` (eHDSI - PIVOT CDA L3)
  - And 8 more...

### ❌ What Requires Login
- Downloading actual CDA XML documents
- Accessing your personal validation history
- Viewing document content from validation reports

---

## Manual Approach: Download Your Validated CDA Documents

### Step 1: Log In to Gazelle EVS

1. Go to: https://gazelle.ehdsi.eu/evs/home.seam
2. Log in with your Gazelle credentials
3. Navigate to: **CDA Validation** > **Validation Logs**
   - Direct link: https://gazelle.ehdsi.eu/evs/cda/allLogs.seam?standard=10

### Step 2: Find Your Passed Validations

Look for entries where:
- **Validation status** = `DONE_PASSED`
- **Entry point** = `GUI` (your manual validations)
- Filter by your username or recent dates if available

### Step 3: Download CDA Documents

For each passed validation:

1. Click the **OID** link (e.g., `1.3.6.1.4.1.12559.11.30.4.70999`)
2. This opens the validation report page
3. Look for one of these options:
   - **"Download Document"** button
   - **"View Original Document"** link
   - **"XML Source"** tab or section
   - Right-click and "Save As" if XML is displayed inline
4. Save the file with a descriptive name (e.g., `patient_summary_validated.xml`)

### Step 4: Add to Your Project

Save downloaded CDA documents to:
```
HL7_EU_Gazelle_Validator/
  examples/
    patient_summary_validated.xml
    hospital_discharge_validated.xml
    medical_imaging_report_validated.xml
```

### Step 5: Update UI (Optional)

Add buttons to `streamlit_app.py` for your new examples:

```python
with col5:
    if st.button("📄 My Validated PS", use_container_width=True, key="my_ps"):
        example_path = Path('examples/patient_summary_validated.xml')
        if example_path.exists():
            with open(example_path, 'rb') as f:
                st.session_state['loaded_file_content'] = f.read()
                st.session_state['loaded_file_name'] = example_path.name
            st.success(f"✅ Loaded {example_path.name}")
            st.rerun()
```

---

## Alternative: Using Session Cookies (Advanced)

If you want to automate retrieval, you can provide a session cookie:

### Extract Session Cookie

1. Log in to https://gazelle.ehdsi.eu/evs/home.seam
2. Open Browser DevTools (F12)
3. Go to **Network** tab
4. Refresh the page
5. Click any request
6. In **Headers** section, find **Cookie** request header
7. Copy the entire cookie string

### Run Script with Cookie

```bash
py scripts/parse_gazelle_validation_history.py --session-cookie "JSESSIONID=abc123..."
```

This will access your personal validation history and attempt to download documents.

---

## What You Have Now

We already created two synthetic CDA examples for you:

### ✅ Ready to Use

1. **[examples/patient_summary_cda.xml](../examples/patient_summary_cda.xml)**
   - eHDSI Patient Summary (PS)
   - Patient: John Smith
   - Sections: Allergies, Medications, Problems
   - Template: `1.3.6.1.4.1.12559.11.10.1.3.1.1.2`

2. **[examples/hospital_discharge_cda.xml](../examples/hospital_discharge_cda.xml)**
   - eHDSI Hospital Discharge Report (HDR)
   - Patient: Sarah Murphy
   - STEMI case with PCI intervention
   - Template: `1.3.6.1.4.1.12559.11.10.1.3.1.1.4`

Both are properly formatted eHDSI CDA documents that should validate successfully with Gazelle EVS.

---

## Testing Your CDA Documents

### Using Streamlit UI

1. Launch: `streamlit run streamlit_app.py`
2. Click **"📄 Patient Summary CDA"** or **"📄 Hospital Discharge CDA"**
3. Select **Gazelle EVS** in sidebar
4. Click **"Validate Bundle"**
5. Review validation results

### Using Command Line

```bash
# Validate with FRIENDLY CDA (L3) validator
py scripts/test_evs_validation.py examples/patient_summary_cda.xml --validator "eHDSI - FRIENDLY CDA (L3) validation - Wave 9 (V9.1.0)"

# Validate with PIVOT CDA (L3) validator
py scripts/test_evs_validation.py examples/hospital_discharge_cda.xml --validator "eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)"

# Validate Patient Summary
py scripts/test_evs_validation.py examples/patient_summary_cda.xml --validator "eHDSI - Patient Summary validation - Wave 9 (V9.1.0)"
```

---

## Gazelle Validation Results from Public Logs

Based on public logs analysis (May 15, 2026):

| OID | Validator | Status | Date |
|-----|-----------|--------|------|
| `70999` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 5:11 PM |
| `70998` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 4:56 PM |
| `70997` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 4:55 PM |
| `70993` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 2:44 PM |
| `70992` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 2:40 PM |
| `70991` | eHDSI - Patient Summary Wave 9 | ✅ PASSED | 5/15/26 2:39 PM |
| `70990` | eHDSI - PIVOT CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 2:38 PM |
| `70989` | eHDSI - FRIENDLY CDA (L3) Wave 9 | ✅ PASSED | 5/15/26 2:38 PM |
| `70987` | eHDSI OrCD Medical Imaging Report Wave 9 | ✅ PASSED | 5/15/26 2:32 PM |

These are publicly accessible validation reports. The CDA documents themselves require authentication to download.

---

## Summary

**Current Status:**
- ✅ API key working
- ✅ 2 synthetic CDA examples created and ready to use
- ✅ UI updated with CDA example buttons
- ✅ Gazelle EVS validation integrated in Streamlit app
- ⏳ Automated document download requires login session

**Next Steps:**
1. **Test the synthetic examples** - They should validate successfully
2. **Manually download your validated CDAs** if you want real-world examples
3. **Add them to examples/** directory
4. **Update README.md** with any new examples

**Scripts Created:**
- `scripts/retrieve_gazelle_cda_examples.py` - REST API discovery
- `scripts/parse_gazelle_validation_history.py` - HTML parsing with session auth
- `scripts/fetch_gazelle_logs.py` - Public log extraction
- `scripts/download_passed_cda_docs.py` - Report fetching and document extraction

All validation reports are saved to `logs/` directory for manual inspection.
