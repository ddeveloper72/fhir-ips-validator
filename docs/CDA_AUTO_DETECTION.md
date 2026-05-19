# CDA Validator Auto-Detection

## Problem Solved

**Before:** The app was hardcoded to use only one validator:
```python
validator_name = 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)'
```

This didn't work for different CDA types (Patient Summary, Hospital Discharge, Medical Imaging, etc.)

**After:** Intelligent auto-detection with manual override capability.

---

## How It Works

### 1. **Template ID Extraction**

When a user uploads any CDA XML file, the system:

1. **Parses the XML** and extracts all `<templateId root="...">` elements
2. **Identifies the document type** from the first templateId
3. **Maps to appropriate validator** using a predefined mapping table

### 2. **Template ID → Validator Mapping**

```python
TEMPLATE_TO_VALIDATOR = {
    # Patient Summary
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.3': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'Patient Summary (PS)',
        'level': 'L3 - Full Content Validation'
    },
    
    # Hospital Discharge Report
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.4': {
        'name': 'eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)',
        'type': 'Hospital Discharge Report (HDR)',
        'level': 'L3 - Full Validation'
    },
    
    # Medical Imaging Report
    '1.3.6.1.4.1.12559.11.10.1.3.1.1.6': {
        'name': 'eHDSI OrCD - Medical Imaging Report CDA (L3) validation - Wave 10 (V10.0.0)',
        'type': 'Medical Imaging Report (MIR)',
        'level': 'L3 - OrCD Validation'
    },
    
    # ... and more
}
```

### 3. **Confidence Levels**

| Confidence | Meaning | Action |
|------------|---------|--------|
| **HIGH** | Exact template ID match found | Use mapped validator |
| **MEDIUM** | Partial match (eHDSI prefix) | Use generic eHDSI validator |
| **LOW** | No match found | Fallback to basic CDA R2 validator |

### 4. **Fallback Strategy**

```
1. Try exact template ID match → HIGH confidence
2. Try eHDSI prefix match (1.3.6.1.4.1.12559.11.10) → MEDIUM confidence  
3. Use generic CDA R2 validator → LOW confidence
```

---

## User Experience

### When User Uploads Random CDA:

1. **Auto-Detection Runs**
   ```
   📋 Detected Document Type: Patient Summary (PS)
   🎯 Confidence: HIGH | Validation: L3 - Full Content Validation
   ```

2. **Template IDs Shown** (expandable)
   ```
   🔍 Template IDs Found
   1.3.6.1.4.1.12559.11.10.1.3.1.1.3
   1.3.6.1.4.1.19376.1.5.3.1.2.4
   ...
   ```

3. **Recommended Validator** (default selected)
   ```
   ✅ Use recommended: eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)
   ```

4. **Manual Override Option**
   - Uncheck "Use recommended"
   - Dropdown appears with all 49+ Gazelle validators
   - User can select any validator they want

5. **Validation Proceeds**
   ```
   🔧 Validating with: eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)
   ✅ Gazelle validation completed!
   ```

---

## Example Scenarios

### Scenario 1: Real-World Patient Summary

**Upload:** `Diana_Ferreira_PS.xml`

**Detection Result:**
```
Document Type: Patient Summary (PS)
Confidence: HIGH
Recommended: eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)
```

**User Action:** Click validate (uses recommended)

---

### Scenario 2: Hospital Discharge Report

**Upload:** `hospital_discharge_cda.xml`

**Detection Result:**
```
Document Type: Hospital Discharge Report (HDR)
Confidence: HIGH  
Recommended: eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)
```

**User Action:** Click validate (uses recommended)

---

### Scenario 3: Medical Imaging Report

**Upload:** `radiology_report.xml`

**Detection Result:**
```
Document Type: Medical Imaging Report (MIR)
Confidence: HIGH
Recommended: eHDSI OrCD - Medical Imaging Report CDA (L3) validation - Wave 10 (V10.0.0)
```

**User Action:** Click validate (uses specialized OrCD validator)

---

### Scenario 4: Unknown/Custom CDA

**Upload:** `custom_document.xml`

**Detection Result:**
```
Document Type: CDA Document (detection failed)
Confidence: LOW
Recommended: HL7 - CDA Release 2
```

**User Action:** Uncheck recommended → Select appropriate validator from dropdown

---

## Technical Implementation

### Core Detection Function

```python
def detect_cda_type(xml_content: str) -> Dict:
    """
    Detect CDA document type from templateId elements
    
    Returns:
        {
            'template_ids': ['1.3.6.1.4.1.12559...', ...],
            'recommended_validator': 'eHDSI - PIVOT CDA...',
            'document_type': 'Patient Summary (PS)',
            'validation_level': 'L3 - Full Content Validation',
            'confidence': 'high'|'medium'|'low'
        }
    """
```

### Streamlit Integration

```python
# 1. Auto-detect when XML uploaded
cda_detection = detect_cda_type(file_content)

# 2. Show detection results
st.info(f"📋 Detected: {cda_detection['document_type']}")
st.caption(f"🎯 Confidence: {cda_detection['confidence']}")

# 3. Checkbox for recommended validator
use_recommended = st.checkbox(
    f"✅ Use recommended: {cda_detection['recommended_validator']}",
    value=True
)

# 4. Manual selection dropdown (if unchecked)
if not use_recommended:
    validator_name = st.selectbox(
        "Available Validators:",
        options=validators  # All 49+ validators
    )
```

---

## Benefits

✅ **Intelligent:** Automatically selects correct validator  
✅ **Flexible:** User can override if needed  
✅ **Transparent:** Shows detection confidence and reasoning  
✅ **Comprehensive:** Supports all eHDSI document types  
✅ **Fallback:** Gracefully handles unknown documents  

---

## Supported Document Types

| Template ID | Document Type | Validator |
|-------------|---------------|-----------|
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.3` | Patient Summary (PS) | eHDSI PIVOT L3 Wave 9 |
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.1` | ePrescription (eP) | eHDSI PIVOT L3 Wave 9 |
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.2` | eDispensation (eD) | eHDSI PIVOT L3 Wave 9 |
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.4` | Hospital Discharge (HDR) | eHDSI PIVOT L3 Wave 9 |
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.5` | Laboratory Report (LR) | eHDSI PIVOT L3 Wave 9 |
| `1.3.6.1.4.1.12559.11.10.1.3.1.1.6` | Medical Imaging (MIR) | eHDSI OrCD L3 Wave 10 |
| `1.3.6.1.4.1.19376.1.5.3.1.1.1` | IHE PCC Medical Docs | eHDSI PIVOT L3 Wave 9 |
| *Any other* | Generic CDA | HL7 - CDA Release 2 |

---

## Testing

Test the detection with command line:

```bash
# Test Patient Summary
python scripts/detect_cda_type.py examples/Diana_Ferreira_PS.xml

# Test Hospital Discharge
python scripts/detect_cda_type.py examples/hospital_discharge_cda.xml

# Test any CDA file
python scripts/detect_cda_type.py path/to/your/document.xml
```

Expected output:
```
================================================================================
CDA DOCUMENT TYPE DETECTION
================================================================================

File: examples/Diana_Ferreira_PS.xml

Document Type: Patient Summary (PS)
Validation Level: L3 - Full Content Validation
Confidence: HIGH

Recommended Validator:
  eHDSI - PIVOT CDA (L3) validation - Wave 9 (V9.1.0)

Template IDs Found:
  - 1.3.6.1.4.1.12559.11.10.1.3.1.1.3
  - 1.3.6.1.4.1.19376.1.5.3.1.2.4
  ...
================================================================================
```

---

## Future Enhancements

Potential improvements:
- 📊 Add validation history by document type
- 🎨 Color-code confidence levels
- 📈 Show statistics on document types validated
- 🔍 Add search/filter in validator dropdown
- 💡 Suggest alternative validators based on document content
- 🌍 Support multi-country template variations

---

## References

- [eHDSI CDA Specifications](https://art-decor.org/art-decor/decor-project--ehdsi-)
- [IHE PCC Templates](https://wiki.ihe.net/index.php/Patient_Care_Coordination)
- [Gazelle Validators List](https://gazelle.ehdsi.eu/)
