"""
FHIR Parser Module

Handles parsing and manipulation of FHIR resources.
"""

from typing import Optional, Union
from pathlib import Path
import json
from loguru import logger

from fhir.resources.bundle import Bundle
from fhir.resources.resource import Resource

from ..utils.exceptions import ParseError


class FHIRParser:
    """
    Parser for FHIR resources in JSON and XML formats.

    Handles FHIR resource parsing, profile detection, and format conversion.
    """

    def __init__(self):
        """Initialize FHIR parser."""
        logger.debug("FHIR Parser initialized")

    def parse_file(self, file_path: Path) -> Resource:
        """
        Parse FHIR resource from file.

        Args:
            file_path: Path to FHIR resource file (JSON or XML)

        Returns:
            Parsed FHIR Resource object

        Raises:
            ParseError: If file cannot be parsed
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self.parse_string(content)

        except Exception as e:
            logger.error(f"Failed to parse file {file_path}: {e}")
            raise ParseError(f"Failed to parse FHIR resource: {e}")

    def parse_string(self, content: str) -> Resource:
        """
        Parse FHIR resource from string.

        Args:
            content: FHIR resource as JSON or XML string

        Returns:
            Parsed FHIR Resource object

        Raises:
            ParseError: If content cannot be parsed
        """
        try:
            # Try JSON first
            data = json.loads(content)
            resource_type = data.get("resourceType")

            if resource_type == "Bundle":
                return Bundle.parse_obj(data)
            else:
                # TODO: Handle other resource types dynamically
                return Resource.parse_obj(data)

        except json.JSONDecodeError:
            # Try XML parsing
            # TODO: Implement XML parsing
            raise ParseError("XML parsing not yet implemented")
        except Exception as e:
            logger.error(f"Failed to parse FHIR content: {e}")
            raise ParseError(f"Failed to parse FHIR resource: {e}")

    def detect_profile(self, resource: Resource) -> Optional[str]:
        """
        Detect FHIR profile from resource metadata.

        Args:
            resource: FHIR Resource object

        Returns:
            Profile URL if found, None otherwise
        """
        try:
            if hasattr(resource, "meta") and resource.meta:
                if hasattr(resource.meta, "profile") and resource.meta.profile:
                    return resource.meta.profile[0]
            logger.warning("No profile found in resource metadata")
            return None
        except Exception as e:
            logger.error(f"Failed to detect profile: {e}")
            return None

    def to_json(self, resource: Resource, pretty: bool = False) -> str:
        """
        Convert FHIR resource to JSON string.

        Args:
            resource: FHIR Resource object
            pretty: Whether to format with indentation

        Returns:
            JSON string representation
        """
        try:
            if pretty:
                return resource.json(indent=2)
            return resource.json()
        except Exception as e:
            logger.error(f"Failed to convert resource to JSON: {e}")
            raise ParseError(f"JSON conversion failed: {e}")

    def to_xml(self, resource: Resource) -> str:
        """
        Convert FHIR resource to XML string.

        Args:
            resource: FHIR Resource object

        Returns:
            XML string representation

        TODO: Implement XML conversion
        """
        raise NotImplementedError("XML conversion not yet implemented")

    def extract_bundle_entries(self, bundle: Bundle) -> list:
        """
        Extract individual resources from Bundle.

        Args:
            bundle: FHIR Bundle resource

        Returns:
            List of resources from bundle entries
        """
        try:
            if not isinstance(bundle, Bundle):
                raise ValueError("Resource is not a Bundle")

            entries = []
            if hasattr(bundle, "entry") and bundle.entry:
                for entry in bundle.entry:
                    if hasattr(entry, "resource") and entry.resource:
                        entries.append(entry.resource)

            logger.info(f"Extracted {len(entries)} resources from bundle")
            return entries

        except Exception as e:
            logger.error(f"Failed to extract bundle entries: {e}")
            raise ParseError(f"Bundle extraction failed: {e}")
