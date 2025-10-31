#!/usr/bin/env python3
"""
Example usage of the new modular components with the existing seo.py functionality.
This demonstrates how to integrate Pydantic config, Jinja2 templates, caching, and logging.
"""

from datetime import datetime, timezone
from pathlib import Path

from config import SEOConfig, get_default_config
from logger import get_logger
from template_renderer import TemplateRenderer
from utils import escape_html, get_country_flag, get_authority_name, truncate_text


def example_basic_usage():
    """Example: Basic usage of config, logger, and utils."""
    # Get configuration
    config = get_default_config()
    logger = get_logger()

    logger.info(f"Starting SEO generation with site: {config.site_name}")
    logger.info(f"Output directory: {config.output_dir}")

    # Use cached utility functions
    uae_flag = get_country_flag("AE")
    authority = get_authority_name("uae-cit-law")

    logger.info(f"UAE Flag: {uae_flag}")
    logger.info(f"Authority: {authority}")


def example_template_rendering():
    """Example: Render HTML using Jinja2 templates."""
    config = get_default_config()
    logger = get_logger()
    renderer = TemplateRenderer(config)

    # Prepare context for rendering
    context = {
        "meta_title": escape_html("Article 1 - Scope | UAE Corporate Tax | GCC Tax Laws"),
        "description": "Understanding the scope of UAE Corporate Tax Law",
        "keywords": "UAE, Corporate Tax, CIT, Article 1",
        "canonical": f"{config.site_url}/articles/uae-cit-fdl-47-of-2022-article-1",
        "doc_type_css": "<link rel='stylesheet' href='/article.css'>",
        "og_tags": "",
        "twitter_tags": "",
        "additional_meta": "",
        "structured_data": {
            "@context": "https://schema.org",
            "@type": "Legislation",
            "name": "Article 1 - Scope",
        },
        "base_styles": "body { margin: 0; padding: 0; }",
        "doc_styles": "",
        "nav_styles": "",
        "additional_styles": "",
        "breadcrumb_html": "<nav>Home > Articles > Article 1</nav>",
        "doc_meta": "<div>Article 1</div>",
        "content": "<h1>Article 1 - Scope</h1><p>This article defines the scope...</p>",
        "document_type": "articles",
        "internal_nav": "",
        "related_content": "",
    }

    try:
        html = renderer.render_base_html(context)
        logger.info(f"Generated HTML length: {len(html)} characters")
        logger.info("Template rendering successful!")
        return html
    except Exception as e:
        logger.error(f"Template rendering failed: {e}", exc_info=e)
        return None


def example_custom_config():
    """Example: Create custom configuration."""
    logger = get_logger()

    # Create custom config for testing
    custom_config = SEOConfig(
        site_url="https://test.example.com",
        site_name="Test Site",
        twitter_handle="testsite",  # Will be converted to @testsite
        default_og_image="/test-image.png",
        output_dir=Path("./test_output"),
        public_path="/test",
        data_dir=Path("./test_data"),
        index_html_path=Path("./test_index.html"),
    )

    logger.info(f"Custom config site URL: {custom_config.site_url}")
    logger.info(f"Custom config twitter: {custom_config.twitter_handle}")
    logger.info(f"Custom config validated successfully!")


def example_error_handling():
    """Example: Error handling with logger."""
    logger = get_logger()

    try:
        # Simulate an error
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error occurred", exc_info=e)
        logger.warning("Continuing with default values...")


def main():
    """Run all examples."""
    logger = get_logger()
    logger.info("=" * 60)
    logger.info("SEO-PY Example Usage")
    logger.info("=" * 60)

    print("\n1. Basic Usage Example:")
    example_basic_usage()

    print("\n2. Template Rendering Example:")
    html = example_template_rendering()
    if html:
        print(f"   ✓ Generated HTML: {len(html)} characters")

    print("\n3. Custom Config Example:")
    example_custom_config()

    print("\n4. Error Handling Example:")
    example_error_handling()

    logger.info("=" * 60)
    logger.info("All examples completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
