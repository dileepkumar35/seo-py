"""
Centralized logging and error reporting module.
"""

import logging
import sys
from typing import Optional


class SEOLogger:
    """Centralized logger for SEO HTML generation."""

    def __init__(self, name: str = "seo-py", level: int = logging.INFO):
        """
        Initialize the SEO logger.

        Args:
            name: Logger name
            level: Logging level
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Avoid duplicate handlers
        if not self.logger.handlers:
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(level)

            # Format
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)

            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: Optional[Exception] = None, **kwargs) -> None:
        """Log error message with optional exception info."""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, extra=kwargs)

    def critical(self, message: str, exc_info: Optional[Exception] = None, **kwargs) -> None:
        """Log critical message with optional exception info."""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)


# Global logger instance
_logger_instance: Optional[SEOLogger] = None


def get_logger() -> SEOLogger:
    """Get the global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SEOLogger()
    return _logger_instance
