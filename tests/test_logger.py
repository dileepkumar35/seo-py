"""Tests for logger module."""

import logging

from logger import SEOLogger, get_logger


def test_seo_logger_creation():
    """Test SEO logger creation."""
    logger = SEOLogger(name="test-logger", level=logging.DEBUG)
    assert logger.logger.name == "test-logger"
    assert logger.logger.level == logging.DEBUG


def test_seo_logger_singleton():
    """Test that get_logger returns the same instance."""
    logger1 = get_logger()
    logger2 = get_logger()
    assert logger1 is logger2


def test_seo_logger_methods(caplog):
    """Test logger methods."""
    logger = SEOLogger(name="test-logger-methods")

    with caplog.at_level(logging.INFO):
        logger.info("Test info message")
        assert "Test info message" in caplog.text

    with caplog.at_level(logging.WARNING):
        logger.warning("Test warning message")
        assert "Test warning message" in caplog.text

    with caplog.at_level(logging.ERROR):
        logger.error("Test error message")
        assert "Test error message" in caplog.text
