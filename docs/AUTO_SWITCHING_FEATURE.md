# Auto-Switching Validator Feature

## Overview
The Streamlit UI now automatically switches to the appropriate validator based on the file type you upload or load.

## How It Works

### 🤖 Smart Detection
When you upload or load a file, the app automatically:

| File Type | Auto-Selects | Reason |
|-----------|-------------|---------|
| **`.json`** | **Azure FHIR** | FHIR R4 bundles are JSON format |
| **`.xml`** | **Gazelle EVS** | CDA documents are XML format |

### 📢 User Notification
After auto-switching, you'll see:
```
💡 Auto-selected: XML format → Gazelle EVS (CDA documents)
You can manually change the validator in the sidebar if needed.
```

### ✋ Manual Override
You can always manually change the validator in the sidebar if the auto-selection isn't what you want.

---

## Why This Matters

### ❌ **Azure FHIR Cannot Validate CDA/XML**
Azure FHIR Service **only supports FHIR R4 JSON bundles**. It will fail if you try to validate:
- CDA documents (XML)
- Any XML-based format

### ✅ **Gazelle EVS Can Only Validate CDA/XML**
Gazelle EVS validators are designed for **CDA documents in XML format**. They cannot validate:
- FHIR JSON bundles
- Other JSON formats

---

## User Experience Improvements

### Before Auto-Switching:
1. User uploads `Patient_Summary.xml`
2. Default validator: **Azure FHIR** ❌
3. User clicks "Validate"
4. Error: "⚠️ Gazelle EVS requires CDA documents in XML format"
5. User must manually switch to Gazelle EVS
6. User clicks "Validate" again

### After Auto-Switching:
1. User uploads `Patient_Summary.xml`
2. **Automatic switch:** Gazelle EVS ✅
3. Notification: "💡 Auto-selected: XML format → Gazelle EVS"
4. User clicks "Validate" → Success!

---

## Example Scenarios

### Scenario 1: Upload JSON FHIR Bundle
```
1. Upload: Diana_Ferreira_bundle.json
2. Auto-switch: Azure FHIR ✅
3. Notification: "💡 Auto-selected: JSON format → Azure FHIR (FHIR R4 bundles)"
4. Validate: Success with Azure FHIR Service
```

### Scenario 2: Upload XML CDA Document
```
1. Upload: 2-5678-W7_PS.xml
2. Auto-switch: Gazelle EVS ✅
3. Notification: "💡 Auto-selected: XML format → Gazelle EVS (CDA documents)"
4. Platform: User can choose eHDSI or EHDS Gazelle
5. Mode: User can choose Strict or Permissive
6. Validate: Success with appropriate CDA validator
```

### Scenario 3: Switch Between Files
```
1. Load: Diana_Ferreira_bundle.json → Azure FHIR ✅
2. Validate JSON: Success
3. Load: Patient_Murphy_PS.xml → Gazelle EVS ✅
4. Validate XML: Success
5. Load: Patrick_Murphy_bundle.json → Azure FHIR ✅
6. Validate JSON: Success
```

---

## Technical Implementation

### Session State Variables
```python
st.session_state['recommended_validator']  # 'Azure FHIR' or 'Gazelle EVS'
st.session_state['show_validator_switch_message']  # Boolean
st.session_state['switch_reason']  # Explanation text
```

### Detection Logic
```python
if file_name.endswith('.json'):
    recommended = 'Azure FHIR'
    reason = 'JSON format → Azure FHIR (FHIR R4 bundles)'
elif file_name.endswith('.xml'):
    recommended = 'Gazelle EVS'
    reason = 'XML format → Gazelle EVS (CDA documents)'
```

### Auto-Switching Trigger
- Triggered on file upload
- Triggered on example button click
- Only triggers if validator changes
- Shows notification once per switch
- Rerun required to update sidebar

---

## UI Updates

### Sidebar Validator Selection
```
🎯 Select Validator
⚪ Azure FHIR          ← Default for JSON
⚪ Gazelle EVS         ← Default for XML

Choose validation service:
Azure FHIR for FHIR R4 JSON bundles, Gazelle for CDA XML documents
```

### File Uploader
```
📤 Upload Document

Choose a FHIR bundle (JSON) or CDA document (XML)
💡 Upload FHIR R4 IPS bundle (JSON) or CDA document (XML) - validator will auto-select
```

### Validator Info Boxes
**Azure FHIR:**
```
✅ FHIR R4 bundles (JSON only)
❌ Cannot validate CDA/XML
💡 Upload an XML file to auto-switch to Gazelle
```

**Gazelle EVS:**
```
✅ CDA Wave 7-10 validation (XML)
💡 Upload a JSON file to auto-switch to Azure
```

---

## Benefits

1. **✅ Reduces User Errors** - No more trying to validate JSON with Gazelle or XML with Azure
2. **⏱️ Saves Time** - One click instead of multiple steps
3. **🎯 Better UX** - Users don't need to know which validator to use
4. **📚 Educational** - Notification explains why the switch happened
5. **🔄 Flexible** - Users can still override if needed

---

## Testing

### Test Cases:
1. ✅ Upload `.json` file → Should auto-select Azure FHIR
2. ✅ Upload `.xml` file → Should auto-select Gazelle EVS
3. ✅ Load JSON example → Should auto-select Azure FHIR
4. ✅ Load XML example → Should auto-select Gazelle EVS
5. ✅ Switch from JSON to XML → Should auto-switch validators
6. ✅ Switch from XML to JSON → Should auto-switch validators
7. ✅ Manual override → Should allow manual change

### Expected Behavior:
- Notification appears once after switch
- Sidebar updates with new default
- User can still manually change validator
- No errors when validating with auto-selected validator

---

## Future Enhancements

Possible improvements:
1. **Content-based detection** - Parse file content to verify format matches extension
2. **FHIR vs CDA detection** - Distinguish between FHIR XML and CDA XML
3. **Multi-format support** - Support other formats (HL7v2, etc.)
4. **Validator recommendations** - Suggest specific validators based on document content
5. **Validation history** - Remember user's validator preferences per file type

---

## Related Documentation
- [VALIDATION_MODE_GUIDE.md](VALIDATION_MODE_GUIDE.md) - Strict vs Permissive modes
- [EHDS_GAZELLE_INTEGRATION.md](EHDS_GAZELLE_INTEGRATION.md) - Gazelle platform details
- [CDA_TO_FHIR_TRADEOFFS.md](CDA_TO_FHIR_TRADEOFFS.md) - Format conversion considerations
