"""
Structured error handling utilities for KIPRIS API.
Provides custom exception classes and error response standardization.
"""

import typing as t
from enum import Enum


class KiprisErrorCode(Enum):
    """KIPRIS API error codes."""

    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"
    HTTP_ERROR = "HTTP_ERROR"
    RATE_LIMITED = "RATE_LIMITED"
    PARSE_ERROR = "PARSE_ERROR"
    API_ERROR = "API_ERROR"


class KiprisApiError(Exception):
    """Base exception for KIPRIS API errors."""

    def __init__(self, code: KiprisErrorCode, message: str, details: t.Dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

    def to_dict(self) -> t.Dict:
        """Convert error to dictionary for API responses."""
        return {"error": self.code.value, "message": self.message, "details": self.details}


class KiprisTimeoutError(KiprisApiError):
    """Timeout exception for KIPRIS API."""

    def __init__(self, timeout_seconds: int, details: t.Dict = None):
        super().__init__(
            code=KiprisErrorCode.TIMEOUT,
            message=f"Request timeout after {timeout_seconds} seconds",
            details={"timeout_seconds": timeout_seconds},
        )


class KiprisConnectionError(KiprisApiError):
    """Connection error for KIPRIS API."""

    def __init__(self, original_error: Exception, details: t.Dict = None):
        super().__init__(
            code=KiprisErrorCode.CONNECTION_ERROR,
            message=f"Connection failed: {str(original_error)}",
            details={"original_error": str(original_error)},
        )


class KiprisHttpError(KiprisApiError):
    """HTTP error for KIPRIS API."""

    def __init__(self, status_code: int, response_text: str, details: t.Dict = None):
        super().__init__(
            code=KiprisErrorCode.HTTP_ERROR,
            message=f"HTTP error {status_code}: {response_text[:200]}",
            details={"status_code": status_code, "response_preview": response_text[:200]},
        )


class KiprisRateLimitError(KiprisApiError):
    """Rate limit error for KIPRIS API."""

    def __init__(self, retry_after: int, details: t.Dict = None):
        super().__init__(
            code=KiprisErrorCode.RATE_LIMITED,
            message=f"Rate limit exceeded. Retry after {retry_after} seconds",
            details={"retry_after": retry_after},
        )


class KiprisParseError(KiprisApiError):
    """Parse error for KIPRIS API."""

    def __init__(self, parse_error: str, response_text: str, details: t.Dict = None):
        super().__init__(
            code=KiprisErrorCode.PARSE_ERROR,
            message=f"Failed to parse XML response: {parse_error}",
            details={"parse_error": parse_error, "response_preview": response_text[:200]},
        )
