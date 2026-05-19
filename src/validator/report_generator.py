"""
Validation Report Generator

Generates formatted validation reports from EVS API responses.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class Severity(Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "information"


@dataclass
class ValidationIssue:
    """
    Represents a single validation issue.

    Attributes:
        severity: Issue severity (error, warning, info)
        message: Issue description
        location: Resource path where issue occurred
        line: Line number (if available)
    """

    severity: Severity
    message: str
    location: Optional[str] = None
    line: Optional[int] = None

    def __str__(self) -> str:
        """String representation of validation issue."""
        loc = f" at {self.location}" if self.location else ""
        line_info = f" (line {self.line})" if self.line else ""
        return f"[{self.severity.value.upper()}]{loc}{line_info}: {self.message}"


@dataclass
class ValidationReport:
    """
    Validation report containing all validation results.

    Attributes:
        is_valid: Overall validation status
        issues: List of validation issues
        profile: FHIR profile used for validation
        validator: EVS validator used
        metadata: Additional metadata
    """

    is_valid: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    profile: Optional[str] = None
    validator: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)

    @property
    def info_count(self) -> int:
        """Count of informational issues."""
        return sum(1 for issue in self.issues if issue.severity == Severity.INFO)

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "is_valid": self.is_valid,
            "profile": self.profile,
            "validator": self.validator,
            "summary": {
                "errors": self.error_count,
                "warnings": self.warning_count,
                "info": self.info_count,
            },
            "issues": [
                {
                    "severity": issue.severity.value,
                    "message": issue.message,
                    "location": issue.location,
                    "line": issue.line,
                }
                for issue in self.issues
            ],
            "metadata": self.metadata,
        }

    def to_console(self, colorize: bool = True) -> str:
        """
        Generate console-friendly report.

        Args:
            colorize: Whether to use color codes

        Returns:
            Formatted console output
        """
        lines = []

        # Header
        status = "✅ PASSED" if self.is_valid else "❌ FAILED"
        lines.append(f"\n{'=' * 60}")
        lines.append(f"Validation Report: {status}")
        lines.append(f"{'=' * 60}")

        if self.profile:
            lines.append(f"Profile: {self.profile}")
        if self.validator:
            lines.append(f"Validator: {self.validator}")

        # Summary
        lines.append(f"\nSummary:")
        lines.append(f"  Errors:   {self.error_count}")
        lines.append(f"  Warnings: {self.warning_count}")
        lines.append(f"  Info:     {self.info_count}")

        # Issues
        if self.issues:
            lines.append(f"\nIssues:")
            for issue in self.issues:
                lines.append(f"  {issue}")

        lines.append(f"{'=' * 60}\n")
        return "\n".join(lines)

    @staticmethod
    def from_api_response(
        api_response: Dict, resource, profile: Optional[str] = None
    ) -> "ValidationReport":
        """
        Create ValidationReport from EVS API response.

        Args:
            api_response: Parsed API response dictionary
            resource: Original FHIR resource
            profile: Profile used for validation

        Returns:
            ValidationReport object

        TODO: Implement actual parsing based on EVS response format
        """
        # Placeholder implementation
        logger.debug("Parsing API response into ValidationReport")

        # TODO: Parse actual EVS XML response structure
        # This is a simplified placeholder
        issues = []
        is_valid = api_response.get("valid", True)

        return ValidationReport(
            is_valid=is_valid, issues=issues, profile=profile, metadata=api_response
        )

    @staticmethod
    def error(error_message: str) -> "ValidationReport":
        """
        Create error report for validation failures.

        Args:
            error_message: Error description

        Returns:
            ValidationReport with error
        """
        return ValidationReport(
            is_valid=False,
            issues=[ValidationIssue(Severity.ERROR, error_message)],
        )
