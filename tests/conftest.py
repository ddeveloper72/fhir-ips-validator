"""
Pytest Configuration

Shared fixtures and configuration for tests.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.validator.api_client import EVSAPIClient
from src.utils.config import Config


@pytest.fixture
def test_config():
    """Fixture providing test configuration."""
    config = Config()
    config.MOCK_API = True
    config.DEBUG = True
    return config


@pytest.fixture
def mock_api_client():
    """Fixture providing mocked EVS API client."""
    client = Mock(spec=EVSAPIClient)
    client.validate_document.return_value = {
        "valid": True,
        "errors": [],
        "warnings": [],
    }
    client.get_list_of_validators.return_value = [
        "hl7-eu-hospital-discharge",
        "hl7-eu-laboratory-report",
        "hl7-eu-patient-summary",
    ]
    return client


@pytest.fixture
def sample_patient_json():
    """Fixture providing sample Patient resource."""
    return {
        "resourceType": "Patient",
        "id": "example",
        "meta": {
            "profile": [
                "http://hl7.eu/fhir/laboratory/StructureDefinition/Patient-eu-lab"
            ]
        },
        "identifier": [{"system": "http://example.org/fhir/sid/patients", "value": "12345"}],
        "name": [{"family": "Doe", "given": ["John"]}],
        "gender": "male",
        "birthDate": "1980-01-01",
    }


@pytest.fixture
def sample_bundle_json():
    """Fixture providing sample Bundle resource."""
    return {
        "resourceType": "Bundle",
        "type": "document",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "name": [{"family": "Test", "given": ["Patient"]}],
                }
            }
        ],
    }


@pytest.fixture
def fixtures_dir():
    """Fixture providing path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def reset_loggers():
    """Automatically reset loggers between tests."""
    # Reset any configured loggers
    yield
    # Cleanup after test
