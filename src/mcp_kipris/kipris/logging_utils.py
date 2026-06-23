"""
Secure logging utilities for KIPRIS MCP server.
Provides redaction functions to prevent sensitive data exposure in logs.
"""

import os
import logging
import os
import re
import urllib.parse
from typing import Any, Dict, Optional


def redact_sensitive_data(text: str) -> str:
    """
    Redact sensitive information from log messages.

    Args:
        text: Original text that may contain sensitive data

    Returns:
        Text with sensitive patterns redacted
    """
    if not isinstance(text, str):
        return str(text)

    # API key patterns to redact
    api_key_patterns = [
        r"(accessKey|ServiceKey|api_key|apikey)[=:]([^&\s]+)",
        r"(Bearer\s+)([a-zA-Z0-9._-]+)",
        r"(Authorization\s*:\s*)([^,\s]+)",
    ]

    # URL patterns with keys
    url_key_patterns = [
        r"([?&](accessKey|ServiceKey|api_key|apikey)[=])[^&\s]+",
    ]

    redacted_text = text

    for pattern in api_key_patterns + url_key_patterns:
        redacted_text = re.sub(pattern, r"\1***REDACTED***", redacted_text, flags=re.IGNORECASE)

    return redacted_text


def create_safe_url_logger(original_logger):
    """
    Create a logger wrapper that redacts sensitive URL parameters.

    Args:
        original_logger: Original logger instance

    Returns:
        Logger wrapper with redaction
    """

    class SafeURLLogger:
        def __init__(self, logger):
            self.logger = logger

        def _log_with_redaction(self, level, msg, *args, **kwargs):
            # Check if message contains URL and redact sensitive params
            if isinstance(msg, str) and ("http" in msg.lower() or "url" in msg.lower()):
                redacted_msg = redact_sensitive_data(msg)
            else:
                redacted_msg = msg

            return self.logger.log(level, redacted_msg, *args, **kwargs)

        def info(self, msg, *args, **kwargs):
            return self._log_with_redaction(logging.INFO, msg, *args, **kwargs)

        def debug(self, msg, *args, **kwargs):
            return self._log_with_redaction(logging.DEBUG, msg, *args, **kwargs)

        def warning(self, msg, *args, **kwargs):
            return self._log_with_redaction(logging.WARNING, msg, *args, **kwargs)

        def error(self, msg, *args, **kwargs):
            return self._log_with_redaction(logging.ERROR, msg, *args, **kwargs)

        def exception(self, msg, *args, **kwargs):
            return self._log_with_redaction(logging.ERROR, msg, *args, **kwargs)

    return SafeURLLogger(original_logger)


def get_log_level_from_env():
    """
    Get appropriate log level from environment variables.

    Returns:
        Logging level constant
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    return level_mapping.get(log_level, logging.INFO)
