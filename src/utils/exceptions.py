"""
Custom Exception Classes

Defines custom exceptions for the HL7 EU Gazelle Validator.
"""


class ValidatorException(Exception):
    """Base exception for all validator errors."""

    pass


class ValidationError(ValidatorException):
    """Raised when FHIR resource validation fails."""

    def __init__(self, message: str, errors: list = None):
        """
        Initialize validation error.

        Args:
            message: Error message
            errors: List of validation error details
        """
        super().__init__(message)
        self.errors = errors or []


class APIError(ValidatorException):
    """Raised when EVS API request fails."""

    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails."""

    pass


class ConfigurationError(ValidatorException):
    """Raised when configuration is invalid or missing."""

    pass


class ParseError(ValidatorException):
    """Raised when FHIR document parsing fails."""

    pass


class NetworkError(APIError):
    """Raised when network-related errors occur."""

    pass
