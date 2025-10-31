"""Snapshot tests for HTML generation."""

import pytest

from config import get_default_config
from template_renderer import TemplateRenderer
from utils import escape_html


@pytest.fixture
def renderer():
    """Create a template renderer instance."""
    config = get_default_config()
    return TemplateRenderer(config)


def test_article_html_snapshot(renderer, snapshot):
    """Test that article HTML generation is stable (snapshot test)."""
    # Mock article data
    context = {
        "meta_title": escape_html("Article 1 - Scope | UAE Corporate Tax | GCC Tax Laws"),
        "description": "Understanding the scope of UAE Corporate Tax Law",
        "keywords": "UAE, Corporate Tax, CIT, Article 1, Scope, Tax Law",
        "canonical": "https://gcctaxlaws.com/articles/uae-cit-fdl-47-of-2022-article-1",
        "doc_type_css": "<link rel='stylesheet' href='/article.css'>",
        "og_tags": "<meta property='og:type' content='article' />",
        "twitter_tags": "<meta name='twitter:card' content='summary_large_image' />",
        "additional_meta": "",
        "structured_data": {
            "@context": "https://schema.org",
            "@type": "Legislation",
            "name": "Article 1 - Scope",
            "legislationIdentifier": "Article 1",
        },
        "base_styles": "body { margin: 0; }",
        "doc_styles": ".static-content { padding: 20px; }",
        "nav_styles": ".breadcrumb-nav { background: #f0f0f0; }",
        "additional_styles": "",
        "breadcrumb_html": "<nav>Home > Articles > Article 1</nav>",
        "doc_meta": "<div><strong>Article Number:</strong> 1</div>",
        "content": "<h1>Article 1 - Scope</h1><p>This article defines the scope of the law.</p>",
        "document_type": "articles",
        "internal_nav": "",
        "related_content": "",
    }

    html = renderer.render_base_html(context)

    # Assert the snapshot matches
    # This will create a snapshot file on first run
    # and compare against it on subsequent runs
    snapshot.assert_match(html, "article_output.html")


def test_blog_html_snapshot(renderer, snapshot):
    """Test that blog HTML generation is stable (snapshot test)."""
    context = {
        "meta_title": escape_html("Understanding UAE VAT | GCC Tax Laws Blog"),
        "description": "A comprehensive guide to UAE VAT regulations",
        "keywords": "UAE, VAT, Blog, Tax Guide",
        "canonical": "https://gcctaxlaws.com/blogs/understanding-uae-vat",
        "doc_type_css": "<link rel='stylesheet' href='/blogs.css'>",
        "og_tags": "<meta property='og:type' content='article' />",
        "twitter_tags": "<meta name='twitter:card' content='summary_large_image' />",
        "additional_meta": "",
        "structured_data": {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": "Understanding UAE VAT",
        },
        "base_styles": "body { margin: 0; }",
        "doc_styles": "",
        "nav_styles": "",
        "additional_styles": "",
        "breadcrumb_html": "<nav>Home > Blogs > Understanding UAE VAT</nav>",
        "doc_meta": "<div><strong>Published:</strong> 2024-01-01</div>",
        "content": "<h1>Understanding UAE VAT</h1><p>Blog content here...</p>",
        "document_type": "blogs",
        "internal_nav": "",
        "related_content": "",
    }

    html = renderer.render_base_html(context)

    # Assert the snapshot matches
    snapshot.assert_match(html, "blog_output.html")


def test_html_structure_stability(renderer):
    """Test that HTML structure contains essential elements."""
    context = {
        "meta_title": "Test Page",
        "description": "Test description",
        "keywords": "test",
        "canonical": "https://example.com/test",
        "doc_type_css": "",
        "og_tags": "",
        "twitter_tags": "",
        "additional_meta": "",
        "structured_data": {},
        "base_styles": "",
        "doc_styles": "",
        "nav_styles": "",
        "additional_styles": "",
        "breadcrumb_html": "",
        "doc_meta": "",
        "content": "<p>Test</p>",
        "document_type": "articles",
        "internal_nav": "",
        "related_content": "",
    }

    html = renderer.render_base_html(context)

    # Check essential HTML structure
    assert "<!DOCTYPE html>" in html
    assert "<html lang=\"en\">" in html
    assert "<meta charset=\"utf-8\"" in html
    assert "<title>Test Page</title>" in html
    assert "GCC Tax Laws" in html  # Site name
    assert "<p>Test</p>" in html  # Content
    assert "</html>" in html
