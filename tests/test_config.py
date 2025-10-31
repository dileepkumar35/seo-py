"""Tests for config module."""

from pathlib import Path

from config import SEOConfig, get_default_config


def test_seo_config_creation():
    """Test SEO config creation with valid data."""
    config = SEOConfig(
        site_url="https://example.com",
        site_name="Test Site",
        twitter_handle="@testsite",
        default_og_image="/image.png",
        output_dir=Path("./output"),
        public_path="/public",
        data_dir=Path("./data"),
        index_html_path=Path("./index.html"),
    )

    assert config.site_url == "https://example.com"
    assert config.site_name == "Test Site"
    assert config.twitter_handle == "@testsite"
    assert isinstance(config.output_dir, Path)


def test_seo_config_twitter_handle_validation():
    """Test twitter handle validation adds @ if missing."""
    config = SEOConfig(
        site_url="https://example.com",
        site_name="Test Site",
        twitter_handle="testsite",  # No @ prefix
        default_og_image="/image.png",
        output_dir=Path("./output"),
        public_path="/public",
        data_dir=Path("./data"),
        index_html_path=Path("./index.html"),
    )

    assert config.twitter_handle == "@testsite"


def test_seo_config_path_conversion():
    """Test that string paths are converted to Path objects."""
    config = SEOConfig(
        site_url="https://example.com",
        site_name="Test Site",
        twitter_handle="@testsite",
        default_og_image="/image.png",
        output_dir="./output",  # String path
        public_path="/public",
        data_dir="./data",  # String path
        index_html_path="./index.html",  # String path
    )

    assert isinstance(config.output_dir, Path)
    assert isinstance(config.data_dir, Path)
    assert isinstance(config.index_html_path, Path)


def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()

    assert config.site_url == "https://gcctaxlaws.com"
    assert config.site_name == "GCC Tax Laws"
    assert config.twitter_handle == "@gcctaxlaws"
    assert isinstance(config.output_dir, Path)
