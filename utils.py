"""
Utility functions with caching for performance optimization.
"""

import html
import re
from functools import lru_cache


@lru_cache(maxsize=128)
def get_country_flag(country_code: str) -> str:
    """
    Get flag emoji for country code (cached).

    Args:
        country_code: Two-letter country code

    Returns:
        Flag emoji string
    """
    flag_map = {
        "AE": "🇦🇪",
        "DZ": "🇩🇿",
        "AL": "🇦🇱",
        "US": "🇺🇸",
        "GB": "🇬🇧",
        "FR": "🇫🇷",
        "DE": "🇩🇪",
        "IN": "🇮🇳",
        "CN": "🇨🇳",
        "JP": "🇯🇵",
        "CA": "🇨🇦",
        "AU": "🇦🇺",
        "BR": "🇧🇷",
        "IT": "🇮🇹",
        "ES": "🇪🇸",
        "RU": "🇷🇺",
        "SA": "🇸🇦",
        "QA": "🇶🇦",
        "KW": "🇰🇼",
        "BH": "🇧🇭",
        "OM": "🇴🇲",
        "EG": "🇪🇬",
        "JO": "🇯🇴",
        "LB": "🇱🇧",
        "MA": "🇲🇦",
        "TN": "🇹🇳",
        "LY": "🇱🇾",
        "SY": "🇸🇾",
        "IQ": "🇮🇶",
        "YE": "🇾🇪",
        "SD": "🇸🇩",
        "SO": "🇸🇴",
        "DJ": "🇩🇯",
        "KM": "🇰🇲",
        "MR": "🇲🇷",
    }
    return flag_map.get(country_code.upper() if country_code else "", "🏳️")


@lru_cache(maxsize=256)
def get_authority_name(law_slug: str) -> str:
    """
    Get the appropriate tax authority name based on the law slug (cached).

    Args:
        law_slug: Law slug identifier

    Returns:
        Authority name string
    """
    if not law_slug:
        return "Tax Authority"

    law_slug_lower = law_slug.lower()

    if law_slug_lower.startswith("uae-"):
        return "Federal Tax Authority"
    elif law_slug_lower.startswith("ksa-"):
        return "Zakat, Tax and Customs Authority"
    elif law_slug_lower.startswith("oman-"):
        return "Oman Tax Authority"
    elif law_slug_lower.startswith("kwt-") or law_slug_lower.startswith("kuwait-"):
        return "Ministry of Finance - Kuwait"
    elif law_slug_lower.startswith("qatar-"):
        return "General Tax Authority - Qatar"
    elif law_slug_lower.startswith("bahrain-"):
        return "National Bureau for Revenue - Bahrain"
    else:
        return "GCC Secretariat General"


def escape_html(text: str) -> str:
    """
    Escape HTML special characters.

    Args:
        text: Input text

    Returns:
        Escaped text
    """
    if not text:
        return ""
    return html.escape(str(text))


def escape_json(text: str) -> str:
    """
    Escape JSON special characters.

    Args:
        text: Input text

    Returns:
        Escaped text
    """
    if not text:
        return ""
    return str(text).replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")


def truncate_text(text: str, max_length: int) -> str:
    """
    Truncate text to specified length.

    Args:
        text: Input text
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].strip() + "..."


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text.

    Args:
        text: Input text

    Returns:
        URL-friendly slug
    """
    if not text:
        return "unknown"
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def render_title(text: str) -> str:
    """
    Render title text that may contain intentional HTML tags.

    Args:
        text: Input text

    Returns:
        Rendered title (escaped if no HTML tags, otherwise as-is)
    """
    if not text:
        return ""
    # If text contains HTML tags (specifically span tags used for styling), return as-is
    if "<span" in text or "</span>" in text:
        return str(text)
    # Otherwise, escape for safety
    return html.escape(str(text))
