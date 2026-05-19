# Project Development Guide

## Getting Started

This document provides quick reference for developers working on the HL7 EU Gazelle Validator.

## Initial Setup

1. **Clone and setup environment**
```bash
cd HL7_EU_Gazelle_Validator
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env and add your EVS_API_KEY
```

3. **Install pre-commit hooks**
```bash
pre-commit install
```

## Development Workflow

### Before Starting Work

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
```

### During Development

```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest

# Run specific test
pytest tests/unit/test_validator.py::TestFHIRValidator::test_validator_initialization -v
```

### Before Committing

```bash
# Run full test suite with coverage
pytest --cov=src --cov-report=html

# View coverage report
# Open htmlcov/index.html in browser

# Stage and commit
git add .
git commit -m "feat: add your feature description"
```

Pre-commit hooks will automatically:
- Format code with black
- Check with flake8
- Validate with mypy
- Check for secrets

### Pushing Changes

```bash
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

## Common Tasks

### Adding a New Validator Profile

1. Update `src/validator/validator.py` - add to `profile_mapping`
2. Add test cases in `tests/unit/test_validator.py`
3. Add example resource in `examples/`
4. Update documentation

### Adding Dependencies

```bash
# Add to requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Install
pip install new-package

# Update lockfile
pip freeze > requirements-lock.txt
```

### Creating Tests

```python
# tests/unit/test_new_feature.py
import pytest
from src.validator import FHIRValidator

def test_new_feature(test_config):
    validator = FHIRValidator(config=test_config)
    result = validator.new_feature()
    assert result is not None
```

### Debugging

```bash
# Run with debug logging
python -m src.cli validate example.json --debug

# Check logs
cat logs/validator.log

# Run pytest with output
pytest -v -s
```

## Project Structure Reference

```
src/
├── validator/
│   ├── api_client.py       # EVS API communication
│   ├── validator.py        # Core validation logic
│   ├── fhir_parser.py      # FHIR parsing
│   └── report_generator.py # Report formatting
├── utils/
│   ├── config.py           # Configuration
│   ├── logger.py           # Logging setup
│   └── exceptions.py       # Custom exceptions
└── cli.py                  # CLI interface

tests/
├── unit/                   # Unit tests
├── integration/            # Integration tests
├── fixtures/               # Test data
└── conftest.py            # Pytest configuration
```

## Useful Commands

```bash
# Run validator
python -m src.cli validate examples/patient_example.json

# List validators
python -m src.cli list-validators

# Validate directory
python -m src.cli validate-dir examples/

# Check project structure
tree /F

# Find TODO comments
grep -r "TODO" src/

# Check dependencies
pip list --outdated
```

## Code Quality Metrics

- **Test Coverage**: Target >80%
- **Linting**: Must pass flake8
- **Type Coverage**: Must pass mypy
- **Formatting**: Must pass black

Check all:
```bash
black src/ tests/ && flake8 src/ tests/ && mypy src/ && pytest --cov=src
```

## Resources

- [Project Instructions](.github/copilot.instructions.md)
- [EVS Documentation](https://gazelle.ehdsi.eu/gazelle-documentation/)
- [FHIR Specification](https://hl7.org/fhir/)
- [Python Best Practices](https://peps.python.org/pep-0008/)

## Need Help?

1. Check `README.md` for installation and usage
2. Read `.github/copilot.instructions.md` for development guidelines
3. Search existing issues on GitHub
4. Contact EVS support for API questions
