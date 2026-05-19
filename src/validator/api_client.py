"""
EVS API Client Module

Handles communication with the Gazelle EVS FHIR validation web service.
Implements SOAP client for EVS API endpoints with authentication, caching,
and error handling.
"""

from typing import Dict, List, Optional
from loguru import logger
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ..utils.config import Config
from ..utils.exceptions import APIError, AuthenticationError


class EVSAPIClient:
    """
    Client for interacting with the EVS validation web service.

    Handles SOAP requests to the Gazelle EVS API including authentication,
    request retries, and response parsing.

    Attributes:
        config: Configuration object with API credentials
        session: Requests session with retry logic
        client: Zeep SOAP client instance
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize EVS API client.

        Args:
            api_key: EVS API key for authentication (uses config if not provided)
            base_url: EVS base URL (uses config if not provided)

        Raises:
            ConfigurationError: If API key is not provided or found in config
        """
        self.config = Config()
        self.api_key = api_key or self.config.EVS_API_KEY
        self.base_url = base_url or self.config.EVS_BASE_URL

        if not self.api_key:
            raise APIError("EVS_API_KEY is required")

        # Setup session with retry logic
        self.session = self._create_session()
        self.client = None
        logger.info(f"Initialized EVS API client for {self.base_url}")

    def _create_session(self) -> Session:
        """
        Create requests session with retry logic.

        Returns:
            Configured session with exponential backoff
        """
        session = Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def connect(self) -> None:
        """
        Establish connection to EVS web service.

        Initializes the SOAP client with the WSDL endpoint.

        Raises:
            APIError: If connection fails
        """
        try:
            wsdl_url = f"{self.base_url}/path/to/wsdl"  # TODO: Add correct WSDL path
            transport = Transport(session=self.session)
            self.client = Client(wsdl_url, transport=transport)
            logger.info("Successfully connected to EVS API")
        except Exception as e:
            logger.error(f"Failed to connect to EVS API: {e}")
            raise APIError(f"Connection failed: {e}")

    def validate_document(
        self, document: str, validator: str
    ) -> Dict[str, any]:
        """
        Validate FHIR document using specified validator.

        Args:
            document: FHIR document as JSON or XML string
            validator: Name of the EVS validator to use

        Returns:
            Dictionary containing validation results

        Raises:
            APIError: If validation request fails
        """
        if not self.client:
            self.connect()

        try:
            logger.debug(f"Validating document with validator: {validator}")
            response = self.client.service.validateDocument(
                document=document,
                validator=validator
            )
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Validation request failed: {e}")
            raise APIError(f"Validation failed: {e}")

    def validate_base64_document(
        self, base64_document: str, validator: str
    ) -> Dict[str, any]:
        """
        Validate base64-encoded FHIR document.

        Args:
            base64_document: Base64-encoded FHIR document
            validator: Name of the EVS validator to use

        Returns:
            Dictionary containing validation results

        Raises:
            APIError: If validation request fails
        """
        if not self.client:
            self.connect()

        try:
            logger.debug(f"Validating base64 document with validator: {validator}")
            response = self.client.service.validateBase64Document(
                base64Document=base64_document,
                validator=validator
            )
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Base64 validation request failed: {e}")
            raise APIError(f"Validation failed: {e}")

    def get_list_of_validators(self, discriminator: Optional[str] = None) -> List[str]:
        """
        Retrieve list of available validators from EVS.

        Args:
            discriminator: Optional filter (e.g., 'IHE', 'HL7-EU')

        Returns:
            List of validator names

        Raises:
            APIError: If request fails
        """
        if not self.client:
            self.connect()

        try:
            logger.debug("Fetching list of validators")
            response = self.client.service.getListOfValidators(
                discriminator=discriminator
            )
            return response
        except Exception as e:
            logger.error(f"Failed to get validators list: {e}")
            raise APIError(f"Failed to retrieve validators: {e}")

    def about(self) -> Dict[str, str]:
        """
        Get information about the EVS service.

        Returns:
            Dictionary with service metadata

        Raises:
            APIError: If request fails
        """
        if not self.client:
            self.connect()

        try:
            response = self.client.service.about()
            return response
        except Exception as e:
            logger.error(f"Failed to get service info: {e}")
            raise APIError(f"Failed to retrieve service info: {e}")

    def _parse_response(self, response) -> Dict[str, any]:
        """
        Parse XML response from EVS into structured dict.

        Args:
            response: Raw XML response from EVS

        Returns:
            Parsed validation results as dictionary

        TODO: Implement XML parsing logic based on EVS response schema
        """
        # Placeholder - implement based on actual EVS response format
        return {"response": response}

    def close(self) -> None:
        """Close the API session."""
        if self.session:
            self.session.close()
            logger.info("Closed EVS API session")
