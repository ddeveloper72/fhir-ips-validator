# [HL7 EU Gazelle Validator](https://ddeveloper72-fhir-ips-validator-streamlit-app-ocgntm.streamlit.app/)

A Python-based validation tool for HL7 FHIR and CDA documents using both **eHDSI Gazelle** and **EHDS Gazelle** validation platforms.

## Overview

This tool enables developers and healthcare professionals to validate FHIR resources and CDA documents against multiple Gazelle validation services, ensuring compliance with healthcare interoperability standards.

### Supported Platforms

#### 🏥 eHDSI Gazelle (Original)
- **URL:** https://gazelle.ehdsi.eu
- **Focus:** CDA validation, eHDSI Wave 7-10, Cross-border eHealth
- **Formats:** CDA R2 (L1, L3), XDS, SAML
- **Status:** ✅ Fully integrated (SOAP API)

#### 🇪🇺 EHDS Gazelle (New)
- **URL:** https://ehds.gazelle-platform.net
- **Focus:** FHIR validation, HL7 EU standards, Modern EU healthcare
- **Validators:**
  - Standard 12: International Patient Summary (IPS)
  - Standard 15: HL7 EU Patient Summary (EU-EPS)
  - Standard 17: HL7 EU Base and Core
- **Status:** 🚧 Integration in progress
- **Docs:** See [EHDS Integration Guide](docs/EHDS_GAZELLE_INTEGRATION.md)

### Supported Validators

The eHDSI Gazelle platform provides validators for various healthcare document types and messages. Use the `list-validators` command to see all available validators.

## Features (Planned)

- ✅ Validate single FHIR resources or bundles
- ✅ Batch validation of multiple resources
- ✅ Support for JSON and XML FHIR formats
- ✅ Detailed validation reports with error categorization
- ✅ Command-line interface (CLI)
- ✅ Python API for programmatic use
- ⏳ Web-based validation interface
- ⏳ Offline validation mode
- ⏳ CI/CD pipeline integration

## Installation

### Prerequisites

- Python 3.10 or higher
- eHDSI Gazelle account (register at https://gazelle.ehdsi.eu/gazelle/user-management/registration)
- API key from your account settings

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ddeveloper72/HL7_EU_Gazelle_Validator.git
cd HL7_EU_Gazelle_Validator
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Copy template
cp .env.example .env

# Edit .env and add your eHDSI Gazelle API key
```

## Usage

### Command-Line Interface

```bash
# Validate a single FHIR resource
python -m src.cli validate patient.json --profile patient-summary

# Validate with detailed output
python -m src.cli validate bundle.json --profile hospital-discharge --verbose

# Batch validate directory
python -m src.cli validate-dir ./resources/ --output report.json

# List available validators
python -m src.cli list-validators

# Generate sample FHIR resource
python -m src.cli generate-sample --profile laboratory-report
```

### Python API

```python
from validator import FHIRValidator
from fhir.resources.bundle import Bundle

# Initialize validator
validator = FHIRValidator(api_key="your_key")

# Load FHIR bundle
with open('bundle.json') as f:
    bundle = Bundle.parse_file('bundle.json')

# Validate
result = validator.validate(
    bundle, 
    profile="hl7-eu-hospital-discharge"
)

# Check results
if result.is_valid:
    print("✅ Validation passed")
else:
    print(f"❌ Found {len(result.errors)} errors")
    for error in result.errors:
        print(f"  - {error.message} (line {error.line})")
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for available options:

- `EVS_API_KEY`: Your eHDSI Gazelle API key (required)
- `EVS_BASE_URL`: EVS API endpoint (default: https://gazelle.ehdsi.eu)
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `STRICT_MODE`: Treat warnings as errors (true/false)

## Development

### Running Tests

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_validator.py

# Run integration tests (requires API credentials)
pytest tests/integration/ -m integration
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
HL7_EU_Gazelle_Validator/
├── src/
│   ├── validator/          # Core validation logic
│   ├── utils/             # Utilities
│   └── cli.py             # CLI interface
├── tests/                 # Test suite
├── examples/              # Sample FHIR resources
├── docs/                  # Documentation
└── .github/              # GitHub configuration
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## Resources

- [eHDSI Gazelle Portal](https://gazelle.ehdsi.eu/)
- [EVS Validation Portal](https://gazelle.ehdsi.eu/evs)
- [EVS API Documentation](https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html)
- [HL7 FHIR Specification](https://hl7.org/fhir/)
- [eHealth Digital Service Infrastructure](https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/eHealth)

## Troubleshooting

### Common Issues

**Issue**: `Authentication failed`  
**Solution**: Verify your API key in `.env` file. You can generate/manage API keys from your eHDSI Gazelle account settings.

**Issue**: `Validator not found`  
**Solution**: Run `python -m src.cli list-validators` to see available validators on the eHDSI platform.

**Issue**: `Connection timeout`  
**Solution**: Check your internet connection and increase `REQUEST_TIMEOUT` in `.env`.

### Getting Help

- Check the [documentation](docs/)
- Search [existing issues](https://github.com/ddeveloper72/HL7_EU_Gazelle_Validator/issues)
- Visit the eHDSI Gazelle portal for platform-specific help

## License

[Specify License - MIT, Apache 2.0, etc.]

## Acknowledgments

- IHE Europe for the Gazelle platform
- HL7 Europe for FHIR implementation guides
- European Health Data Space initiative

---

**Status**: 🚧 Under Active Development  
**Version**: 0.1.0-alpha  
**Last Updated**: March 2026
