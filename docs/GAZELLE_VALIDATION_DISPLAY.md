# Gazelle EVS Validation Display

## Overview

The Gazelle EVS validation now displays results in a clean, structured format similar to the Azure FHIR validation display, inspired by the [HL7_v2_Message_Validator-Auto-Correct](https://github.com/ddeveloper72/HL7_v2_Message_Validator-Auto-Correct) project.

## Features

### ✅ Structured XML Parsing

Instead of showing raw XML output, the validation results are now parsed and displayed in a user-friendly format:

```python
results = {
    'errors': [],      # Critical validation failures
    'warnings': [],    # Non-critical issues
    'information': [], # Informational messages
    'status': 'passed/failed',
    'raw_xml': '...'   # Original XML for reference
}
```

### 📊 Tabbed Display

Results are organized into three tabs:

#### 1. **Summary Tab**
- **Metrics**: Shows counts for errors, warnings, and info messages
- **Status**: Clear pass/fail indicator
- **Expandable Sections**: Each issue category can be expanded to view details
- **Context**: Displays location/path and test constraints for each issue

#### 2. **Full Response Tab**
- **Structured JSON**: Shows parsed validation results
- **Raw XML**: Original Gazelle response (in expandable section)

#### 3. **Download Tab**
- **JSON Export**: Download structured validation results
- **XML Export**: Download raw Gazelle report

## XML Parsing Logic

### Schematron Failed Assertions

Gazelle uses SVRL (Schematron Validation Report Language) format:

```xml
<svrl:failed-assert test="..." location="...">
    <svrl:text>Error message here</svrl:text>
</svrl:failed-assert>
```

The parser extracts:
- `test`: The constraint that failed
- `location`: XPath to the problem location in the CDA
- `text`: Human-readable error message

### Severity Classification

Issues are categorized by keywords:
- **Errors**: "error", "shall" (mandatory requirements)
- **Warnings**: "warning", "should" (recommendations)
- **Information**: Everything else

## Display Format

### Error Example
```
❌ Errors (2)

1. The effective time element SHALL be present
   📍 Location: /ClinicalDocument/effectiveTime
   🔍 Test: count(hl7:effectiveTime) = 1

2. Code system SHALL be from value set
   📍 Location: /ClinicalDocument/code
   🔍 Test: @codeSystem='2.16.840.1.113883.6.1'
```

### Warning Example
```
⚠️ Warnings (1)

1. The confidentiality code SHOULD be present
   📍 Location: /ClinicalDocument/confidentialityCode
   🔍 Test: count(hl7:confidentialityCode) >= 1
```

## Comparison with HL7_v2 Project

Both projects now share the same validation display pattern:

| Feature | HL7_v2 Validator | FHIR/CDA Validator |
|---------|------------------|-------------------|
| XML Parsing | ✅ | ✅ |
| Structured Display | ✅ | ✅ |
| Error Categorization | ✅ | ✅ |
| Download Results | ✅ | ✅ |
| Raw XML Access | ✅ | ✅ |

## Benefits

1. **User-Friendly**: No need to read raw XML
2. **Actionable**: Clear error messages with locations
3. **Consistent**: Same display for Azure FHIR and Gazelle EVS
4. **Exportable**: Download results for reporting
5. **Debuggable**: Raw XML available when needed

## Example Workflow

1. Load CDA example (e.g., Diana Ferreira PS)
2. Select "Gazelle EVS" validator
3. Click "Validate Bundle"
4. View structured results in Summary tab
5. Check specific error locations
6. Download JSON for documentation

## Testing

To test the enhanced display:

```bash
# Test with real-world eHDSI Patient Summary
streamlit run streamlit_app.py

# Load: Diana Ferreira PS or Patrick Murphy PS
# Validator: Gazelle EVS
# View: Structured results with errors/warnings/info
```

## API Response Structure

The `validate_document()` function now returns:

```python
{
    'errors': [
        {
            'diagnostics': 'Error message',
            'location': 'XPath location',
            'test': 'Schematron test expression',
            'details': {...}
        }
    ],
    'warnings': [...],
    'information': [...],
    'status': 'passed|failed|unknown',
    'raw_xml': '<?xml version="1.0"?>...'
}
```

## Future Enhancements

Potential improvements:
- 🔍 Click location to highlight in XML preview
- 📊 Validation history tracking
- 📈 Trend analysis across multiple validations
- 🎨 Color-coded XPath visualization
- 💾 Save/compare validation reports

## References

- [HL7_v2 Message Validator](https://github.com/ddeveloper72/HL7_v2_Message_Validator-Auto-Correct)
- [Gazelle EVS Documentation](https://gazelle.ehdsi.eu/)
- [SVRL Specification](http://www.schematron.com/validators.html)
