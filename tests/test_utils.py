"""Tests for utils module."""


from utils import (
    escape_html,
    escape_json,
    generate_slug,
    get_authority_name,
    get_country_flag,
    render_title,
    truncate_text,
)


def test_get_country_flag():
    """Test country flag retrieval (cached function)."""
    assert get_country_flag("AE") == "🇦🇪"
    assert get_country_flag("US") == "🇺🇸"
    assert get_country_flag("GB") == "🇬🇧"
    assert get_country_flag("XX") == "🏳️"  # Unknown country
    assert get_country_flag("") == "🏳️"  # Empty string


def test_get_country_flag_caching():
    """Test that country flag function uses caching."""
    # Call twice with same input
    result1 = get_country_flag("AE")
    result2 = get_country_flag("AE")
    # Should return same object due to caching
    assert result1 is result2


def test_get_authority_name():
    """Test authority name retrieval (cached function)."""
    assert get_authority_name("uae-cit-law") == "Federal Tax Authority"
    assert get_authority_name("ksa-vat-law") == "Zakat, Tax and Customs Authority"
    assert get_authority_name("oman-tax-law") == "Oman Tax Authority"
    assert get_authority_name("kwt-tax-law") == "Ministry of Finance - Kuwait"
    assert get_authority_name("kuwait-tax-law") == "Ministry of Finance - Kuwait"
    assert get_authority_name("qatar-tax-law") == "General Tax Authority - Qatar"
    assert get_authority_name("bahrain-tax-law") == "National Bureau for Revenue - Bahrain"
    assert get_authority_name("gcc-agreement") == "GCC Secretariat General"
    assert get_authority_name("") == "Tax Authority"


def test_escape_html():
    """Test HTML escaping."""
    assert (
        escape_html("<script>alert('xss')</script>")
        == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    )
    assert escape_html("Normal text") == "Normal text"
    assert escape_html("") == ""
    assert escape_html("A & B") == "A &amp; B"


def test_escape_json():
    """Test JSON escaping."""
    assert escape_json('{"key": "value"}') == '{\\"key\\": \\"value\\"}'
    assert escape_json("Line 1\nLine 2") == "Line 1\\nLine 2"
    assert escape_json("") == ""


def test_truncate_text():
    """Test text truncation."""
    assert truncate_text("Short text", 100) == "Short text"
    assert (
        truncate_text("This is a long text that should be truncated", 20)
        == "This is a long text..."
    )
    assert truncate_text("", 100) == ""
    assert truncate_text("Exact", 5) == "Exact"


def test_generate_slug():
    """Test slug generation."""
    assert generate_slug("Hello World") == "hello-world"
    assert generate_slug("UAE VAT Law 2023") == "uae-vat-law-2023"
    assert generate_slug("Test@#$%String") == "teststring"
    assert generate_slug("Multiple   Spaces") == "multiple-spaces"
    assert generate_slug("") == "unknown"


def test_render_title():
    """Test title rendering."""
    assert render_title("Plain Title") == "Plain Title"
    assert (
        render_title("<span class='highlight'>Title</span>")
        == "<span class='highlight'>Title</span>"
    )
    assert (
        render_title("<script>alert('xss')</script>")
        == "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
    )
    assert render_title("") == ""
