"""Tests for template_renderer module."""

import pytest

from config import get_default_config
from template_renderer import TemplateRenderer


@pytest.fixture
def renderer():
    """Create a template renderer instance."""
    config = get_default_config()
    return TemplateRenderer(config)


def test_template_renderer_creation(renderer):
    """Test template renderer creation."""
    assert renderer is not None
    assert renderer.env is not None


def test_render_base_html(renderer):
    """Test rendering base HTML template."""
    context = {
        "meta_title": "Test Page",
        "description": "Test description",
        "keywords": "test, keywords",
        "canonical": "https://example.com/test",
        "doc_type_css": "<link rel='stylesheet' href='/test.css'>",
        "og_tags": "",
        "twitter_tags": "",
        "additional_meta": "",
        "structured_data": {"@context": "https://schema.org"},
        "base_styles": "body { margin: 0; }",
        "doc_styles": "",
        "nav_styles": "",
        "additional_styles": "",
        "breadcrumb_html": "<nav>Test</nav>",
        "doc_meta": "<div>Meta</div>",
        "content": "<p>Test content</p>",
        "document_type": "articles",
        "internal_nav": "",
        "related_content": "",
    }

    html = renderer.render_base_html(context)

    assert "Test Page" in html
    assert "Test description" in html
    assert "Test content" in html
    assert "GCC Tax Laws" in html  # Site name from config


def test_custom_filter_truncate_text(renderer):
    """Test custom truncate_text filter."""
    truncate = renderer.env.filters["truncate_text"]

    assert truncate("Short text", 100) == "Short text"
    assert truncate("This is a very long text", 10) == "This is a..."
    assert truncate("", 10) == ""
