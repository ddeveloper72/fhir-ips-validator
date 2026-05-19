# 🏥 FHIR IPS Bundle Validator

**A web-based validation tool for FHIR International Patient Summary (IPS) bundles and CDA documents**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.57-FF4B4B?style=flat&logo=streamlit)](https://streamlit.io/)

---

## 🚀 **Try It Now**

👉 **[Launch Web App](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)**

No installation required! Upload your FHIR bundle (JSON) or CDA document (XML) and get instant validation results.

---

## 📋 **Overview**

This web application provides **comprehensive validation** for healthcare interoperability documents using **free public validation services** and optional private Azure integration:

### 🌐 **Public Validators** (No Registration Required)
- ✅ **EHDS Matchbox** - Specialized FHIR IPS validation with 21 profiles (**Default**)
- ✅ **HAPI FHIR Public Server** - Generic FHIR R4 validation (file size limit ~50KB)
- ✅ **Gazelle EVS** - CDA document validation using eHDSI and EHDS platforms (49+ validators)

### 🔐 **Optional Private Validator**
- 🔒 **Azure FHIR Service** - HIPAA/GDPR compliant validation (requires your Azure credentials)

Perfect for developers, healthcare professionals, and organizations working with **FHIR International Patient Summary (IPS)** or **Clinical Document Architecture (CDA)** standards.

---

## 🎯 **Which Validator Should I Use?**

| Use Case | Recommended Validator | Why? |
|----------|---------------------|------|
| **Testing/IPS** | 🌐 **EHDS Matchbox** (Default) | Free, IPS-specific, 21 profiles, handles large files |
| **Small FHIR** | 🌐 **HAPI FHIR (Public)** | Free, generic FHIR, ~50KB limit |
| **CDA Documents** | 🌐 **Gazelle EVS** | 49+ validators for eHDSI/EHDS |
| **Production/HIPAA** | 🔒 **Azure FHIR** | Private, compliant, requires credentials |

Perfect for developers, healthcare professionals, and organizations working with **FHIR International Patient Summary (IPS)** or **Clinical Document Architecture (CDA)** standards.

---

## ✨ **Key Features**

### 📁 **File Upload & Validation**
- ✅ **Drag-and-drop file upload** for JSON and XML documents
- ✅ **Maximum file size:** 10MB per file
- ✅ **Supported formats:**
  - JSON: FHIR R4 bundles
  - XML: CDA R2 documents
- ✅ **Pre-validation checks:**
  - File size validation (prevents crashes with large files)
  - JSON/XML format validation (shows line-specific errors)
  - Automatic format detection and validator switching

### 🔍 **Four Validation Services**

#### 1. **EHDS Matchbox FHIR IPS Validator** (JSON Only) 🌐 **DEFAULT**
- **FREE & Public** - No registration or API keys required
- Specialized FHIR IPS validation with **21 profiles**:
  - Bundle (IPS) 1.1.0 and 2.0.0
  - Patient, AllergyIntolerance, Condition, Device, etc.
- Validates specific IPS sections (Medication Summary, Allergies, Problem List, etc.)
- ✅ Handles large files (tested up to 10MB)
- Fast validation (~10 seconds)
- Human-readable diagnostic messages
- Best for: **IPS-specific validation** (recommended)

#### 2. **HAPI FHIR Public Server** (JSON Only) 🌐 **ALTERNATIVE**
- **FREE & Anonymous** - No registration or API keys required
- Validates FHIR R4 resources via http://hapi.fhir.org
- REST API-based validation
- Fast validation (<5 seconds)
- ⚠️ **File size limit: ~50KB** (public server constraint)
- Best for: Small FHIR resources, quick checks
- **Not suitable for typical IPS bundles** (usually >100KB)

#### 3. **Azure FHIR Service** (JSON Only) 🔒 **OPTIONAL**
- **HIPAA/GDPR compliant** - Requires your Azure credentials
- Validates FHIR R4 resources via Azure Health Data Services
- OAuth2-based authentication
- Private validation in your own Azure environment
- Best for: Production use, sensitive patient data
- 💡 **Setup:** Provide credentials in sidebar or deploy via Docker

#### 3. **EHDS Matchbox FHIR IPS Validator** (JSON Only) 🌐 **PUBLIC**
- Specialized FHIR IPS validation with **21 profiles**:
  - Bundle (IPS) 1.1.0 and 2.0.0
  - Patient (IPS)
  - AllergyIntolerance (IPS)
  - Condition (IPS)
  - Device (IPS)
  - DeviceUseStatement (IPS)
  - DiagnosticReport (IPS)
  - ImagingStudy (IPS)
  - Immunization (IPS)
  - Media (IPS)
  - Medication (IPS)
  - MedicationRequest (IPS)
  - MedicationStatement (IPS)
  - Observation (IPS) - Multiple profiles
  - Organization (IPS)
  - Practitioner (IPS)
  - PractitionerRole (IPS)
  - Procedure (IPS)
  - Specimen (IPS)
- **Validates specific IPS sections:**
  - Medication Summary
  - Allergies and Intolerances
  - Problem List
  - Immunizations
  - History of Procedures
  - Medical Devices
  - Diagnostic Results (Laboratory, Radiology, Pathology)
  - Vital Signs
  - Pregnancy Information
  - Social History
  - Plan of Care
  - Advance Directives
- Fast validation (~10 seconds)
- Human-readable diagnostic messages

#### 4. **Gazelle EVS** (XML Only) 🌐 **PUBLIC**
- **FREE & Anonymous** - No registration required
- **Two platforms:**
  - **eHDSI Gazelle** (49 validators): Wave 7-10, Cross-border eHealth
  - **EHDS Gazelle** (32 validators): Modern HL7 EU standards
- **Validation modes:**
  - **Strict (Recommended):** Full compliance with implementation guides
  - **Permissive (Basic):** CDA R2 structure validation only
- **Intelligent auto-detection:** Analyzes templateId elements to recommend correct validator
- **Document types supported:**
  - Patient Summary (PS)
  - ePrescription (eP)
  - eDispensation (eD)
  - Hospital Discharge Reports
  - Laboratory Reports
  - Imaging Reports
  - And many more...

### 📊 **Detailed Error Reports**

- ✅ **Tabbed interface** with three severity levels:
  - ❌ **Errors:** Critical issues that prevent validation
  - ⚠️ **Warnings:** Potential problems or best practice violations
  - ℹ️ **Information:** Helpful notes and suggestions
- ✅ **Rich diagnostic information:**
  - Line numbers and column positions
  - FHIR expression paths (e.g., `Bundle.entry[0].resource`)
  - Human-readable error messages (not technical jargon)
  - Context-specific help and recovery suggestions
- ✅ **Multiple result formats:**
  - XSD validation errors (schema violations)
  - Schematron validation results (business rule violations)
  - FHIR OperationOutcome parsing (structured FHIR errors)
- ✅ **Persistent reports:** Links to Gazelle web UI for CDA validation results
- ✅ **Export capabilities:** Download full validation reports

### 🎯 **Smart Features**

- ✅ **Auto-validator switching:** Detects file type and recommends appropriate validator
- ✅ **Example files included:** Try validation without uploading your own files
- ✅ **API timeout handling:** 60-second timeout prevents hanging on slow networks
- ✅ **Network error recovery:** User-friendly error messages with actionable recovery steps
- ✅ **Secret validation:** Startup checks warn if API keys are missing or expiring
- ✅ **Rate limit handling:** Graceful handling of API rate limits

---

## 🎬 **Quick Start**

### **Option 1: Use the Web App (Recommended)**

1. **Visit:** [https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)
2. **Choose a validator** from the sidebar (Azure FHIR, EHDS Matchbox, or Gazelle EVS)
3. **Upload your file** or try an example
4. **Click "Validate"** and review results

### **Option 2: Run Locally**

#### Prerequisites

- Python 3.12 or higher
- **Optional:** Azure FHIR credentials (only if you want private validation)

> 🌐 **Note:** Public validators (EHDS Matchbox, HAPI FHIR, Gazelle EVS) work without any credentials!

#### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/ddeveloper72/fhir-ips-validator.git
cd fhir-ips-validator
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables (Optional):**

Create a `.env` file **only if you have Azure FHIR credentials**:

```env
# Azure FHIR Service (Optional - for private validation)
AZURE_FHIR_BASE_URL=your-fhir-service.fhir.azurehealthcareapis.com
AZURE_FHIR_CLIENT_ID=your-client-id
AZURE_FHIR_CLIENT_SECRET=your-client-secret
AZURE_FHIR_TENANT_ID=your-tenant-id

# Application Configuration
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
API_TIMEOUT_SECONDS=60
```

> 🌐 **Skip this step** if you only want to use public validators (EHDS Matchbox, HAPI FHIR, Gazelle EVS)

5. **Run the app:**
```bash
streamlit run streamlit_app.py
```

6. **Open your browser:** http://localhost:8501

---

## 🐳 **Deployment Options**

### **Comparison: Public Validators vs Docker Deployment**

| Feature | Streamlit Cloud (Demo) | Docker Self-Hosted |
|---------|----------------------|-------------------|
| **Deployment Complexity** | ⭐ One-click | ⭐⭐ Docker required |
| **Validators** | 🌐 All public validators | 🌐 Public + 🔐 Azure FHIR (optional) |
| **Credentials Required** | ❌ None | ❌ None (Azure optional) |
| **Cost** | ✅ Free | 💵 Hosting only |
| **Data Privacy** | ⚠️ Public validators | ✅ Your infrastructure |
| **Production Ready** | ✅ Yes (public validators) | ✅ Yes (full control) |
| **Best For** | Testing, demos, education | Healthcare orgs, production |

### **Option 1: Streamlit Cloud (Public Validators)**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)

✅ **No setup required** - Just click the link above  
✅ **Free to use** - No infrastructure costs  
🌐 **Public validators** - EHDS Matchbox, HAPI FHIR, Gazelle EVS  
🔐 **Optional Azure FHIR** - Provide your own credentials via sidebar

**Features:**
- All public validators work immediately
- Optionally provide Azure FHIR credentials (stored in browser session only)
- Perfect for testing, demos, and education
- Suitable for non-sensitive data validation

### **Option 2: Docker Self-Hosted**

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker)](https://hub.docker.com/)

✅ **Full control** - Deploy in your infrastructure  
✅ **Public validators included** - Works immediately  
✅ **Optional Azure FHIR** - Add your credentials for private validation  
✅ **Production ready** - HIPAA/GDPR compliant when using Azure FHIR  
✅ **HIPAA/GDPR compliant** - Suitable for healthcare data

#### **Quick Start**

```bash
# 1. Clone repository
git clone https://github.com/ddeveloper72/fhir-ips-validator.git
cd fhir-ips-validator

# 2. Configure credentials
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker Compose
docker-compose up -d

# 4. Open browser
http://localhost:8501
```

#### **Docker Features**

- ✅ Multi-stage build for minimal image size
- ✅ Non-root user for security
- ✅ Health checks built-in
- ✅ Environment-based configuration
- ✅ Volume mounting for example files
- ✅ Ready for Kubernetes deployment

#### **Full Documentation**

📖 See **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** for complete guide including:
- Prerequisites and API key setup
- docker-compose deployment
- Kubernetes deployment examples
- AWS/Azure/GCP deployment guides
- Security best practices
- Monitoring and troubleshooting

---

## 🏗️ **Architecture**

### **Validation Services**

```
┌─────────────────────────────────────────────────────────┐
│           Streamlit Web Interface                        │
│  (File Upload, Validator Selection, Results Display)    │
└─────────────────┬───────────────────────────────────────┘
                  │
          ┌───────┴────────┐
          │  Auto-Detection │
          │  (JSON → FHIR)  │
          │  (XML → CDA)    │
          └───────┬─────────┘
                  │
     ┌────────────┼────────────┐
     │            │            │
┌────▼────┐  ┌───▼────┐  ┌───▼────────┐
│ Azure   │  │ EHDS   │  │ Gazelle    │
│ FHIR    │  │ Match- │  │ EVS SOAP   │
│ REST    │  │ box    │  │ (eHDSI &   │
│ API     │  │ REST   │  │  EHDS)     │
└─────────┘  └────────┘  └────────────┘
```

### **File Processing Flow**

1. **Upload** → File validation (size, format)
2. **Parse** → JSON/XML parsing with error detection
3. **Auto-detect** → Recommend appropriate validator
4. **Validate** → Call selected validation service (with timeout)
5. **Parse results** → Extract errors/warnings/info
6. **Display** → Human-readable tabbed interface

---

## 📖 **Usage Examples**

### **Validating a FHIR IPS Bundle**

1. Select **"EHDS Matchbox (IPS Validator)"** from sidebar
2. Choose IPS profile (e.g., "Bundle (IPS) 2.0.0")
3. Upload your FHIR bundle JSON file
4. Click **"🔍 Validate with EHDS Matchbox"**
5. Review results in the tabbed interface

### **Validating a CDA Patient Summary**

1. Select **"Gazelle EVS"** from sidebar
2. Choose **"eHDSI Gazelle"** platform
3. Select **"Strict (Recommended)"** validation mode
4. Upload your CDA XML file (app auto-detects document type)
5. Review recommended validator or manually override
6. Click **"🔍 Validate Document"**
7. Review results and access Gazelle web UI link

---

## 🛠️ **Project Structure**

```
HL7_EU_Gazelle_Validator/
├── streamlit_app.py              # Main web application
├── scripts/
│   ├── validate_with_azure_fhir.py    # Azure FHIR validation
│   ├── validate_with_matchbox.py      # EHDS Matchbox validation
│   ├── test_evs_validation.py         # Gazelle EVS SOAP validation
│   └── detect_cda_type.py             # CDA auto-detection
├── examples/                     # Sample FHIR/CDA files
│   ├── Diana_Ferreira_bundle.json
│   ├── Patrick_Murphy_bundle.json
│   └── *.xml                     # CDA examples
├── docs/                         # Documentation
│   ├── ROBUSTNESS_TESTING.md     # Test plan
│   ├── ROBUSTNESS_FIXES.py       # Implementation guide
│   └── IMPLEMENTATION_GUIDE.md   # Step-by-step fixes
├── .streamlit/
│   └── secrets.toml              # Streamlit Cloud secrets
├── requirements.txt              # Python dependencies
└── .env                          # Local environment variables
```

---

## 🧪 **Testing**

The app includes comprehensive robustness testing:

- ✅ File size validation (10MB limit)
- ✅ JSON/XML format validation
- ✅ API timeout handling (60 seconds)
- ✅ Network error recovery
- ✅ Rate limit handling
- ✅ Missing credential detection
- ✅ API key expiry warnings

See [ROBUSTNESS_TESTING.md](ROBUSTNESS_TESTING.md) for detailed test plan.

---

## 🤝 **Contributing**

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Commit Convention**

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `ui:` UI/UX improvements
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

---

## 📚 **Resources & Documentation**

### **Validation Services**
- [Azure FHIR Service](https://learn.microsoft.com/en-us/azure/healthcare-apis/fhir/)
- [EHDS Matchbox FHIR Validator](https://ehds.gazelle-platform.net/matchboxv3/fhir)
- [eHDSI Gazelle Portal](https://gazelle.ehdsi.eu/)
- [EHDS Gazelle Platform](https://ehds.gazelle-platform.net/)

### **Standards & Specifications**
- [HL7 FHIR R4 Specification](https://hl7.org/fhir/R4/)
- [IPS Implementation Guide](http://hl7.org/fhir/uv/ips/)
- [CDA R2 Specification](http://www.hl7.org/implement/standards/product_brief.cfm?product_id=7)
- [eHDSI Implementation Guides](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eHealth)

### **Gazelle Documentation**
- [EVS Validation Portal](https://gazelle.ehdsi.eu/evs)
- [EVS SOAP API Documentation](https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html)
- [Gazelle API Key Management](https://gazelle.ehdsi.eu/gazelle/user-management/api-keys)

---

## 🔧 **Troubleshooting**

### **Common Issues**

**Issue:** File upload fails  
**Solution:** Check file size (<10MB) and format (valid JSON/XML)

**Issue:** Azure validation fails with 401 Unauthorized  
**Solution:** Verify your Azure credentials in `.env` or Streamlit secrets

**Issue:** Gazelle validation times out  
**Solution:** Check internet connection. Large documents may take 30+ seconds.

**Issue:** "No module named 'streamlit'"  
**Solution:** Activate virtual environment and run `pip install -r requirements.txt`

**Issue:** API key expiring soon warning  
**Solution:** Generate new API key from Gazelle portal before expiration

### **Getting Help**

- 📖 Check [documentation](docs/)
- 🐛 Search [existing issues](https://github.com/ddeveloper72/fhir-ips-validator/issues)
- 💬 Create a new issue with error details
- 📧 Contact eHDSI Gazelle support for platform issues

---

## 📄 **License**

[Specify License - MIT, Apache 2.0, etc.]

---

## 🙏 **Acknowledgments**

- **IHE Europe** for the Gazelle testing platform
- **HL7 International** for FHIR and IPS specifications
- **HL7 Europe** for European FHIR implementation guides
- **European Health Data Space (EHDS)** initiative
- **Microsoft Azure** for Azure Health Data Services
- **Streamlit** for the excellent web framework

---

## 📊 **Status**

- **Version:** 1.0.0
- **Status:** ✅ Production Ready
- **Last Updated:** May 2026
- **Live App:** [Launch Validator](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)

---

<div align="center">
  <strong>Built with ❤️ for the healthcare interoperability community</strong>
</div>
