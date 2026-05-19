# HL7 EU Gazelle Validator - AI Agent Development Guide

## Project Overview

This project develops a Python-based validation tool for HL7 FHIR bundles and resources against the eHDSI (eHealth Digital Service Infrastructure) Gazelle validation services. The tool provides automated validation with clear feedback for developers and healthcare professionals.

### Key Objectives
- Validate FHIR bundles/resources against available Gazelle validators
- Support eHealth Digital Service Infrastructure compliance
- Provide user-friendly command-line and programmatic interfaces
- Generate detailed validation reports with actionable feedback
- Enable batch validation of multiple resources
- Support both online (API) and offline validation modes

## Project Context & Resources

### Primary Resources
- **eHDSI Gazelle Portal**: https://gazelle.ehdsi.eu/
- **EVS Validation Portal**: https://gazelle.ehdsi.eu/evs
- **EVS Web Service API Documentation**: https://gazelle.ehdsi.eu/gazelle-documentation/EVS-Client/wsvalidation.html
- **Gazelle Maven Client**: https://gazelle.ihe.net/nexus/ (for Java reference implementation)

### Authentication & API Access
- **Registration**: Register at https://gazelle.ehdsi.eu/gazelle/user-management/registration
- **API Key Management**: Manage your API keys after login through your account settings
- **Store Credentials Securely**: Use environment variables (.env file) - NEVER hardcode

### Supported Implementation Guides

The eHDSI Gazelle platform provides validators for:
- CDA (Clinical Document Architecture) documents
- ATNA (Audit Trail and Node Authentication) logging messages
- XD* metadata (XDS/XDR)
- DSUB messages
- HPD messages
- SVS messages
- HL7v3 messages
- XDW documents
- SAML assertions
- Other IHE profiles

**Note**: The specific validators available may vary. Use the `list-validators` command to see current options.

### Related Projects (Reference Only)
- **HL7v2 Validator**: https://github.com/ddeveloper72/HL7_v2_Message_Validator-Auto-Correct
- **Django NCP (FHIR samples)**: https://github.com/ddeveloper72/Django_NCP
  - Use FHIR resource samples from this project for test data
  - Do NOT use Django framework - this is a standalone CLI tool

## EVS API Integration

### Authentication & Access
- **Registration Required**: Register at https://gazelle.ehdsi.eu/gazelle/user-management/registration
- **API Authentication**: Use API key from your account settings
- **Store Credentials Securely**: Use environment variables (.env file) - NEVER hardcode

### Web Service Endpoints
The EVS uses SOAP-based web services with the following key methods:

#### Core API Methods
1. **validateDocument** - Validate XML/JSON FHIR document
   - Parameters: `document` (string), `validator` (string)
   - Returns: XML validation result structure
   
2. **validateBase64Document** - Validate base64-encoded document
   - Parameters: `base64Document` (string), `validator` (string)
   - Returns: XML validation result structure

3. **getListOfValidators** - Retrieve available validators
   - Parameters: `discriminator` (optional filter)
   - Returns: List of validator names

4. **about** - Get service information
   - Returns: Service metadata

### WSDL Locations (for SOAP client generation)
- FHIR Validators: Check EVS portal for current endpoint
- General Pattern: `https://{service}.gazelle-platform.net/{module}/ModelBasedValidationWSService/ModelBasedValidationWS?wsdl`

### Request/Response Handling
- **Input Formats**: JSON (FHIR), XML (FHIR), Base64-encoded
- **Output Format**: XML structure with validation results
- **Error Codes**: Parse XML response for errors, warnings, and informational messages
- **Batch Processing**: Implement queue-based validation for multiple resources

## Project Architecture

### Recommended Structure
```
HL7_EU_Gazelle_Validator/
├── .github/                    # GitHub workflows & instructions
├── .venv/                      # Virtual environment (not tracked)
├── src/
│   ├── validator/
│   │   ├── __init__.py
│   │   ├── api_client.py      # EVS API communication
│   │   ├── fhir_parser.py     # FHIR resource parsing
│   │   ├── validator.py       # Core validation logic
│   │   └── report_generator.py # Validation report formatting
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── logger.py          # Logging utilities
│   │   └── exceptions.py      # Custom exceptions
│   └── cli.py                 # Command-line interface
├── tests/
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   ├── fixtures/              # Test FHIR resources
│   └── conftest.py            # Pytest configuration
├── examples/                  # Example FHIR resources
├── docs/                      # Additional documentation
├── .env.example               # Template for environment variables
├── .gitignore
├── requirements.txt           # Production dependencies
├── requirements-dev.txt       # Development dependencies
├── setup.py or pyproject.toml # Package configuration
└── README.md
```

### Core Components

#### 1. API Client (`api_client.py`)
- Implement SOAP client using `zeep` library
- Handle authentication (session tokens or API keys)
- Retry logic with exponential backoff for transient failures
- Connection pooling for batch operations
- Parse XML responses into Python dictionaries
- Cache validator lists to minimize API calls

#### 2. FHIR Parser (`fhir_parser.py`)
- Use `fhir.resources` library for FHIR R4/R5 support
- Validate JSON schema before API submission
- Extract resource type, profile, and meta information
- Convert between FHIR JSON and XML as needed
- Handle Bundle resources (extract individual entries)

#### 3. Validator (`validator.py`)
- Select appropriate validator based on FHIR profile
- Pre-validation checks (schema validation, profile detection)
- Submit to EVS API and parse results
- Categorize errors: ERROR, WARNING, INFO
- Map validation results to FHIR resources (line numbers, paths)

#### 4. Report Generator (`report_generator.py`)
- Generate human-readable reports (console, HTML, JSON)
- Color-coded console output for errors/warnings
- Export results in standard formats (JSON, XML, CSV)
- Summary statistics (pass/fail rates, error categories)

## Python Environment & Dependencies

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### Core Dependencies
```
# API & Web Services
zeep>=4.2.1              # SOAP client
requests>=2.31.0         # HTTP requests
requests-cache>=1.1.0    # API response caching

# FHIR Libraries
fhir.resources>=7.0.0    # FHIR R4/R5 models
fhirclient>=4.1.0        # FHIR client utilities

# Data Processing
pydantic>=2.5.0          # Data validation
python-dotenv>=1.0.0     # Environment variables
lxml>=4.9.0              # XML processing
xmltodict>=0.13.0        # XML to dict conversion

# CLI & UI
click>=8.1.0             # CLI framework
rich>=13.0.0             # Beautiful console output
tqdm>=4.66.0             # Progress bars

# Logging & Monitoring
loguru>=0.7.0            # Enhanced logging
structlog>=23.2.0        # Structured logging

# Testing & Dev
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
black>=23.12.0           # Code formatting
flake8>=7.0.0            # Linting
mypy>=1.7.0              # Type checking
```

## Version Control Best Practices

### Git Workflow
1. **Branching Strategy**
   - `main`: Production-ready code
   - `develop`: Integration branch
   - `feature/<name>`: New features
   - `bugfix/<name>`: Bug fixes
   - `hotfix/<name>`: Critical production fixes

2. **Commit Guidelines**
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
   - Example: `feat: add support for Laboratory Report validation`
   - Keep commits atomic and focused
   - Reference issue numbers: `fix: resolve #42 - handle empty bundle`

3. **Pre-commit Hooks** (recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```
   - Auto-format with black
   - Run flake8 linting
   - Check for secrets/API keys

### .gitignore Essentials
```
# Virtual environment
.venv/
venv/

# Environment variables
.env
.env.local
*.env

# Credentials
credentials.json
api_keys.txt

# Test outputs
.pytest_cache/
htmlcov/
.coverage

# IDE
.vscode/
.idea/
*.swp

# Python
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
```

## Testing Strategy

### Test Levels
1. **Unit Tests** (`tests/unit/`)
   - Test individual functions/classes in isolation
   - Mock API calls using `pytest-mock`
   - Focus on business logic, parsers, validators
   - Target: >80% code coverage

2. **Integration Tests** (`tests/integration/`)
   - Test API client against EVS (or mock server)
   - Validate end-to-end workflows
   - Use real FHIR samples from `examples/`
   - May require API credentials in CI/CD

3. **Fixtures** (`tests/fixtures/`)
   - Valid FHIR resources (various profiles)
   - Invalid FHIR resources (missing fields, wrong profiles)
   - EVS API response samples (success, errors)

### Pytest Configuration (`conftest.py`)
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_api_client():
    """Mock EVS API client for unit tests"""
    client = Mock()
    client.validate_document.return_value = {
        'valid': True,
        'errors': []
    }
    return client

@pytest.fixture
def sample_bundle():
    """Load sample FHIR Bundle for testing"""
    with open('tests/fixtures/hospital_discharge_bundle.json') as f:
        return json.load(f)
```

### Running Tests
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_validator.py

# Run with verbose output
pytest -v

# Run only integration tests
pytest tests/integration/ -m integration
```

## Code Quality Standards

### PEP 8 Compliance
- Use `black` for automatic formatting (line length: 88)
- Use `flake8` for linting (max line length: 100)
- Use `mypy` for type checking
- Run checks before commits:
  ```bash
  black src/ tests/
  flake8 src/ tests/
  mypy src/
  ```

### Type Hints
```python
from typing import List, Dict, Optional
from fhir.resources.bundle import Bundle

def validate_bundle(
    bundle: Bundle,
    validator_name: str,
    strict: bool = False
) -> Dict[str, any]:
    """
    Validate FHIR Bundle against specified validator.
    
    Args:
        bundle: FHIR Bundle resource
        validator_name: Name of EVS validator
        strict: If True, warnings are treated as errors
        
    Returns:
        Dictionary with validation results
        
    Raises:
        ValidationError: If bundle is malformed
        APIError: If EVS request fails
    """
    pass
```

### Code Organization Principles
- **Single Responsibility**: Each class/function has one clear purpose
- **Dependency Injection**: Pass dependencies (API clients, configs) as parameters
- **Avoid Global State**: No module-level mutable variables
- **Error Handling**: Use custom exceptions, not bare `Exception`
- **Logging**: Use structured logging, not `print()` statements

## Documentation Standards

### Docstring Format (Google Style)
```python
def parse_validation_response(xml_response: str) -> ValidationResult:
    """Parse EVS XML validation response into structured format.
    
    Extracts error messages, line numbers, and severity levels from
    the XML response returned by the EVS validation service.
    
    Args:
        xml_response: Raw XML string from EVS API
        
    Returns:
        ValidationResult object containing parsed errors and warnings
        
    Raises:
        XMLParseError: If response is not valid XML
        
    Example:
        >>> xml = '<ValidationResult>...</ValidationResult>'
        >>> result = parse_validation_response(xml)
        >>> print(result.error_count)
        3
    """
    pass
```

### README.md Must Include
- Project description and objectives
- Installation instructions
- Configuration (environment variables)
- Usage examples (CLI commands, Python API)
- Supported FHIR profiles
- Troubleshooting guide
- Contributing guidelines
- License

## Security & Privacy

### Sensitive Data Management
1. **Environment Variables (.env)**
   ```
   EVS_API_KEY=your_api_key_here
   EVS_BASE_URL=https://gazelle.ehdsi.eu
   LOG_LEVEL=INFO
   ```

2. **Configuration Loading**
   ```python
   from dotenv import load_dotenv
   import os
   
   load_dotenv()
   
   class Config:
       EVS_API_KEY = os.getenv('EVS_API_KEY')
       if not EVS_API_KEY:
           raise ValueError("EVS_API_KEY must be set")
   ```

3. **Security Checklist**
   - ✅ Never commit `.env` files
   - ✅ Use `.env.example` as template (without real values)
   - ✅ Sanitize logs (redact API keys, patient data)
   - ✅ Validate all user inputs
   - ✅ Use HTTPS for all API calls
   - ✅ Implement rate limiting for API calls
   - ✅ Handle PHI (Protected Health Information) according to GDPR/HIPAA

### FHIR Data Privacy
- **De-identification**: Remove/mask patient identifiers before logging
- **Audit Trail**: Log validation requests (without resource content)
- **Access Control**: Limit who can access validation results
- **Retention Policy**: Auto-delete logs after specified period

## AI Agent Development Guidelines

### When Generating Code
1. **Always ask for clarification** if requirements are ambiguous
2. **Propose architecture** before implementing large features
3. **Generate tests alongside code** (test-driven development)
4. **Use type hints** for all function signatures
5. **Add logging statements** for debugging and monitoring
6. **Handle errors gracefully** with meaningful error messages
7. **Document complex logic** with inline comments

### Iterative Development Pattern
```
1. Understand requirement → Ask clarifying questions
2. Design solution → Propose architecture/approach
3. Implement incrementally → Start with core functionality
4. Add tests → Unit tests + integration tests
5. Document → Docstrings + README updates
6. Refactor → Improve code quality
7. Validate → Run tests + linting
```

### Code Review Checklist (for AI-generated code)
- [ ] Follows PEP 8 style guide
- [ ] Has type hints
- [ ] Has docstrings
- [ ] Has unit tests
- [ ] Handles errors appropriately
- [ ] No hardcoded credentials
- [ ] Uses dependency injection
- [ ] Logging instead of print statements
- [ ] No security vulnerabilities

### Common Pitfalls to Avoid
❌ Hardcoding API endpoints or credentials  
❌ Using bare `except:` clauses  
❌ Ignoring return types from functions  
❌ Not validating user input  
❌ Generating code without tests  
❌ Creating overly complex functions (>50 lines)  
❌ Not handling API rate limits  
❌ Forgetting to close resources (use context managers)  

### AI-Assisted Debugging
When encountering errors:
1. Read the full error traceback
2. Check logs for additional context
3. Verify API credentials and connectivity
4. Test with minimal examples
5. Add debug logging statements
6. Use pytest's `-vv` flag for detailed test output

## Continuous Integration (CI/CD)

### GitHub Actions Workflow (recommended)
```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      - name: Lint
        run: |
          black --check src/ tests/
          flake8 src/ tests/
      - name: Type check
        run: mypy src/
      - name: Test
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Performance Considerations

### API Optimization
- **Caching**: Cache validator lists and API responses
- **Batch Processing**: Validate multiple resources in parallel (use `asyncio`)
- **Connection Pooling**: Reuse HTTP connections
- **Rate Limiting**: Respect EVS rate limits (implement backoff)

### Resource Management
```python
from contextlib import contextmanager

@contextmanager
def api_session():
    """Context manager for EVS API session"""
    session = EVSClient()
    try:
        yield session
    finally:
        session.close()

# Usage
with api_session() as client:
    result = client.validate(bundle)
```

## Roadmap & Future Enhancements

### Phase 1: Core Functionality
- CLI tool for single resource validation
- Support for major HL7 EU profiles
- JSON and XML output formats

### Phase 2: Advanced Features
- Batch validation with parallel processing
- Web UI for validation
- Integration with CI/CD pipelines
- Offline validation mode (local schema validation)

### Phase 3: Enterprise Features
- REST API server
- Database for validation history
- Dashboard for analytics
- Integration with EHR systems

---

## Quick Reference

### Common Commands
```bash
# Validate single resource
python -m src.cli validate input.json --profile hospital-discharge

# Batch validate directory
python -m src.cli validate-dir ./resources/ --output report.json

# List available validators
python -m src.cli list-validators

# Generate sample FHIR resource
python -m src.cli generate-sample --profile patient-summary
```

### Getting Help
- EVS Documentation: https://gazelle.ehdsi.eu/gazelle-documentation/
- EVS Support: Contact via Gazelle platform
- FHIR Specification: https://hl7.org/fhir/
- Project Issues: [GitHub Issues](https://github.com/ddeveloper72/HL7_EU_Gazelle_Validator/issues)

---

**Last Updated**: March 2026  
**Maintainer**: Duncan Groenewald  
**License**: [Specify License]
