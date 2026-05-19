"""
HL7 EU Gazelle Validator Package

A Python tool for validating HL7 FHIR bundles and resources against
the eHDSI (eHealth Digital Service Infrastructure) Gazelle validation services.
"""

__version__ = "0.1.0"
__author__ = "Duncan Groenewald"
__license__ = "MIT"

from .validator.validator import FHIRValidator
from .validator.api_client import EVSAPIClient
from .utils.exceptions import ValidationError, APIError

__all__ = [
    "FHIRValidator",
    "EVSAPIClient",
    "ValidationError",
    "APIError",
]
