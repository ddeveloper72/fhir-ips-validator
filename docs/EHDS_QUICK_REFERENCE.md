# EHDS Gazelle Quick Reference

## 🚀 Quick Start

### 1. API Key Setup
```bash
# Already configured in .env:
EHDS_GAZELLE_BASE_URL=https://ehds.gazelle-platform.net
EHDS_GAZELLE_API_KEY=3ZOyR...V8E7 (expires 6/16/26)
```

### 2. Run Exploration
```bash
# Activate virtual environment
.venv\Scripts\activate

# Discover available validators
python scripts/explore_ehds_gazelle.py
```

### 3. Check Results
```bash
# View discovered endpoints
ls logs/ehds_api_exploration/
```

---

## 📍 Validator Endpoints

### Standard 12: IPS (International)
```
https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=12
```
**Use for:** FHIR IPS bundles, international patient summaries

**Example files:**
- `examples/Diana_Ferreira_bundle.json`
- `examples/Patrick_Murphy_bundle.json`

---

### Standard 15: EU-EPS (European)
```
https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=15
```
**Use for:** EU-specific patient summaries, MyHealth@EU

**Key differences from IPS:**
- EU terminology bindings
- eHDSI identifiers required
- Additional EU extensions

---

### Standard 17: EU Base & Core
```
https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=17
```
**Use for:** Individual FHIR resources with EU base profiles

**Validates:**
- Patient (EU Base)
- Organization (EU Base)
- Practitioner (EU Base)
- Observation (EU Base)

---

## 🔧 Command Cheat Sheet

```bash
# List all known standards
python scripts/explore_ehds_gazelle.py --list-all

# Explore specific standard
python scripts/explore_ehds_gazelle.py --standard 12   # IPS
python scripts/explore_ehds_gazelle.py --standard 15   # EU-EPS
python scripts/explore_ehds_gazelle.py --standard 17   # Base

# Discover API endpoints
python scripts/explore_ehds_gazelle.py --discover

# Try SOAP/WSDL services
python scripts/explore_ehds_gazelle.py --soap

# Full exploration (all of the above)
python scripts/explore_ehds_gazelle.py
```

---

## 🎯 Use Case Selection

| If you have... | Use Standard | Platform |
|----------------|--------------|----------|
| **FHIR IPS Bundle** | 12 (IPS) | EHDS Gazelle |
| **EU Patient Summary** | 15 (EU-EPS) | EHDS Gazelle |
| **Individual FHIR resource** | 17 (Base) | EHDS Gazelle |
| **CDA eHDSI Wave 7-10** | N/A | Original Gazelle |
| **CDA L1-L3 validation** | N/A | Original Gazelle |

---

## 🆚 Platform Comparison

### When to use **eHDSI Gazelle** (original)
- ✅ CDA document validation
- ✅ eHDSI Wave 7/9/10 compliance
- ✅ Cross-border CDA exchange
- ✅ Legacy system integration

### When to use **EHDS Gazelle** (new)
- ✅ FHIR IPS validation
- ✅ EU-specific FHIR profiles
- ✅ Modern HL7 EU standards
- ✅ EHDS regulation compliance

---

## 📋 Next Steps

1. **Explore Platform:**
   ```bash
   python scripts/explore_ehds_gazelle.py
   ```

2. **Review Results:**
   - Check `logs/ehds_api_exploration/` folder
   - Identify working API endpoints
   - Note authentication requirements

3. **Document Findings:**
   - Update `docs/EHDS_GAZELLE_INTEGRATION.md`
   - Add actual API endpoint formats
   - Document request/response examples

4. **Implement Integration:**
   - Create `scripts/validate_with_ehds.py`
   - Add EHDS option to Streamlit app
   - Test with example documents

---

## 🔗 Important URLs

| Resource | URL |
|----------|-----|
| **EHDS Platform** | https://ehds.gazelle-platform.net |
| **API Key Management** | https://ehds.gazelle-platform.net/evs/administration/apiKeyManagement.seam |
| **IPS Validator** | https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=12 |
| **EU-EPS Validator** | https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=15 |
| **EU Base Validator** | https://ehds.gazelle-platform.net/evs/default/validator.seam?standard=17 |
| **Registration** | https://ehds.gazelle-platform.net/gazelle/user-management/registration |

---

## ⚠️ Troubleshooting

### API Key Not Working
```bash
# Check configuration
cat .env | grep EHDS

# Verify key expiry
# Current key expires: 6/16/26 12:00:00 AM

# Regenerate if needed at:
# https://ehds.gazelle-platform.net/evs/administration/apiKeyManagement.seam
```

### Endpoint Not Found
```bash
# Run discovery to find actual endpoints
python scripts/explore_ehds_gazelle.py --discover

# Check saved responses
ls -la logs/ehds_api_exploration/

# Review HTML/JSON responses for API documentation
```

### Authentication Required
```bash
# The platform may require web-based login + session cookies
# API key alone might not be sufficient for all endpoints
# Check exploration results for redirect patterns
```

---

## 📚 Documentation

- **Integration Guide:** `docs/EHDS_GAZELLE_INTEGRATION.md`
- **Exploration Script:** `scripts/explore_ehds_gazelle.py`
- **Environment Config:** `.env` (configured ✅)
- **Example Documents:** `examples/` folder

---

## ✅ Status

- [x] Environment variables configured
- [x] API key generated (expires 6/16/26)
- [x] Exploration script created
- [x] Documentation written
- [ ] Discovery run needed
- [ ] API endpoints identified
- [ ] Integration script created
- [ ] Streamlit UI updated
