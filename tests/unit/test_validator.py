"""
Unit tests for FHIR validator core functionality.
"""

import pytest
from unittest.mock import Mock, patch

from src.validator.validator import FHIRValidator
from src.validator.report_generator import ValidationReport
from src.utils.exceptions import ValidationError


class TestFHIRValidator:
    """Test cases for FHIRValidator class."""

    def test_validator_initialization(self, test_config):
        """Test validator initializes correctly."""
        validator = FHIRValidator(config=test_config)
        assert validator is not None
        assert validator.config is not None
        assert validator.api_client is not None
        assert validator.parser is not None

    def test_validate_with_resource_object(self, mock_api_client, sample_patient_json):
        """Test validation with FHIR resource object."""
        # TODO: Implement when resource parsing is complete
        pass

    def test_select_validator_from_profile(self, test_config):
        """Test validator selection based on profile."""
        validator = FHIRValidator(config=test_config)

        # Hospital discharge profile
        result = validator._select_validator("hospital-discharge")
        assert "hospital-discharge" in result.lower()

        # Laboratory report profile
        result = validator._select_validator("laboratory-report")
        assert "laboratory-report" in result.lower()

    def test_batch_validation(self, test_config, mock_api_client):
        """Test batch validation of multiple resources."""
        # TODO: Implement batch validation test
        pass

    def test_validation_error_handling(self, test_config):
        """Test that validation errors are properly handled."""
        validator = FHIRValidator(config=test_config)

        with pytest.raises((ValidationError, Exception)):
            # Invalid resource should raise error
            validator.validate("invalid-resource-data")


class TestValidationReport:
    """Test cases for ValidationReport class."""

    def test_report_creation(self):
        """Test validation report creation."""
        report = ValidationReport(is_valid=True)
        assert report.is_valid is True
        assert report.error_count == 0
        assert report.warning_count == 0

    def test_error_report(self):
        """Test error report creation."""
        report = ValidationReport.error("Test error")
        assert report.is_valid is False
        assert report.error_count == 1

    def test_report_to_dict(self):
        """Test conversion of report to dictionary."""
        report = ValidationReport(is_valid=True, profile="test-profile")
        result = report.to_dict()

        assert isinstance(result, dict)
        assert result["is_valid"] is True
        assert "summary" in result
        assert result["profile"] == "test-profile"

    def test_report_to_console(self):
        """Test console output generation."""
        report = ValidationReport(is_valid=True)
        output = report.to_console()

        assert isinstance(output, str)
        assert "PASSED" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
