"""
Configuration Management

Loads and manages application configuration from environment variables.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from loguru import logger

from .exceptions import ConfigurationError


class Config:
    """
    Application configuration loaded from environment variables.

    Attributes:
        EVS_API_KEY: API key for EVS authentication
        EVS_BASE_URL: Base URL for EVS API
        EVS_SESSION_TIMEOUT: Session timeout in seconds
        DEFAULT_VALIDATOR: Default validator to use
        STRICT_MODE: Whether to treat warnings as errors
        LOG_LEVEL: Logging level
        LOG_FILE: Path to log file
        ENABLE_CACHE: Whether to enable response caching
        CACHE_TTL: Cache time-to-live in seconds
    """

    def __init__(self, env_file: Optional[Path] = None):
        """
        Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file (defaults to .env in project root)

        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Load .env file
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # EVS API Configuration
        self.EVS_API_KEY = os.getenv("EVS_API_KEY")
        self.EVS_BASE_URL = os.getenv(
            "EVS_BASE_URL", "https://gazelle.ehdsi.eu"
        )
        self.EVS_SESSION_TIMEOUT = int(os.getenv("EVS_SESSION_TIMEOUT", "3600"))

        # Validation Settings
        self.DEFAULT_VALIDATOR = os.getenv(
            "DEFAULT_VALIDATOR", "cda-validator"
        )
        self.STRICT_MODE = os.getenv("STRICT_MODE", "false").lower() == "true"
        self.MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "50"))

        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.LOG_FILE = os.getenv("LOG_FILE", "logs/validator.log")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

        # API Rate Limiting
        self.RATE_LIMIT_CALLS = int(os.getenv("RATE_LIMIT_CALLS", "60"))
        self.RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

        # Cache Settings
        self.ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
        self.CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
        self.CACHE_DIR = os.getenv("CACHE_DIR", ".cache")

        # Output Settings
        self.DEFAULT_OUTPUT_FORMAT = os.getenv("DEFAULT_OUTPUT_FORMAT", "json")
        self.COLORIZE_OUTPUT = os.getenv("COLORIZE_OUTPUT", "true").lower() == "true"

        # Performance
        self.MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
        self.REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

        # Development
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        self.MOCK_API = os.getenv("MOCK_API", "false").lower() == "true"

        # Validate required settings
        self._validate()

        logger.info("Configuration loaded successfully")

    def _validate(self) -> None:
        """
        Validate that required configuration is present.

        Raises:
            ConfigurationError: If required configuration is missing
        """
        if not self.MOCK_API and not self.EVS_API_KEY:
            raise ConfigurationError(
                "EVS_API_KEY is required. Set it in .env file or as environment variable."
            )

        # Create necessary directories
        Path(self.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        if self.ENABLE_CACHE:
            Path(self.CACHE_DIR).mkdir(parents=True, exist_ok=True)

    def __repr__(self) -> str:
        """String representation (hides sensitive data)."""
        return (
            f"<Config EVS_BASE_URL={self.EVS_BASE_URL} "
            f"LOG_LEVEL={self.LOG_LEVEL} "
            f"STRICT_MODE={self.STRICT_MODE}>"
        )
