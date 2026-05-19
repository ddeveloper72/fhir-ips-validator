# Validation Mode Guide

## Overview
The FHIR IPS Validator now supports two validation modes to address different use cases and platform behaviors.

## The Platform Difference You Discovered

**Important Finding:**
- **2-5678-W7_PS.xml** on eHDSI Gazelle (gazelle.ehdsi.eu): ✅ PASSES with Wave 7 validator
- **Same file** on EHDS Gazelle (ehds.gazelle-platform.net): ❌ FAILS with "epSOS - Patient Summary Pivot" but ✅ PASSES with "HL7 - CDA Release 2"

**Why This Happens:**
- eHDSI platform has Wave 7/8/9/10 validators that are calibrated for eHDSI documents
- EHDS platform has epSOS validators that enforce stricter legacy requirements
- Generic "HL7 - CDA Release 2" validates basic CDA structure only (more lenient)

---

## Validation Modes

### 🔍 Strict Mode (Recommended)
**When to use:**
- Production/conformance testing
- Preparing documents for real eHDSI/epSOS systems
- Quality assurance and certification
- You want to know ALL potential issues

**What it does:**
- Prioritizes implementation-specific validators (epSOS, eHDSI Wave 7-10)
- Catches compliance issues with implementation guides
- May flag documents with minor issues
- Scoring: epSOS/eHDSI validators get +8 points, PIVOT/FRIENDLY +5 points

**Example results:**
- 2-5678-W7_PS.xml on EHDS Gazelle → Selects "epSOS - Patient Summary Pivot" → May show errors
- Diana_Ferreira_PS.xml → Selects "eHDSI - PIVOT CDA (L3) Wave 9" → Shows ~60 errors due to FHIR conversion modifications

---

### ✅ Permissive Mode (Basic Structure)
**When to use:**
- Quick structure validation
- Development/debugging
- Confirming "is this valid XML?"
- You just need to verify basic CDA R2 compliance

**What it does:**
- Prioritizes generic "HL7 - CDA Release 2" validator
- Checks basic CDA structure only
- Higher pass rate
- Scoring: Generic CDA R2 gets +20 points (highest priority)

**Example results:**
- 2-5678-W7_PS.xml on EHDS Gazelle → Selects "HL7 - CDA Release 2" → ✅ PASSES
- Diana_Ferreira_PS.xml → Selects "HL7 - CDA Release 2" → Likely passes basic structure

**⚠️ Important:** Passing in permissive mode does NOT guarantee:
- eHDSI/epSOS compliance
- Interoperability with real NCPeH systems
- Production readiness

---

## Choosing the Right Mode

### Use Strict Mode If:
- ✅ You're validating for production deployment
- ✅ You need to meet eHDSI/epSOS certification requirements
- ✅ You want comprehensive quality checks
- ✅ You're debugging specific implementation guide issues
- ✅ Even if documents fail, you want to know WHY

### Use Permissive Mode If:
- ✅ You're in early development
- ✅ You just need basic XML structure validation
- ✅ You're testing document generation code
- ✅ You want a "sanity check" before deeper validation
- ✅ You've already validated with strict validators and just want quick confirmation

---

## Technical Details

### Scoring Algorithm Changes

**Strict Mode:**
```
Document type match (PS, HDR, etc.): +10 points
epSOS validators: +8 points
eHDSI validators: +8 points
PIVOT/FRIENDLY validators: +5 points
Wave version match: +5 points
Validation level (L3): +5 points
Generic CDA: +2 points
```

**Permissive Mode:**
```
Generic "CDA Release 2" match: +20 points (PRIORITY)
Document type match: +10 points
Validation level (L3): +5 points
epSOS/eHDSI/PIVOT/FRIENDLY: NO BONUS (0 points)
```

### Validator Selection Flow

1. **Parse CDA** → Extract templateIds
2. **Detect document type** → Patient Summary, HDR, etc.
3. **Get available validators** → From selected Gazelle platform
4. **Score each validator** → Based on validation mode
5. **Select best match** → Highest scoring validator
6. **Show confidence** → HIGH/MEDIUM/LOW
7. **Allow manual override** → User can change if needed

---

## Platform-Specific Recommendations

### eHDSI Gazelle (gazelle.ehdsi.eu)
**Strict Mode:**
- Selects: "eHDSI - PIVOT CDA (L3) validation - Wave 7/8/9/10"
- Good for: eHDSI NCPeH systems, cross-border eHealth

**Permissive Mode:**
- Selects: "HL7 - CDA Release 2"
- Good for: Basic structure checks

### EHDS Gazelle (ehds.gazelle-platform.net)
**Strict Mode:**
- Selects: "epSOS - Patient Summary Pivot" (or similar epSOS validator)
- Good for: Legacy epSOS systems
- **Note:** May be stricter than eHDSI Wave validators!

**Permissive Mode:**
- Selects: "HL7 - CDA Release 2"
- Good for: Basic structure checks
- **Note:** Most likely to pass

---

## Example Scenarios

### Scenario 1: Production eHDSI Document
**Goal:** Validate 2-5678-W7_PS.xml for production use

**Approach:**
1. Use **eHDSI Gazelle** platform
2. Use **Strict Mode**
3. Expected result: Selects "Wave 7" validator → ✅ PASSES
4. Confidence: HIGH

### Scenario 2: Modified CDA for FHIR Conversion
**Goal:** Validate Diana_Ferreira_PS.xml (modified for FHIR)

**Approach:**
1. Use **EHDS Gazelle** platform
2. Use **Permissive Mode**
3. Expected result: Selects "HL7 - CDA Release 2" → ✅ PASSES
4. Note: Document has known modifications, strict validation will fail

### Scenario 3: Development Testing
**Goal:** Quick check that generated CDA is valid XML

**Approach:**
1. Use **either platform**
2. Use **Permissive Mode**
3. Expected result: Basic structure validation → Fast feedback
4. Follow up with Strict Mode before production

### Scenario 4: Conformance Testing
**Goal:** Verify full eHDSI compliance

**Approach:**
1. Use **eHDSI Gazelle** platform
2. Use **Strict Mode**
3. Review all errors/warnings
4. Fix issues until validation passes
5. Do NOT switch to Permissive Mode to "make it pass"

---

## FAQ

**Q: Should I favor a validator that passes my document?**
**A:** It depends on your goal:
- If you're validating for **production**: NO - use strict validators to find real issues
- If you're doing **basic structure checks**: YES - use permissive mode
- If you're **debugging**: Use strict to see issues, permissive to confirm structure

**Q: Why does my document fail on EHDS but pass on eHDSI?**
**A:** Different platforms have different validators with different strictness levels:
- eHDSI Wave validators are calibrated for eHDSI documents
- EHDS epSOS validators enforce stricter legacy requirements
- Always match the platform to your use case

**Q: Can I manually override the recommended validator?**
**A:** YES! There's a checkbox to disable auto-selection and choose manually from the dropdown.

**Q: What if I get errors in Strict Mode but pass in Permissive Mode?**
**A:** This is NORMAL for documents that:
- Were modified for FHIR conversion
- Use placeholder OIDs (2.999.*)
- Don't fully comply with implementation guides
- Are in development/testing phase

**Q: Which mode should I use for my workflow?**
**A:** General workflow:
1. **Development:** Permissive Mode (quick checks)
2. **Pre-production:** Strict Mode (find issues)
3. **Fix issues:** Iterate in Strict Mode
4. **Production:** Strict Mode must pass

---

## Related Documentation
- [EHDS_GAZELLE_INTEGRATION.md](EHDS_GAZELLE_INTEGRATION.md) - Platform comparison
- [EHDS_QUICK_REFERENCE.md](EHDS_QUICK_REFERENCE.md) - Platform cheat sheet
- [CDA_TO_FHIR_TRADEOFFS.md](CDA_TO_FHIR_TRADEOFFS.md) - Why modified CDAs fail strict validation
