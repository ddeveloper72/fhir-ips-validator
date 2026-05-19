"""
Core FHIR Validator

Main validation orchestration logic for FHIR resources.
"""

from typing import Dict, Optional, Union
from pathlib import Path
from loguru import logger

from fhir.resources.bundle import Bundle
from fhir.resources.resource import Resource

from .api_client import EVSAPIClient
from .fhir_parser import FHIRParser
from .report_generator import ValidationReport
from ..utils.exceptions import ValidationError, ParseError
from ..utils.config import Config


class FHIRValidator:
    """
    Main FHIR validation orchestrator.

    Coordinates FHIR parsing, API communication, and result processing.

    Attributes:
        config: Application configuration
        api_client: EVS API client instance
        parser: FHIR parser instance
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        config: Optional[Config] = None,
    ):
        """
        Initialize FHIR validator.

        Args:
            api_key: Optional EVS API key (uses config if not provided)
            base_url: Optional EVS base URL (uses config if not provided)
            config: Optional configuration object
        """
        self.config = config or Config()
        self.api_client = EVSAPIClient(api_key=api_key, base_url=base_url)
        self.parser = FHIRParser()
        logger.info("FHIR Validator initialized")

    def validate(
        self,
        resource: Union[str, Path, Resource, Bundle],
        profile: Optional[str] = None,
        validator: Optional[str] = None,
    ) -> ValidationReport:
        """
        Validate FHIR resource against specified profile.

        Args:
            resource: FHIR resource (file path, JSON string, or Resource object)
            profile: FHIR profile URL (optional, auto-detected if not provided)
            validator: EVS validator name (optional, auto-selected based on profile)

        Returns:
            ValidationReport with results

        Raises:
            ValidationError: If validation fails
            ParseError: If resource cannot be parsed
        """
        try:
            # Parse resource
            logger.info("Parsing FHIR resource")
            parsed_resource = self._parse_resource(resource)

            # Detect profile if not provided
            if not profile:
                profile = self.parser.detect_profile(parsed_resource)
                logger.info(f"Auto-detected profile: {profile}")

            # Select validator
            validator_name = validator or self._select_validator(profile)
            logger.info(f"Using validator: {validator_name}")

            # Convert to string for API submission
            resource_string = self.parser.to_json(parsed_resource)

            # Validate via API
            logger.info("Submitting to EVS API for validation")
            api_response = self.api_client.validate_document(
                document=resource_string, validator=validator_name
            )

            # Generate report
            report = ValidationReport.from_api_response(
                api_response, parsed_resource, profile
            )

            logger.info(
                f"Validation complete: {report.error_count} errors, {report.warning_count} warnings"
            )
            return report

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise ValidationError(f"Validation failed: {e}")

    def validate_batch(
        self, resources: list, profile: Optional[str] = None
    ) -> Dict[str, ValidationReport]:
        """
        Validate multiple FHIR resources.

        Args:
            resources: List of FHIR resources
            profile: Optional profile to use for all resources

        Returns:
            Dictionary mapping resource IDs to validation reports

        TODO: Implement parallel processing for batch validation
        """
        results = {}
        for i, resource in enumerate(resources):
            logger.info(f"Validating resource {i + 1}/{len(resources)}")
            try:
                report = self.validate(resource, profile=profile)
                results[f"resource_{i}"] = report
            except Exception as e:
                logger.error(f"Failed to validate resource {i}: {e}")
                results[f"resource_{i}"] = ValidationReport.error(str(e))

        return results

    def _parse_resource(
        self, resource: Union[str, Path, Resource, Bundle]
    ) -> Resource:
        """
        Parse resource from various input formats.

        Args:
            resource: Resource in various formats

        Returns:
            Parsed FHIR Resource object

        Raises:
            ParseError: If parsing fails
        """
        if isinstance(resource, (Resource, Bundle)):
            return resource
        elif isinstance(resource, Path):
            return self.parser.parse_file(resource)
        elif isinstance(resource, str):
            # Try as file path first, then as JSON string
            try:
                return self.parser.parse_file(Path(resource))
            except (FileNotFoundError, OSError):
                return self.parser.parse_string(resource)
        else:
            raise ParseError(f"Unsupported resource type: {type(resource)}")

    def _select_validator(self, profile: str) -> str:
        """
        Select appropriate EVS validator for profile.

        Args:
            profile: FHIR profile URL

        Returns:
            EVS validator name

        TODO: Implement profile-to-validator mapping based on eHDSI Gazelle validators
        """
        # Placeholder - implement mapping based on profile URLs and available validators
        # Common eHDSI validators might include:
        # - CDA validators
        # - XDS/XDR metadata validators
        # - ATNA validators
        # - etc.
        
        profile_lower = profile.lower() if profile else ""
        
        if "cda" in profile_lower:
            return "cda-validator"
        elif "xds" in profile_lower or "xdr" in profile_lower:
            return "xds-validator"
        
        # Default fallback
        return self.config.DEFAULT_VALIDATOR

    def list_validators(self) -> list:
        """
        Get list of available EVS validators.

        Returns:
            List of validator names
        """
        return self.api_client.get_list_of_validators()

    def close(self) -> None:
        """Close API client connection."""
        self.api_client.close()
