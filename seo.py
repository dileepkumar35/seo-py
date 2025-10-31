#!/usr/bin/env python3
"""
SEO HTML Generator for UAE Tax Consulting Platform
Generates static HTML pages from JSON data during Docker build
Updated to handle the actual JSON structure from the platform
"""

import json
import os
import shutil
import html
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import re
from html.parser import HTMLParser
from dataclasses import dataclass
from typing import Tuple

# Configuration
CONFIG = {
    "SITE_URL": "https://gcctaxlaws.com",
    "SITE_NAME": "GCC Tax Laws",
    "TWITTER_HANDLE": "@gcctaxlaws",
    "DEFAULT_OG_IMAGE": "/web-app-manifest-512x512.png",
    "OUTPUT_DIR": "./public/seo",  # for prod
    # "PUBLIC_PATH": "/public/seo", # needed for local testing since links present inside html documents won't work http://127.0.0.1:5500/public/seo/articles/uae-cit-fdl-47-of-2022-article-43.html testing html doc on live server extension, as files are present inside "./public/seo/articles/..." and not at "./articles/..."
    "PUBLIC_PATH": "",  # for prod
    # "DATA_DIR": "../deploy/data",  # for local
    "INDEX_HTML_PATH": "./public/index.html", # for local
    "DATA_DIR": "./data", # for prod
    # "INDEX_HTML_PATH": "./build/index.html",  # for prod
}
law_files = [
    
    # GCC Agreements
    # "0-gcc-customs-agreement.json",
    "1-gcc-vat-agreement.json",
    "2-gcc-excise-agreement.json",
    
    # UAE Laws
    "3-uae-cit-47-country-law-articles-decisions.json",
    "6-uae-vat-country-law-articles-decisions.json",
    "8-uae-tp-country-law-articles.json",
    # "10-uae-excise-country-law-articles.json",
    # "12-uae-fatca-law.json",
    
    # KSA Laws
    "13-ksa-incometax-country-law-articles-guides.json",
    # "14-ksa-vat-country-law-articles-decisions.json",
    # "16-ksa-excise-country-law-articles.json",
    # "17-ksa-zakat-country-law-articles.json",
    # "34-ksa-customs-country-law-guides.json",
    # "35-ksa-fatca-law.json",
    
    # Kuwait Laws
    # "19-kwt-bptl-country-law-articles.json",
    "20-kwt-ktl-country-law-articles.json",
    "21-kwt-dl-157-country-law-articles.json",
    
    # Qatar Laws
    # "22-qatar-incometax-country-law-articles-decisions.json",
    # "24-qatar-tp-country-law-articles-decisions-circulars.json",
    # "25-qatar-excisetax-country-law-articles-decisions.json",
    # "26-qatar-fatca-law.json",
    
    # Bahrain Laws
    # "27-bahrain-incometax-country-law-articles.json",
    
    # Oman Laws
    # "28-oman-incometax-country-law-articles.json",
    # "29-oman-vat-country-law-articles-decisions.json",
    # "31-oman-excise-country-law-guides.json",
    # "32-oman-cbcr-country-law-guides.json",
    # "33-oman-fatca-law.json",
]

guidance_files = [
    # UAE Guidance
    "4-uae-cit-guidelines-guide.json",
    "4-uae-cit-guidelines-pc.json",
    "7-uae-vat-guidelines-guide-pc.json",
    "9-uae-tp-guidelines-guide-pc.json",
    # "11-uae-excise-guidelines-guide.json",
    # "11-uae-excise-guidelines-pc.json",
    # KSA Guidance
    # "15-ksa-vat-guidelines-guide.json",
    # "18-ksa-zakat-guidelines-guide.json",
    # Qatar Guidance
    # "23-qatar-incometax-circulars.json",
    # Oman Guidance
    # "30-oman-vat-guidelines-guide.json",
    # "36-ksa-incometax-guides.json",
]
treaty_files = [
    "dtaa-uae-1.json",
    "dtaa-uae-2.json",
    "dtaa-ksa.json",
    "dtaa-kuwait.json",
    "dtaa-qatar.json",
    "dtaa-oman.json",
    "dtaa-bahrain.json",
    # "dtaa-extra.json",
]
blog_files = [
    "blogs.json",
]


# ============================================================================
# Basic Helper Functions (must be defined before classes that use them)
# ============================================================================

def escape_html(text: str) -> str:
    """Escape HTML special characters"""
    if not text:
        return ""
    return html.escape(str(text))


def escape_json(text: str) -> str:
    """Escape JSON special characters"""
    if not text:
        return ""
    return str(text).replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")


# ============================================================================
# Helper Classes for DRY Principle
# ============================================================================

@dataclass
class MetaTags:
    """Container for common meta tags to avoid duplication"""
    title: str
    description: str
    keywords: str
    canonical: str
    og_image: str
    og_image_alt: str
    
    def get_og_tags(self) -> str:
        """Generate Open Graph meta tags"""
        return f"""
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{self.canonical}" />
    <meta property="og:title" content="{escape_html(self.title)}" />
    <meta property="og:description" content="{self.description}" />
    <meta property="og:image" content="{self.og_image}" />
    <meta property="og:image:alt" content="{self.og_image_alt}" />
    <meta property="og:site_name" content="{CONFIG['SITE_NAME']}" />
    <meta property="fb:app_id" content="123456789012345" />"""
    
    def get_twitter_tags(self) -> str:
        """Generate Twitter Card meta tags"""
        return f"""
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="{self.canonical}" />
    <meta name="twitter:title" content="{escape_html(self.title)}" />
    <meta name="twitter:description" content="{self.description}" />
    <meta name="twitter:image" content="{self.og_image}" />
    <meta name="twitter:image:alt" content="{self.og_image_alt}" />
    <meta name="twitter:site" content="{CONFIG['TWITTER_HANDLE']}" />"""


class StructuredDataBuilder:
    """Builder for schema.org structured data to reduce duplication"""
    
    @staticmethod
    def get_organization_schema(name: str = "GCC Tax Laws") -> Dict[str, Any]:
        """Generate organization schema object"""
        return {
            "@type": "Organization",
            "name": name,
            "url": "https://gcctaxlaws.com",
            "logo": {
                "@type": "ImageObject",
                "url": f"{CONFIG['SITE_URL']}/web-app-manifest-512x512.png",
                "width": 180,
                "height": 60,
            },
            "alternateName": "GTL",
        }
    
    @staticmethod
    def get_language_schema() -> Dict[str, Any]:
        """Generate language schema object"""
        return {
            "@type": "Language",
            "name": "English",
            "alternateName": "en",
        }
    
    @staticmethod
    def get_webpage_schema(canonical: str) -> Dict[str, Any]:
        """Generate webpage schema object"""
        return {"@type": "WebPage", "@id": canonical}
    
    @staticmethod
    def get_country_schema(country_name: str) -> Dict[str, Any]:
        """Generate country schema object"""
        return {
            "@type": "Country",
            "name": escape_json(country_name),
        }


class CSSGenerator:
    """Generate common CSS to avoid duplication"""
    
    @staticmethod
    def get_base_styles() -> str:
        """Generate base CSS styles used across all document types"""
        return """
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            line-height: 1.6; 
            background: #f8f9fa;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
        .header { background: #232536; color: white; padding: 20px 0; }
        .header p { margin: 0; font-size: 1.5rem; }
        .header nav a { color: #ccc; margin-right: 20px; text-decoration: none; }
        .header nav a:hover { color: white; }
        .breadcrumb-nav { background: #e2eaf2;padding: 10px 0; border-bottom: 1px solid #e9ecef; }
        .breadcrumb-nav a { color: #007bff; text-decoration: none; }
        .breadcrumb-nav a:hover { text-decoration: underline; }
        .main-content { padding: 30px 0; }
        .document-meta { 
            background: #e8f4fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border-left: 4px solid #007bff;
        }
        .bot-notice {
            background: #e3f2fd;
            border: 1px solid #1976d2;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
            color: #1565c0;
            text-align: center;
        }
        .footer { background: #232536; color: white; padding: 20px 0; text-align: center; }
        .footer a { color: #ccc; }"""
    
    @staticmethod
    def get_document_styles() -> str:
        """Generate document-specific styles"""
        return """
        .static-content { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 2rem; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .document-actions { 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
            text-align: center;
        }
        .action-btn {
            margin: 0 10px;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary { background: #4071a3; color: white; }
        .btn-success { background: #28a745; color: white; }"""
    
    @staticmethod
    def get_navigation_styles() -> str:
        """Generate navigation styles"""
        return """
        .internal-navigation { 
            display: flex; 
            justify-content: space-between; 
            margin: 30px 0; 
            padding: 20px; 
            background: #e2eaf2;
            border-radius: 8px; 
        }
        .internal-navigation a { 
            padding: 10px 20px; 
            background: #e2eaf2;
            text-decoration: none; 
            border-radius: 4px; 
            transition: background 0.3s; 
        }
        .internal-navigation a:hover { background: #c8d7e6; }
        .nav-link {
            color: #007bff;
            text-decoration: none;
            display: flex;
            align-items: center;
        }
        .prev-link {
            /* Inherits from .nav-link */
        }
        .next-link {
            text-align: right;
        }
        .related-content { 
            margin: 30px 0; 
            padding: 20px; 
            background: #e2eaf2;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }
        .related-content h3 { color: #333; margin-bottom: 15px; }
        .related-content ul { list-style: none; padding: 0; }
        .related-content li { margin-bottom: 10px; }
        .related-content a { 
            color: #007bff; 
            text-decoration: none;
            display: block;
            padding: 8px 0;
            border-bottom: 1px solid #d0e1f0;
        }
        .related-content a:hover { text-decoration: underline; }
        .treaty-benefits { margin-top: 30px; padding: 20px; background: #e2eaf2;border-radius: 8px; }
        .treaty-benefits h3 { color: #333; margin-bottom: 15px; }
        .treaty-benefits ul { padding-left: 20px; }
        .treaty-benefits li { margin-bottom: 8px; }"""


def get_document_css_link(document_type: str) -> str:
    """Get document-type specific CSS link"""
    css_map = {
        "articles": "article.css",
        "decisions": "decision.css",
        "guidances": "guide.css",
        "tax-treaties": "dtaa.css",
        "blogs": "blogs.css",
    }
    css_file = css_map.get(document_type, "article.css")
    return f"<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/{css_file}'>"


def generate_unified_html(
    title: str,
    description: str,
    canonical: str,
    doc_meta: str,
    breadcrumb_html: str,
    content: str,
    structured_data: Dict[str, Any],
    document_type: str,
    item: Dict[str, Any],
    internal_nav: str = "",
    related_content: str = "",
    meta_keywords: str = "",
    additional_meta: str = "",
    additional_styles: str = "",
) -> str:
    """
    Unified HTML generation function for all document types.
    Replaces both generate_base_html and generate_blog_base_html.
    """
    # Use provided meta_keywords or generate as fallback
    if document_type == "blogs":
        keywords = meta_keywords or generate_blog_keywords(item)
    else:
        keywords = meta_keywords or generate_keywords(document_type, item)

    # Handle OG image
    if document_type == "blogs":
        og_image = item.get("imageUrl", f"{CONFIG['SITE_URL']}{CONFIG['DEFAULT_OG_IMAGE']}")
    else:
        og_image = f"{CONFIG['SITE_URL']}{CONFIG['DEFAULT_OG_IMAGE']}"
    
    og_image_alt = f"{title} - {CONFIG['SITE_NAME']}"
    
    # Get document type CSS
    doc_type_css = get_document_css_link(document_type)
    
    # Build meta tags
    meta = MetaTags(
        title=title,
        description=description,
        keywords=keywords,
        canonical=canonical,
        og_image=og_image,
        og_image_alt=og_image_alt,
    )
    
    # Generate CSS
    css_gen = CSSGenerator()
    base_styles = css_gen.get_base_styles()
    doc_styles = css_gen.get_document_styles()
    nav_styles = css_gen.get_navigation_styles()
    
    # Prepare title for meta tag
    meta_title = escape_html(item.get('metaTitle', '') or title) if document_type != "blogs" else title
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="index, follow" />
    <meta name="theme-color" content="#232536" />
    
    <!-- SEO Meta Tags -->
    <title>{meta_title}</title>
    
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="sitemap" type="application/xml" title="Sitemap" href="{CONFIG['SITE_URL']}/sitemap.xml" />
    
    <!-- Document Type Specific CSS -->
    {doc_type_css}
    
    <!-- Open Graph / Facebook -->
    {meta.get_og_tags()}
    
    <!-- Twitter -->
    {meta.get_twitter_tags()}
    
    {additional_meta}
    
    <!-- Additional SEO -->
    <meta name="author" content="Team GTL" />
    <meta name="geo.region" content="AE" />
    <meta name="geo.placename" content="UAE" />
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>
    
    <!-- Critical CSS -->
    <style>
        {base_styles}
        {doc_styles}
        {nav_styles}
        {additional_styles}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <p><strong>{CONFIG['SITE_NAME']}</strong></p>
            <nav>
                <a href="/">Home</a>
                <a href="{CONFIG['PUBLIC_PATH']}/articles">Articles</a>
                <a href="{CONFIG['PUBLIC_PATH']}/decisions">Decisions</a>
                <a href="{CONFIG['PUBLIC_PATH']}/guidances">Guidance</a>
                <a href="{CONFIG['PUBLIC_PATH']}/tax-treaties">Treaties</a>
                <a href="{CONFIG['PUBLIC_PATH']}/blogs">Blogs</a>
            </nav>
        </div>
    </div>

    {breadcrumb_html}

    <div class="main-content">
        <div class="container">
            {doc_meta}
            
            <div class="{"blog-content" if document_type == "blogs" else "static-content"}">
                {content}
            </div>

            {internal_nav}
            {related_content}

            <div class="bot-notice">
                🤖 This page is optimized for search engines and web crawlers. 
                <a href="/">Visit our main site</a> for the full interactive experience.
            </div>
        </div>
    </div>

    <div class="footer">
        <div class="container">
            <p>&copy; {datetime.now(timezone.utc).year} {CONFIG['SITE_NAME']}. All rights reserved.</p>
            <p>
                <a href="/">Home</a> | 
                <a href="{CONFIG['PUBLIC_PATH']}/articles">Articles</a> | 
                <a href="{CONFIG['PUBLIC_PATH']}/decisions">Decisions</a> |
                <a href="{CONFIG['PUBLIC_PATH']}/guidances">Guidance</a> |
                <a href="{CONFIG['PUBLIC_PATH']}/tax-treaties">Treaties</a> |
                <a href="{CONFIG['PUBLIC_PATH']}/blogs">Blogs</a>
            </p>
        </div>
    </div>
</body>
</html>"""


class BodyExtractor(HTMLParser):
    """Extract content between <body> tags"""

    def __init__(self):
        super().__init__()
        self.in_body = False
        self.body_content = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "body":
            self.in_body = True
        elif self.in_body:
            attrs_str = " ".join([f'{k}="{v}"' for k, v in attrs])
            self.body_content.append(
                f"<{tag} {attrs_str}>" if attrs_str else f"<{tag}>"
            )

    def handle_endtag(self, tag):
        if tag.lower() == "body":
            self.in_body = False
        elif self.in_body:
            self.body_content.append(f"</{tag}>")

    def handle_data(self, data):
        if self.in_body:
            self.body_content.append(data)

    def get_body_content(self):
        return "".join(self.body_content)


def extract_body_content(html_content: str) -> str:
    """Extract only content between <body> tags, excluding the body tags themselves"""
    if not html_content:
        return "<p>Content not available</p>"

    # Try to find body tags
    body_match = re.search(
        r"<body[^>]*>(.*?)</body>", html_content, re.DOTALL | re.IGNORECASE
    )
    if body_match:
        return body_match.group(1).strip()

    # Fallback: use HTMLParser
    parser = BodyExtractor()
    try:
        parser.feed(html_content)
        content = parser.get_body_content()
        return content if content else html_content
    except:
        # Last resort: return original content
        return html_content


# Helper functions
def render_title(text: str) -> str:
    """Render title text that may contain intentional HTML tags (like span for styling).
    Does not escape if the text contains HTML tags, otherwise escapes for safety."""
    if not text:
        return ""
    # If text contains HTML tags (specifically span tags used for styling), return as-is
    if "<span" in text or "</span>" in text:
        return str(text)
    # Otherwise, escape for safety
    return html.escape(str(text))


def truncate_text(text: str, max_length: int) -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text or ""
    return text[:max_length].strip() + "..."


def clean_content(content: str) -> str:
    """Clean HTML content for display"""
    if not content:
        return "<p>Content not available</p>"

    # Fix internal links by adding PUBLIC_PATH prefix for local testing
    # Pattern: href="/articles/slug" or href='/articles/slug' (both single and double quotes)
    doc_types = ["articles", "decisions", "guidances", "blogs", "tax-treaties"]

    for doc_type in doc_types:
        # Handle double quotes: href="/doctype/something"
        content = re.sub(
            rf'href="/{doc_type}/([^"]+?)"',
            rf'href="{CONFIG["PUBLIC_PATH"]}/{doc_type}/\1"',
            content,
            flags=re.IGNORECASE,
        )

        # Handle single quotes: href='/doctype/something'
        content = re.sub(
            rf"href='/{doc_type}/([^']+?)'",
            rf"href='{CONFIG['PUBLIC_PATH']}/{doc_type}/\1'",
            content,
            flags=re.IGNORECASE,
        )

    return content


def generate_slug(text: str) -> str:
    """Generate URL-friendly slug from text"""
    if not text:
        return "unknown"
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug.strip("-")


def get_country_flag(country_code: str) -> str:
    """Get flag emoji for country code"""
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


def generate_article_slug(
    law_short_name: str, article_number: str, country_name: str = None
) -> str:
    """Generate article slug based on country, law and article number
    Example: uae-cit-fdl-47-of-2022-article-1
    """
    country_prefix = ""
    if country_name:
        country_prefix = f"{generate_slug(country_name)}"

    return f"{country_prefix}-{law_short_name}-article-{article_number}"


def generate_decision_slug(
    law_short_name: str,
    decision_number: str,
    decision_year: str,
    decision_type: str = None,
    country_name: str = None,
) -> str:
    """Generate decision slug based on country, law, type, number and year
    Example: uae-cit-fdl-47-of-2022-cd-35-of-2025
    some decisions dont have number OR during parsing we are not aware of them
    Decision types stored as:
    - CD - Cabinet Decision
    - BL - Bylaws
    - MD - Ministerial Decision
    - FTA - Federal Tax Authority Decision
    - ZD - ZATCA Decision
    - TD - Tax Department, Ministry of Finance
    - ER - Executive Rules & Instructions
    """
    country_prefix = ""
    if country_name:
        country_prefix = f"{generate_slug(country_name)}"

    # Extract type abbreviation by splitting on '-' and taking first part
    type_abbrev = "cd"  # Default
    if decision_type:
        type_abbrev = decision_type.split("-")[0].strip().lower()

    # Clean up decision number (remove spaces, slashes, etc.)
    clean_number = re.sub(r"[^\w-]", "-", str(decision_number))
    clean_number = re.sub(r"-+", "-", clean_number).strip("-")

    if decision_year:
        return f"{country_prefix}-{law_short_name}-{type_abbrev}-{clean_number}-of-{decision_year}"
    else:
        return f"{country_prefix}-{law_short_name}-{type_abbrev}-{clean_number}"


def generate_guidance_slug(law_slug: str, guidance_type: str, unique_code: str) -> str:
    """Generate guidance slug: lawSlug-type-uniqueCode
    Example: uae-cit-fdl-47-of-2022-guide-CTGFF1

    Guidance types stored as:
    - GUIDE - Federal Tax Authority Guide
    - PC - Public Clarification
    - GUIDE - Zakat, Tax and Customs Authority
    - GUIDE - Foreign Account Tax Compliance Act Guide
    - GUIDE - VAT Taxpayer Guide
    - GUIDE - Oman Tax Authority
    - CIRCULAR - Circular
    - MANUAL - User Manual
    """
    # Extract type abbreviation by splitting on '-' and taking first part
    type_abbrev = "guide"  # Default
    if guidance_type:
        type_abbrev = guidance_type.split("-")[0].strip().lower()

    # Simple format: lawSlug-type-uniqueCode
    return f"{law_slug}-{type_abbrev}-{unique_code}"


def generate_treaty_slug(country1_slug: str, country2_alpha3: str) -> str:
    """Generate treaty slug based on country slugs and alpha3 codes
    Example: uae-alb-dtaa

    Args:
        country1_slug: Usually 'uae'
        country2_alpha3: 3-letter country code (e.g., 'ALB', 'USA', 'GBR')
    """
    # Ensure country1 is lowercase
    country1_clean = country1_slug.lower() if country1_slug else "uae"

    # Convert alpha3 code to lowercase
    country2_clean = country2_alpha3.lower() if country2_alpha3 else "unknown"

    return f"{country1_clean}-{country2_clean}-dtaa"


# generate_slug_from_title
def generate_blog_slug(title: str) -> str:
    """
    Generates a URL-friendly slug from a title.
    """
    if not title:
        import time

        return f"blog-{int(time.time())}"

    # 1. Strip HTML tags (title.replaceAll("<[^>]*>", ""))
    clean_title = re.sub(r"<[^>]*>", "", title)

    # 2. Decode common HTML entities
    # Using a simple dictionary for the most common ones
    entity_map = {
        "&amp;": "&",
        "&lt;": "<",
        "&gt;": ">",
        "&quot;": '"',
        "&#39;": "'",
        "&nbsp;": " ",
    }
    for entity, char in entity_map.items():
        clean_title = clean_title.replace(entity, char)

    # 3. Lowercase conversion
    clean_title = clean_title.lower()

    # 4. Remove special characters (except a-z, 0-9, whitespace, and hyphen)
    # replaceAll("[^a-z0-9\\s-]", "")
    clean_title = re.sub(r"[^a-z0-9\s-]", "", clean_title)

    # 5. Replace spaces with a single hyphen (replaceAll("\\s+", "-"))
    clean_title = re.sub(r"\s+", "-", clean_title).strip()

    # 6. Replace multiple hyphens with a single one (replaceAll("-+", "-"))
    clean_title = re.sub(r"-+", "-", clean_title)

    # 7. Remove leading/trailing hyphens (replaceAll("^-|-$", ""))
    return clean_title.strip("-")


def get_authority_name(law_slug: str) -> str:
    """Get the appropriate tax authority name based on the law slug

    Determines the issuing authority based on the lawSlug/country prefix.

    Examples:
    - law_slug="uae-cit-..." -> "Federal Tax Authority"
    - law_slug="ksa-vat-..." -> "Zakat, Tax and Customs Authority"
    - law_slug="oman-vat-..." -> "Oman Tax Authority"
    - law_slug="kwt-vat-..." or "law_slug="kuwait-..." -> "Ministry of Finance - Kuwait"
    - law_slug="qatar-vat-..." -> "General Tax Authority - Qatar"
    - law_slug="bahrain-vat-..." -> "National Bureau for Revenue - Bahrain"
    - law_slug="gcc-vat-..." -> "GCC Secretariat General"
    """
    if law_slug:
        # Check law_slug for country-based authority
        law_slug = law_slug.lower()  # Ensure case-insensitive matching

        if law_slug.startswith("uae-"):
            return "Federal Tax Authority"
        elif law_slug.startswith("ksa-"):
            return "Zakat, Tax and Customs Authority"
        elif law_slug.startswith("oman-"):
            return "Oman Tax Authority"
        # Check for both 'kwt-' and 'kuwait-'
        elif law_slug.startswith("kwt-") or law_slug.startswith("kuwait-"):
            return "Ministry of Finance - Kuwait"
        elif law_slug.startswith("qatar-"):
            return "General Tax Authority - Qatar"
        elif law_slug.startswith("bahrain-"):
            return "National Bureau for Revenue - Bahrain"
        # If the slug doesn't match a specific country prefix,
        # it might be a general GCC document.
        else:
            return "GCC Secretariat General"
    # Default fallback if law_slug is None or an empty string
    return "Tax Authority"


def generate_internal_links(
    current_item: Dict, all_items: List[Dict], doc_type: str
) -> str:
    """Generate prev/next navigation to reduce orphan pages"""
    # Only show navigation buttons for articles, not for decisions, guides, or tax-treaties
    if doc_type not in ["articles", "blogs"]:
        return ""

    if not all_items or len(all_items) < 2:
        return ""

    current_index = -1
    for i, item in enumerate(all_items):
        if item.get("slug") == current_item.get("slug"):
            current_index = i
            break

    if current_index == -1:
        return ""

    links_html = '<div class="internal-navigation">'

    # Previous link
    if current_index > 0:
        prev_item = all_items[current_index - 1]
        links_html += f"""
        <a href="{CONFIG['PUBLIC_PATH']}/{doc_type}/{prev_item['slug']}" class="nav-link prev-link">
            <span style="margin-right: 12px; font-size: 20px; flex-shrink: 0;">&larr;</span>
            <div class="nav-link-content">
                <div class="nav-link-label">Previous</div>
                <div class="nav-link-title">{render_title(prev_item.get('title', ''))}</div>
            </div>
        </a>"""
    else:
        links_html += "<div></div>"

    # Next link
    if current_index < len(all_items) - 1:
        next_item = all_items[current_index + 1]
        links_html += f"""
        <a href="{CONFIG['PUBLIC_PATH']}/{doc_type}/{next_item['slug']}" class="nav-link next-link">
            <div class="nav-link-content">
                <div class="nav-link-label">Next</div>
                <div class="nav-link-title">{render_title(next_item.get('title', ''))}</div>
            </div>
            <span style="margin-left: 12px; font-size: 20px; flex-shrink: 0;">&rarr;</span>
        </a>"""
    else:
        links_html += "<div></div>"

    links_html += "</div>"
    return links_html


def parse_related_doc_url(url: str) -> Optional[Dict[str, str]]:
    """Parse a relatedDocs URL to extract doc type, law slug, and identifiers

    Examples:
    - /articles/uae-cit-fdl-47-of-2022-article-18
    - /decisions/uae-cit-fdl-47-of-2022-md-68-of-2023
    - /guidances/uae-cit-fdl-47-of-2022-guide-CTGGCT1
    - /tax-treaties/uae-dtaa-india
    """
    if not url or not url.startswith("/"):
        return None

    # Remove leading slash and split
    parts = url[1:].split("/", 1)
    if len(parts) != 2:
        return None

    doc_type = parts[0]  # articles, decisions, guidances, tax-treaties
    slug = parts[1]

    return {"doc_type": doc_type, "slug": slug, "url": url}


def find_related_docs_from_json(
    related_doc_urls: List[str], all_laws_data: List[Dict]
) -> List[Dict]:
    """Find related documents from JSON data based on relatedDocs URLs

    Args:
        related_doc_urls: List of URLs from relatedDocs field
        all_laws_data: All law data loaded from JSON files

    Returns:
        List of dicts with {title, slug, doc_type, url} for each found document
    """
    found_docs = []

    for url in related_doc_urls:
        # Handle /laws/ URLs specially - render them as-is without looking up in JSON
        if url.strip().startswith("/laws/"):
            found_docs.append(
                {
                    "title": url.strip(),  # Use the URL itself as anchor text
                    "slug": "",
                    "doc_type": "laws",
                    "url": url.strip(),
                }
            )
            continue

        parsed = parse_related_doc_url(url)
        if not parsed:
            continue

        doc_type = parsed["doc_type"]
        target_slug = parsed["slug"]

        # Search through all laws data
        for law_data in all_laws_data:
            if "laws" not in law_data:
                continue

            for law in law_data["laws"]:
                # Search in articles
                if doc_type == "articles" and "articles" in law:
                    for article in law["articles"]:
                        article_slug = generate_article_slug(
                            law.get("lawShortName", ""),
                            article.get("number", ""),
                            law_data.get("countryName", ""),
                        )
                        if article_slug == target_slug:
                            found_docs.append(
                                {
                                    "title": article.get("title", "Untitled"),
                                    "slug": article_slug,
                                    "doc_type": "articles",
                                    "url": url,
                                }
                            )
                            break

                # Search in decisions
                elif doc_type == "decisions" and "decisions" in law:
                    for decision in law["decisions"]:
                        decision_slug = generate_decision_slug(
                            law.get("lawShortName", ""),
                            decision.get("number", ""),
                            decision.get("year", ""),
                            decision.get("type", ""),
                            law_data.get("countryName", ""),
                        )
                        if decision_slug == target_slug:
                            found_docs.append(
                                {
                                    "title": decision.get("title", "Untitled"),
                                    "slug": decision_slug,
                                    "doc_type": "decisions",
                                    "url": url,
                                }
                            )
                            break

                # Search in guidances
                elif doc_type == "guidances" and "guidances" in law:
                    for guidance in law["guidances"]:
                        guidance_slug = generate_guidance_slug(
                            law.get("lawShortName", ""),
                            guidance.get("type", ""),
                            guidance.get("code", ""),
                            law_data.get("countryName", ""),
                        )
                        if guidance_slug == target_slug:
                            found_docs.append(
                                {
                                    "title": guidance.get("title", "Untitled"),
                                    "slug": guidance_slug,
                                    "doc_type": "guidances",
                                    "url": url,
                                }
                            )
                            break

                # Search in tax treaties
                elif doc_type == "tax-treaties" and "treaties" in law:
                    for treaty in law["treaties"]:
                        treaty_slug = generate_treaty_slug(
                            treaty.get("name", ""),
                            law_data.get("countryName", ""),
                        )
                        if treaty_slug == target_slug:
                            found_docs.append(
                                {
                                    "title": treaty.get("title", "Untitled"),
                                    "slug": treaty_slug,
                                    "doc_type": "tax-treaties",
                                    "url": url,
                                }
                            )
                            break

    return found_docs


def generate_related_docs_html(
    related_doc_urls: List[str], all_laws_data: List[Dict]
) -> str:
    """Generate HTML for related documents section based on relatedDocs field"""
    if not related_doc_urls:
        return ""

    found_docs = find_related_docs_from_json(related_doc_urls, all_laws_data)

    if not found_docs:
        return ""

    html = """
    <div class="related-content">
        <h3 style="margin-top: 0; color: #232536; font-size: 18px;">Related Documents</h3>
        <ul style="list-style: none; padding: 0; margin: 0;">"""

    for doc in found_docs:
        html += f"""
            <li style="margin-bottom: 10px;">
                <a href="{doc['url']}" class="related-link">
                    &rarr; {render_title(doc.get('title', 'Untitled'))}
                </a>
            </li>"""

    html += "</ul></div>"
    return html


# Main HTML generation functions
def generate_article_html(
    article: Dict[str, Any],
    law_info: Dict[str, Any],
    country_info: Dict[str, Any],
    all_articles: List[Dict[str, Any]] = None,
    all_laws_data: List[Dict] = None,
) -> tuple[str, str]:
    """Generate HTML for article documents"""
    article_slug = generate_article_slug(
        law_info.get("lawShortName", ""),
        article.get("number", ""),
        country_info.get("countryName", ""),
    )
    canonical = f"{CONFIG['SITE_URL']}/articles/{article_slug}"

    # Build path string from article path
    path_parts = []
    if article.get("path"):
        for path_item in article["path"]:
            path_parts.append(path_item.get("name", ""))
    path_string = " &rsaquo; ".join(path_parts) if path_parts else ""

    # Use metaDescription and metaKeywords from JSON
    # Check if title already starts with "Article" to avoid duplication
    article_title = article.get("title", "")
    if article_title.lower().startswith("article"):
        title = f"{escape_html(article_title)} | {law_info.get('lawFullName', '')} | {CONFIG['SITE_NAME']}"
    else:
        title = f"Article {article.get('number', '')} - {escape_html(article_title)} | {law_info.get('lawFullName', '')} | {CONFIG['SITE_NAME']}"

    description = (
        article.get("metaDescription", "")
        or f"Article {article.get('number', '')}: {escape_html(truncate_text(article.get('textOnly', ''), 140))}"
    )
    meta_keywords = article.get("metaKeywords", "")

    # Generate breadcrumbs for articles
    breadcrumbs = [
        '<a href="/">Home</a>',
        f'<a href="{CONFIG["PUBLIC_PATH"]}/articles">Articles</a>',
    ]

    # Add law name
    breadcrumbs.append(
        f'<a href="{CONFIG["PUBLIC_PATH"]}/laws/{country_info.get("countryName", "")}/{escape_html(law_info.get("lawShortName", ""))}">{escape_html(law_info.get("lawShortName", ""))}</a>'
    )

    # Add the current article as the final breadcrumb
    article_title = article.get("title", "")
    # Check if title already starts with "Article {number}" to avoid duplication
    if not article_title.lower().startswith(f"article {article.get('number', '')}"):
        article_breadcrumb_title = (
            f"Article {article.get('number', '')} - {article_title}"
        )
    else:
        article_breadcrumb_title = article_title
    breadcrumbs.append(f"<strong>{escape_html(article_breadcrumb_title[:60])}</strong>")

    breadcrumb_html = f"""
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            {' &rsaquo; '.join(breadcrumbs)}
        </div>
    </nav>"""

    # Document metadata
    doc_meta = f"""
    <div class="document-meta">
        <strong>Document Type:</strong> Tax Law Article<br>
        <strong>Law:</strong> {escape_html(law_info.get('lawFullName', ''))}<br>
        <strong>Article Number:</strong> {article.get('number', 'N/A')}<br>
        <strong>Country:</strong> {get_country_flag(country_info.get('flagCode', ''))} {escape_html(country_info.get('countryName', ''))}<br>
        {f"<strong>Location:</strong> {escape_html(path_string)}<br>" if path_string else ''}
        <strong>Order:</strong> {article.get('orderIndex', 'N/A')}<br>
       <strong>Last updated at:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
    </div>"""

    # Structured data
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Legislation",
        "@id": canonical,
        "name": escape_json(article.get("title", "")),
        "legislationIdentifier": f"Article {article.get('number', '')}",
      "legislationType": "Tax Law Article",
        "description": escape_json(
            article.get("metaDescription", "")
            or truncate_text(article.get("textOnly", ""), 155)
        ),
        "url": canonical,
        "datePublished": article.get(
            "publishedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "dateModified": article.get(
            "modifiedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "legislationJurisdiction": StructuredDataBuilder.get_country_schema(country_info.get("countryName", "")),
        "author": StructuredDataBuilder.get_organization_schema("GCC Tax Laws"),
        "publisher": StructuredDataBuilder.get_organization_schema(CONFIG["SITE_NAME"]),
        "mainEntityOfPage": StructuredDataBuilder.get_webpage_schema(canonical),
        "inLanguage": StructuredDataBuilder.get_language_schema(),
        "about": {
            "@type": "Thing", 
            "name": "Tax Law",
            "description": f"{escape_json(country_info.get('countryName', ''))} tax legislation and regulations",
        },
        "mentions": [
            {
                "@type": "Organization",
                "name": get_authority_name(
                    law_slug=law_info.get(
                        "lawSlug",
                        f"{country_info.get('countryName', '').lower()}-{law_info.get('lawShortName', '').lower()}",
                    )
                ),
            },
            StructuredDataBuilder.get_country_schema(country_info.get("countryName", "")),
        ],
    "isPartOf": {
        "@type": "Legislation",
        "name": escape_json(law_info.get("lawFullName", "")),
        "legislationIdentifier": law_info.get("lawShortName", ""),
        "legislationJurisdiction": escape_json(country_info.get("countryName", "")),
    },
     "keywords": article.get("metaKeywords", "") or generate_keywords("articles", article),

    **({"identifier": {
        "@type": "PropertyValue",
        "name": "Article Number",
        "value": article.get("number", ""),
    }} if article.get("number") else {}),

    **({"wordCount": len(article.get("content", "").split())} if article.get("content") else {}),

    }

    # Extract body content only
    article_content = clean_content(article.get("content", ""))
    article_content = extract_body_content(article_content)

    # Generate internal navigation and related content
    internal_nav = ""
    related_content = ""
    if all_articles:
        internal_nav = generate_internal_links(
            {"slug": article_slug, "title": article.get("title", "")},
            all_articles,
            "articles",
        )

    # Generate related content from relatedDocs field only
    if article.get("relatedDocs") and all_laws_data:
        related_content = generate_related_docs_html(
            article.get("relatedDocs"), all_laws_data
        )

    return (
        generate_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=article_content,
            structured_data=structured_data,
            document_type="articles",
            item=article,
            internal_nav=internal_nav,
            related_content=related_content,
            meta_keywords=meta_keywords,
        ),
        article_slug,
    )


def generate_decision_html(
    decision: Dict[str, Any],
    law_info: Dict[str, Any],
    country_info: Dict[str, Any],
    all_decisions: List[Dict[str, Any]] = None,
    all_laws_data: List[Dict] = None,
) -> tuple[str, str]:
    """Generate HTML for decision documents"""
    decision_slug = generate_decision_slug(
        law_info.get("lawShortName", ""),
        decision.get("number", ""),
        decision.get("year", ""),
        decision.get("type", ""),  # Already stored as "CD - Cabinet Decision"
        country_info.get("countryName", ""),
    )
    canonical = f"{CONFIG['SITE_URL']}/decisions/{decision_slug}"

    decision_type = decision.get("type", "Decision")
    # Use title from JSON directly (it already contains proper formatting)
    title = f"{render_title(decision.get('title', ''))} {decision_type} {decision.get('number', '')}/{decision.get('year', '')} | {law_info.get('lawFullName', '')} | {CONFIG['SITE_NAME']}"
    # Use metaDescription and metaKeywords from JSON
    description = (
        decision.get("metaDescription", "")
        or f"{decision_type} {decision.get('number', '')} of {decision.get('year', '')}: {escape_html(truncate_text(decision.get('textOnly', ''), 120))}"
    )
    meta_keywords = decision.get("metaKeywords", "")

    # Document metadata
    doc_meta = f"""
    <div class="document-meta">
        <strong>Document Type:</strong> {escape_html(decision_type)}<br>
        <strong>Law:</strong> {escape_html(law_info.get('lawFullName', ''))}<br>
        <strong>Decision Number:</strong> {decision.get('number', 'N/A')}<br>
        <strong>Year:</strong> {decision.get('year', 'N/A')}<br>
        <strong>Country:</strong> {get_country_flag(country_info.get('flagCode', ''))} {escape_html(country_info.get('countryName', ''))}<br>
        <strong>Official Name:</strong> {escape_html(decision.get('name', ''))}
       <br><strong>Last updated at:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}        
    </div>"""

    # Breadcrumbs
    breadcrumb_html = f"""
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            <a href="/">Home</a> &rsaquo; <a href="{CONFIG['PUBLIC_PATH']}/decisions">Decisions</a> &rsaquo; <strong>{render_title(decision.get('title', ''))}</strong>
        </div>
    </nav>"""

    # Structured data
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Legislation",
        "@id": canonical,
        "name": escape_json(decision.get("title", "")),
    "headline": escape_json(decision.get("name", "")),
    "legislationIdentifier": decision.get("number", ""),
    "legislationType": escape_json(decision_type),
    "legislationDate": decision.get("issueDate", decision.get("year", "")),
    "description": escape_json(
        decision.get("metaDescription", "")
        or truncate_text(decision.get("textOnly", ""), 155)
    ),
    "url": canonical,
    "datePublished": decision.get(
        "year", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),
    "dateModified": decision.get(
        "modifiedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),
    "dateCreated": decision.get(  # ADD THIS
        "modifiedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),
    "legislationJurisdiction": {
        "@type": "Country", 
        "name": escape_json(country_info.get("countryName", "")),
    },

    "author": StructuredDataBuilder.get_organization_schema("GCC Tax Laws"),
    "publisher": StructuredDataBuilder.get_organization_schema(CONFIG["SITE_NAME"]),
    "mainEntityOfPage": StructuredDataBuilder.get_webpage_schema(canonical),
    "temporalCoverage": str(decision.get("year", "")),
    "inLanguage": StructuredDataBuilder.get_language_schema(),
    "about": {
        "@type": "Thing",
        "name": "Tax Decision",
        "description": f"{escape_json(country_info.get('countryName', ''))} official tax authority ruling and decision",
    },
    "mentions": [
        {
            "@type": "Organization",
            "name": get_authority_name(
                law_slug=law_info.get(
                    "lawSlug",
                    f"{country_info.get('countryName', '').lower()}-{law_info.get('lawShortName', '').lower()}",
                )
            ),
        },
        StructuredDataBuilder.get_country_schema(country_info.get("countryName", "")),
    ],
    "isBasedOn": {
        "@type": "Legislation",
        "name": escape_json(law_info.get("lawFullName", "")),
    },
    "keywords": decision.get("metaKeywords", "") or generate_keywords("decisions", decision),
    **({"identifier": {
        "@type": "PropertyValue",
        "name": "Decision Number",
        "value": f"{decision.get('type', '').split('-')[0].strip()} {decision.get('number', '')} of {decision.get('year', '')}".strip(),
    }} if decision.get("number") else {}),
    **({"category": decision.get("category", "")} if decision.get("category") else {}),
    **({"wordCount": len(decision.get("content", "").split())} if decision.get("content") else {}),   
        }

    # Extract body content only
    decision_content = clean_content(decision.get("content", ""))
    decision_content = extract_body_content(decision_content)

    # Generate internal navigation
    internal_nav = ""
    related_content = ""
    if all_decisions:
        internal_nav = generate_internal_links(
            {"slug": decision_slug, "title": decision.get("title", "")},
            all_decisions,
            "decisions",
        )

    # Generate related content from relatedDocs field only
    if decision.get("relatedDocs") and all_laws_data:
        related_content = generate_related_docs_html(
            decision.get("relatedDocs"), all_laws_data
        )

    return (
        generate_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=decision_content,
            structured_data=structured_data,
            document_type="decisions",
            item=decision,
            internal_nav=internal_nav,
            related_content=related_content,
            meta_keywords=meta_keywords,
        ),
        decision_slug,
    )


def generate_guidance_html(
    guidance: Dict[str, Any],
    law_info: Dict[str, Any] = None,
    all_guidances: List[Dict[str, Any]] = None,
    all_laws_data: List[Dict] = None,
) -> tuple[str, str]:
    """Generate HTML for guidance documents"""
    # Get lawSlug from law_info or guidance data
    law_slug = guidance.get("lawSlug", "")
    if not law_slug and law_info:
        law_slug = law_info.get("lawSlug", law_info.get("slug", ""))

    guidance_slug = generate_guidance_slug(
        law_slug,
        guidance.get(
            "type", ""
        ),  # Already stored as "GUIDE - Federal Tax Authority Guide"
        guidance.get("uniqueCode", ""),
    )
    canonical = f"{CONFIG['SITE_URL']}/guidances/{guidance_slug}"

    guidance_type = guidance.get("type", "Guidance")
    # Use title from JSON directly (it already contains proper formatting)
    title = f"{escape_html(guidance.get('title', ''))} | {guidance_type} | {CONFIG['SITE_NAME']}"
    # Use metaDescription and metaKeywords from JSON
    description = (
        guidance.get("metaDescription", "")
        or f"Official FTA guidance {guidance.get('uniqueCode', '')}: {escape_html(truncate_text(guidance.get('textOnly', '') or guidance.get('text', ''), 130))}"
    )
    meta_keywords = guidance.get("metaKeywords", "")
    
    country_name = "United Arab Emirates"  # Default
    if law_slug:
        country_prefix = law_slug.split("-")[0].lower()
        country_map = {
            "uae": "United Arab Emirates",
            "ksa": "Saudi Arabia",
            "kwt": "Kuwait",
            "qatar": "Qatar",
            "bahrain": "Bahrain",
            "oman": "Oman",
        }
        country_name = country_map.get(country_prefix, "United Arab Emirates")

    # Get authority name based on guidance type and law slug
    authority_name = get_authority_name(law_slug)

    # Document metadata
    doc_meta = f"""
    <div class="document-meta">
        <strong>Document Type:</strong> {escape_html(guidance_type)}<br>
        <strong>Guidance Code:</strong> {guidance.get('uniqueCode', 'N/A')}<br>
        <strong>Year:</strong> {guidance.get('year', 'N/A')}<br>
        <strong>Related Law:</strong> {escape_html(guidance.get('lawSlug', 'N/A'))}<br>
        <strong>Authority:</strong> {escape_html(authority_name)}
       <br><strong>Last updated at:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
    </div>"""

    # Breadcrumbs
    breadcrumb_html = f"""
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            <a href="/">Home</a> &rsaquo; <a href="{CONFIG['PUBLIC_PATH']}/guidances">Guidance</a> &rsaquo; <strong>{escape_html(guidance.get('title', ''))}</strong>
        </div>
    </nav>"""

    # Structured data
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Legislation", 
    "@id": canonical,
    "name": escape_json(guidance.get("title", "")),
    "headline": escape_json(guidance.get("metaTitle", "") or guidance.get("title", "")),
    "description": escape_json(
        guidance.get("metaDescription", "")
        or truncate_text(
            guidance.get("textOnly", "") or guidance.get("text", ""), 155
        )
    ),
    "url": canonical,
    "datePublished": guidance.get(
        "year", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),
    "dateModified": guidance.get(
        "modifiedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    ),

    "legislationType": guidance.get("type", "Tax Guidance"),
    "legislationJurisdiction": { 
        "@type": "Country",
        "name": country_name,
    },

    "provider": {
        "@type": "Organization",
        "name": "GCC Tax Laws",
        "url": "https://gcctaxlaws.com",
        "logo": {
            "@type": "ImageObject",
            "url": f"{CONFIG['SITE_URL']}/web-app-manifest-512x512.png",
            "width": 180,
            "height": 60,
        },
        "alternateName": "GTL",
    },
    "publisher": {
        "@type": "Organization",
        "name": CONFIG["SITE_NAME"],
        "logo": {
            "@type": "ImageObject",
            "url": f"{CONFIG['SITE_URL']}/web-app-manifest-512x512.png",
            "width": 180,
            "height": 60,
        },
        "alternateName": "GTL",
    },
    "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},

    "inLanguage": { 
        "@type": "Language",
        "name": "English",
        "alternateName": "en",
    },
    "about": {
        "@type": "Thing",
        "name": "Tax Guidance", 
        "description": f"{country_name} tax guidance and procedures",
    },

    "mentions": [
        {
            "@type": "Organization",
            "name": authority_name,
        },
        {
            "@type": "Country",
            "name": country_name, 
        },
    ],
    }
    
    # Extract body content only
    guidance_content = clean_content(guidance.get("content", ""))
    guidance_content = extract_body_content(guidance_content)

    # Generate internal navigation
    internal_nav = ""
    related_content = ""
    if all_guidances:
        internal_nav = generate_internal_links(
            {"slug": guidance_slug, "title": guidance.get("title", "")},
            all_guidances,
            "guidances",
        )

    # Generate related content from relatedDocs field only
    if guidance.get("relatedDocs") and all_laws_data:
        related_content = generate_related_docs_html(
            guidance.get("relatedDocs"), all_laws_data
        )

    return (
        generate_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=guidance_content,
            structured_data=structured_data,
            document_type="guidances",
            item=guidance,
            internal_nav=internal_nav,
            related_content=related_content,
            meta_keywords=meta_keywords,
        ),
        guidance_slug,
    )


def generate_treaty_html(
    treaty: Dict[str, Any],
    all_treaties: List[Dict[str, Any]] = None,
    all_laws_data: List[Dict] = None,
) -> tuple[str, str]:
    """Generate HTML for tax treaty documents"""
    treaty_slug = generate_treaty_slug(
        treaty.get("country1Slug", "uae"), treaty.get("country2Alpha3Code", "")
    )
    canonical = f"{CONFIG['SITE_URL']}/tax-treaties/{treaty_slug}"

    # country2_name = treaty.get("country2Name", "Unknown")  -> Removed this duplicate initializtion
    # print(f"/***&&****/Generating treaty HTML for:{country2Name}") 
    
    country2Name = treaty.get("country2Name", "Unknown")
    country1Slug = treaty.get("country1Slug", "uae").upper()

    # print(f"/***&&****/Generating treaty HTML for: {country1Slug} - {country2Name}")    
    
    # Use title from JSON if available, otherwise generate it
    treaty_title = treaty.get("metaTitle", "")
    title = f"{treaty_title} | {CONFIG['SITE_NAME']}"

    translation_status = (
        "Official" if treaty.get("officialTranslation") == True else "Unofficial"
    )
    # Use metaDescription and metaKeywords from JSON
    description = (
        treaty.get("metaDescription", "")
        or f"Double Taxation Avoidance Agreement between {country1Slug} and {country2Name}. {translation_status} translation."
    )
    meta_keywords = treaty.get("metaKeywords", "")
    
    # country2Name = treaty.get("country2Name", "Unknown") # removing here because already defined above
    # country1Slug = treaty.get("country1Slug", "uae").upper()
    
    # Document metadata
    flag_code = treaty.get("flagCode", "")
    country_flag = get_country_flag(flag_code)
    doc_meta = f"""
    <div class="document-meta">
        <strong>Document Type:</strong> Double Taxation Agreement<br>
        <strong>Countries:</strong> {country1Slug} - {country2Name}<br>
        <strong>Translation:</strong> {translation_status}<br>
        {f"<strong>Year:</strong> {treaty.get('year', 'N/A')}<br>" if treaty.get('year') else ''}
        {f"<strong>Issue Date:</strong> {treaty.get('issueDate', 'N/A')}<br>" if treaty.get('issueDate') else ''}
       <br><strong>Last updated at:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
    </div>"""

    # Breadcrumbs
    breadcrumb_html = f"""
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            <a href="/">Home</a> &rsaquo; <a href="{CONFIG['PUBLIC_PATH']}/tax-treaties">Tax Treaties</a> &rsaquo; <strong>{country1Slug}-{escape_html(country2Name)} Treaty</strong>
        </div>
    </nav>"""

    # Structured data
    structured_data = {
        "@context": "https://schema.org",
        "@type": "Legislation",
        "@id": canonical,
        "name": escape_json(treaty.get("title", "")),
        "alternateName": f"DTAA between {country1Slug} and {country2Name}",
        "legislationIdentifier": treaty.get(
            "treatyNumber",
            f"{treaty.get('country1Slug')}-{treaty.get('country2Alpha3Code').lower()}-dtaa",
        ),
        "legislationType": "International Tax Treaty",
        "legislationDate": treaty.get("signingDate", treaty.get("issueDate", "")),
        "description": escape_json(
            treaty.get("metaDescription", "")
            or f"Double Taxation Avoidance Agreement between {country1Slug} and {country2Name}"
        ),
        "url": canonical,
        "datePublished": treaty.get(
            "publishedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "dateModified": treaty.get(
            "modifiedDate", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        ),
        "legislationJurisdiction": [
            {
                "@type": "Country",
                "name": country1Slug,
                "identifier": treaty.get("country1Slug", ""),
            },
            {
                "@type": "Country",
                "name": country2Name,
                "identifier": treaty.get("country2Alpha3Code", ""),
            },
        ],
        "temporalCoverage": str(treaty.get("year", datetime.now().year)),
         "inLanguage": {
        "@type": "Language",
        "name": "English",
        "alternateName": "en",
        },
         "about": {
        "@type": "Thing",
        "name": "Double Taxation Avoidance", 
        "description": "International tax treaty to prevent double taxation", 
     },
        "publisher": {
        "@type": "Organization",
        "name": CONFIG["SITE_NAME"],
        "url": CONFIG["SITE_URL"], 
        "logo": {
            "@type": "ImageObject",
            "url": f"{CONFIG['SITE_URL']}{CONFIG['DEFAULT_OG_IMAGE']}",
            "width": 180,
            "height": 60,
        },
        "alternateName": CONFIG.get("SITE_SHORT_NAME", "GTL"),
    },
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": canonical,
    },   

    "mentions": [
        {
            "@type": "Country",
            "name": country1Slug,
        },
        {
            "@type": "Country",
            "name": country2Name,
        },
        ],
         "keywords": treaty.get("metaKeywords") or f"{country1Slug}, {country2Name}, DTAA, tax treaty, double taxation",
        "identifier": {
            "@type": "PropertyValue",
            "name": "Tax Treaty Code",
            "value": treaty.get("slug", f"{treaty.get('country1Slug')}-{treaty.get('country2Alpha3Code').lower()}-dtaa"),
        },
        **({"translationOfWork": {
            "@type": "CreativeWork",
            "name": f"Original {country1Slug} - {country2Name} Tax Treaty",
            "inLanguage": "Original Language",
        }} if not treaty.get("isOfficial", True) else {}),
         "isPartOf": {
            "@type": "Collection",
            "name": f"{country1Slug} - {country2Name} Double Taxation Agreements",
            "description": f"Collection of bilateral tax treaties signed by {country1Slug} and {country2Name}",
        },
        }

    # Additional content for treaties
    additional_content = f"""
    <div class="treaty-benefits">
        <h3>About This Tax Treaty</h3>
        <p>This Double Taxation Avoidance Agreement between <strong>UAE</strong> and <strong>{escape_html(country2Name)}</strong> provides:</p>
        <ul>
            <li>Elimination of double taxation on income and capital</li>
            <li>Prevention of tax evasion and avoidance</li>
            <li>Clear residence rules for tax purposes</li>
            <li>Reduced withholding taxes on cross-border payments</li>
        </ul>
    </div>"""

    # Extract body content only
    treaty_content = clean_content(treaty.get("content", "")) + additional_content
    treaty_content = extract_body_content(treaty_content)

    # Generate internal navigation
    internal_nav = ""
    related_content = ""
    if all_treaties:
        internal_nav = generate_internal_links(
            {"slug": treaty_slug, "title": f"{country1Slug}-{country2Name} Treaty"},
            all_treaties,
            "tax-treaties",
        )

    # Generate related content from relatedDocs field only
    if treaty.get("relatedDocs") and all_laws_data:
        related_content = generate_related_docs_html(
            treaty.get("relatedDocs"), all_laws_data
        )

    return (
        generate_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=treaty_content,
            structured_data=structured_data,
            document_type="tax-treaties",
            item=treaty,
            internal_nav=internal_nav,
            related_content=related_content,
            meta_keywords=meta_keywords,
        ),
        treaty_slug,
    )


def generate_blog_html(
    blog: Dict[str, Any], all_blogs: List[Dict[str, Any]] = None
) -> tuple[str, str]:
    """Generate HTML for blog posts"""
    blog_slug = generate_blog_slug(blog.get("title", ""))
    canonical = f"{CONFIG['SITE_URL']}/blogs/{blog_slug}"

    title = f"{escape_html(blog.get('title', ''))} | {CONFIG['SITE_NAME']}"
    # Use metaDescription and metaKeywords from JSON
    description = blog.get("metaDescription", "") or escape_html(
        blog.get("description", "")
    )
    meta_keywords = blog.get("metaKeywords", "")

    # Parse published date
    published_date = blog.get("publishedDate", "")
    try:
        if published_date:
            from datetime import datetime

            parsed_date = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
            formatted_date = parsed_date.strftime("%B %d, %Y")
            iso_date = parsed_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            formatted_date = "Recently"
            iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except:
        formatted_date = "Recently"
        iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Document metadata
    doc_meta = f"""
    <div class="document-meta">
        <strong>Document Type:</strong> Blog Post<br>
        <strong>Author:</strong> {escape_html(blog.get('author', 'Team GTL'))}<br>
        <strong>Published:</strong> {formatted_date}<br>
        <strong>Category:</strong> {escape_html(blog.get('category', 'Tax Insights'))}<br>
        {f"<strong>Reading Time:</strong> {estimate_reading_time(blog.get('content', ''))} min read<br>" if blog.get('content') else ''}
        <strong>Status:</strong> {'Published' if blog.get('published', False) else 'Draft'}
       <br><strong>Last updated at:</strong> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
    </div>"""

    # Breadcrumbs
    breadcrumb_html = f"""
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            <a href="/">Home</a> &rsaquo; <a href="{CONFIG['PUBLIC_PATH']}/blogs">Blog</a> &rsaquo; <strong>{escape_html(blog.get('title', ''))}</strong>
        </div>
    </nav>"""

    # Structured data for blog post
    structured_data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "@id": canonical,
        "headline": escape_json(blog.get("title", "")),
        "description": escape_json(description),
        "articleBody": escape_json(blog.get("content", "")),
        "url": canonical,
         "image": {
        "@type": "ImageObject",
        "url": blog.get(
            "imageUrl", f"{CONFIG['SITE_URL']}/web-app-manifest-512x512.png"
        ),
        "width": 1200,
        "height": 630,
        },
        "datePublished": iso_date,
        "dateModified": blog.get("modifiedDate", iso_date),
        "author": {
            "@type": "Person",  # CHANGED from Organization
            "name": escape_json(blog.get("author", "Team GTL")),
            # REMOVE url property
        },
        "publisher": {
            "@type": "Organization",
            "name": CONFIG["SITE_NAME"],
            "logo": {
                "@type": "ImageObject",
                "url": f"{CONFIG['SITE_URL']}/web-app-manifest-512x512.png",
                "width": 180,
                "height": 60,
            },
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical},
        "about": {  # ADD THIS
            "@type": "Thing",
            "name": escape_json(blog.get("category", "Tax Insights")),
            "description": escape_json(description),
        },
        "articleSection": escape_json(blog.get("category", "Tax Insights")),
        "keywords": generate_blog_keywords(blog),
        "inLanguage": "en",
        "wordCount": len(blog.get("content", "").split()) if blog.get("content") else 0,
        "timeRequired": f"PT{max(1, len(blog.get('content', '').split()) // 225)}M",
    }

    # Add image to structured data if available
    if blog.get("imageUrl"):
        structured_data["image"] = {
            "@type": "ImageObject",
            "url": blog["imageUrl"],
            "width": 1200,
            "height": 630,
        }

    # Extract body content only
    blog_content = clean_content(blog.get("content", ""))
    blog_content = extract_body_content(blog_content)

    # Generate internal navigation
    internal_nav = ""
    related_content = ""
    if all_blogs:
        internal_nav = generate_internal_links(
            {"slug": blog_slug, "title": blog.get("title", "")}, all_blogs, "blogs"
        )

    # Generate blog-specific HTML with proper OG tags
    return (
        generate_blog_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=blog_content,
            structured_data=structured_data,
            blog=blog,
            formatted_date=formatted_date,
            internal_nav=internal_nav,
            related_content=related_content,
            meta_keywords=meta_keywords,
        ),
        blog_slug,
    )


def generate_blog_keywords(blog: Dict[str, Any]) -> str:
    """Generate SEO keywords for blog posts from JSON data"""
    # Use metaKeywords from JSON if available and not empty
    
    meta_keywords = blog.get("metaKeywords", "").strip()
    
    if meta_keywords:
        return meta_keywords    

    return ""


def estimate_reading_time(content: str) -> int:
    """Estimate reading time based on content length"""
    if not content:
        return 1

    # Remove HTML tags and count words
    text_content = re.sub(r"<[^>]*>", "", content)
    word_count = len(text_content.split())

    # Average reading speed is 200-250 words per minute
    return max(1, round(word_count / 225))


def generate_base_html(
    title: str,
    description: str,
    canonical: str,
    doc_meta: str,
    breadcrumb_html: str,
    content: str,
    structured_data: Dict[str, Any],
    document_type: str,
    item: Dict[str, Any],
    internal_nav: str = "",
    related_content: str = "",
    meta_keywords: str = "",
) -> str:
    """Generate base HTML template - delegates to unified HTML generator"""
    return generate_unified_html(
        title=title,
        description=description,
        canonical=canonical,
        doc_meta=doc_meta,
        breadcrumb_html=breadcrumb_html,
        content=content,
        structured_data=structured_data,
        document_type=document_type,
        item=item,
        internal_nav=internal_nav,
        related_content=related_content,
        meta_keywords=meta_keywords,
    )


def generate_base_html_OLD_VERSION_DO_NOT_USE(
    title: str,
    description: str,
    canonical: str,
    doc_meta: str,
    breadcrumb_html: str,
    content: str,
    structured_data: Dict[str, Any],
    document_type: str,
    item: Dict[str, Any],
    internal_nav: str = "",
    related_content: str = "",
    meta_keywords: str = "",
) -> str:
    """OLD VERSION - Generate base HTML template"""

    # Use provided meta_keywords or generate as fallback
    keywords = meta_keywords or generate_keywords(document_type, item)

    # OG Image with alt text - use configured default image
    # og_image = f"{CONFIG['SITE_URL']}/images/{document_type}/default-og.jpg"
    og_image = f"{CONFIG['SITE_URL']}{CONFIG['DEFAULT_OG_IMAGE']}"
    og_image_alt = f"{title} - {CONFIG['SITE_NAME']}"

    # Add document-type specific CSS
    doc_type_css = ""
    if document_type == "articles":
        doc_type_css = "<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/article.css'>"
    elif document_type == "decisions":
        doc_type_css = "<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/decision.css'>"
    elif document_type == "guidances":
        doc_type_css = "<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/guide.css'>"
    elif document_type == "tax-treaties":
        doc_type_css = "<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/dtaa.css'>"
    elif document_type == "blogs":
        doc_type_css = "<link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/blogs.css'>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="index, follow" />
    <meta name="theme-color" content="#232536" />
    
    <!-- SEO Meta Tags -->

    <title>{escape_html(item.get('metaTitle', '') or title)}</title>
    
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="sitemap" type="application/xml" title="Sitemap" href="{CONFIG['SITE_URL']}/sitemap.xml" />
    
    <!-- Document Type Specific CSS -->
    {doc_type_css}
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:title" content="{title}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:image:alt" content="{og_image_alt}" />
    <meta property="og:site_name" content="{CONFIG['SITE_NAME']}" />
        <meta property="fb:app_id" content="123456789012345" />
    <!-- random appid added so that User-agent: facebookexternalhit scrapes the thumbnail img value -->

    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="{canonical}" />
    <meta name="twitter:title" content="{title}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{og_image}" />
    <meta name="twitter:image:alt" content="{og_image_alt}" />
    <meta name="twitter:site" content="{CONFIG['TWITTER_HANDLE']}" />
    
    <!-- Additional SEO -->
    <meta name="author" content="Team GTL" />
    <meta name="geo.region" content="AE" />
    <meta name="geo.placename" content="UAE" />
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>
    
    <!-- Critical CSS -->
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            line-height: 1.6; 
            background: #f8f9fa;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .header {{ background: #232536; color: white; padding: 20px 0; }}
        .header p {{ margin: 0; font-size: 1.5rem; }}
        .header nav a {{ color: #ccc; margin-right: 20px; text-decoration: none; }}
        .header nav a:hover {{ color: white; }}
        .breadcrumb-nav {{ background: #e2eaf2;padding: 10px 0; border-bottom: 1px solid #e9ecef; }}
        .breadcrumb-nav a {{ color: #007bff; text-decoration: none; }}
        .breadcrumb-nav a:hover {{ text-decoration: underline; }}
        .main-content {{ padding: 30px 0; }}
        .document-meta {{ 
            background: #e8f4fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border-left: 4px solid #007bff;
        }}
        .static-content {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            padding: 2rem; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .bot-notice {{
            background: #e3f2fd;
            border: 1px solid #1976d2;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
            color: #1565c0;
            text-align: center;
        }}
        .footer {{ background: #232536; color: white; padding: 20px 0; text-align: center; }}
        .footer a {{ color: #ccc; }}
        .document-actions {{ 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
            text-align: center;
        }}
        .action-btn {{
            margin: 0 10px;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{ background: #4071a3; color: white; }}
        .btn-success {{ background: #28a745; color: white; }}
        .treaty-benefits {{ margin-top: 30px; padding: 20px; background: #e2eaf2;border-radius: 8px; }}
        .treaty-benefits h3 {{ color: #333; margin-bottom: 15px; }}
        .treaty-benefits ul {{ padding-left: 20px; }}
        .treaty-benefits li {{ margin-bottom: 8px; }}
        .internal-navigation {{ 
            display: flex; 
            justify-content: space-between; 
            margin: 30px 0; 
            padding: 20px; 
            background: #e2eaf2;
            border-radius: 8px; 
        }}
        .internal-navigation a {{ 
            padding: 10px 20px; 
            background: #e2eaf2;
            text-decoration: none; 
            border-radius: 4px; 
            transition: background 0.3s; 
        }}
        .internal-navigation a:hover {{ background: #c8d7e6; }}
        .nav-link {{
            color: #007bff;
            text-decoration: none;
            display: flex;
            align-items: center;
        }}
        .prev-link {{
            /* Inherits from .nav-link */
        }}
        .next-link {{
            text-align: right;
        }}
        .related-content {{ 
            margin: 30px 0; 
            padding: 20px; 
            background: #e2eaf2;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .related-content h3 {{ color: #333; margin-bottom: 15px; }}
        .related-content ul {{ list-style: none; padding: 0; }}
        .related-content li {{ margin-bottom: 10px; }}
        .related-content a {{ 
            color: #007bff; 
            text-decoration: none; 
            transition: color 0.3s; 
        }}
        .related-content a:hover {{ color: #0056b3; text-decoration: underline; }}
        .related-link {{
            color: #007bff;
            text-decoration: none;
            display: block;
            padding: 8px 0;
        }}
        .footer-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-bottom: 20px;
        }}
        .footer-copyright {{
            border-top: 1px solid #444;
            padding-top: 20px;
            text-align: center;
        }}
        .excerpt-box {{
            background: #e2eaf2;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #007bff;
        }}
        .excerpt-text {{
            margin-bottom: 0;
            font-style: italic;
            line-height: 1.6;
        }}
        .treaty-benefits {{
            margin-top: 30px;
            padding: 20px;
            background: #e2eaf2;
            border-radius: 8px;
        }}
        .index-container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }}
        .index-header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: #e2eaf2;
            border-radius: 8px;
        }}
        .index-header h1 {{
            color: #232536;
            margin-bottom: 10px;
        }}
        .index-header p {{
            color: #666;
        }}
        .section-title {{
            color: #232536;
            border-bottom: 3px solid;
            padding-bottom: 10px;
            display: flex;
            align-items: center;
        }}
        .section-count {{
            font-size: 14px;
            margin-left: 15px;
            color: #666;
            font-weight: normal;
        }}
        .section-box {{
            background: #e2eaf2;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .subsection-title {{
            color: #232536;
            border-left: 4px solid;
            padding-left: 15px;
            margin-bottom: 15px;
        }}
        .document-item {{
            border-left: 4px solid #007bff;
            padding: 15px;
            background: white;
            border-radius: 0 8px 8px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        .document-item a {{
            text-decoration: none;
            color: #007bff;
            font-size: 16px;
        }}
        .document-item a:hover {{
            text-decoration: underline;
        }}
        .document-description {{
            margin: 8px 0;
            color: #666;
            font-size: 14px;
        }}
        .document-preview {{
            margin: 8px 0 0 0;
            color: #555;
            font-size: 13px;
            line-height: 1.5;
        }}
        .law-section {{
            margin-bottom: 30px;
        }}
        .law-section h3 {{
            color: #232536;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #007bff;
            font-size: 14px;
            line-height: 1.4;
        }}           
        .gtl-summary {{
            color: #43af76;
        }}  
    </style>
</head>
<body>
    <!-- This will be hydrated by React for human users -->
    <div id="root">
        <header class="header">
            <div class="container">
                <p>{CONFIG['SITE_NAME']}</p>
                <nav>
                    <a href="/">Home</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/articles">Articles</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/decisions">Decisions</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/guidances">Guidance</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/tax-treaties">Treaties</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/blogs">Blog</a>                    
                </nav>
            </div>
        </header>
        
        {breadcrumb_html}
        
        <main class="main-content">
            <div class="container">                     
                <div class="static-content">
                    {"" if item.get('slug') == 'index' else '''<section class="document-meta">                          
                           <p class='gtl-summary'><b>GTL Summary: </b></p>                 
                          <p id="summary">''' + escape_html(item.get('summary', '')) + '''</p>
                    </section>'''}
                    {doc_meta}
                    
                    <article>
                    
                        
                        <section class="document-content">
                            {content}
                        </section>
                        
                        {internal_nav}
                        {related_content}
                    </article>
                    
                    <div class="document-actions">
                        <button onclick="window.print()" class="action-btn btn-primary">
                            🖨️ Print
                        </button>
                        <button onclick="navigator.share ? navigator.share({{title: document.title, url: window.location.href}}) : alert('URL: ' + window.location.href)"
                                class="action-btn btn-success">
                            📤 Share
                        </button>
                    </div>
            <div class="bot-notice">
                    <strong>Fast-loading version for search engines</strong> - 
                    <a href="{canonical}" style="color: #1565c0;">Click here for the interactive version</a>
                </div>
                </div>
            </div>
        </main>
        
        <footer class="footer">
            <div class="container">
            
                <div class="footer-grid">
                    <div>
                        <h3 style="margin-bottom: 10px;">About {CONFIG['SITE_NAME']}</h3>
                        <p style="font-size: 14px; line-height: 1.6;">Searchable GCC tax database: UAE VAT & Corporate Tax (CIT) Saudi/KSA VAT customs duty excise transfer pricing and tax treaties (DTAA). Kuwait Oman Qatar Bahrain.</p>
                    </div>
                    <div>
                        <h3 style="margin-bottom: 10px;">Get In Touch</h3>
                        <p style="font-size: 14px; margin-bottom: 8px;">Have questions or suggestions?</p>
                        <p style="font-size: 14px;"><strong>📧 Email:</strong> <a href="mailto:support@gcctaxlaws.com" style="color: #ccc;">support@gcctaxlaws.com</a></p>
                    </div>
                </div>
                <div class="footer-copyright">
                    <p>&copy; {datetime.now().year} {CONFIG['SITE_NAME']}. All rights reserved.</p>
                    <p><a href="{CONFIG['SITE_URL']}">Visit our main website</a></p>
                </div>
            </div>
        </footer>
    </div>
    
    <!-- Data for React hydration -->
    <script>
        window.__STATIC_PAGE_DATA__ = {json.dumps({
            'type': document_type,
            'slug': item.get('slug', ''),
            'url': f"/{document_type}/{item.get('slug', '')}",
            'title': item.get('title', ''),
            'id': item.get('_id', {}).get('$oid', '') if isinstance(item.get('_id'), dict) else item.get('_id', '')
        })};
    </script>
</body>
</html>"""


def generate_keywords(document_type: str, item: Dict[str, Any]) -> str:
    """Generate SEO keywords based on document type and content"""
    keywords = ["UAE tax laws", "tax compliance", "legal document"]

    if document_type == "articles":
        keywords.extend(["tax legislation", "UAE tax law", "tax article"])
        if item.get("number"):
            keywords.append(f"article {item['number']}")

    elif document_type == "decisions":
        keywords.extend(
            ["FTA decision", "tax decision", "regulatory decision", "cabinet decision"]
        )
        if item.get("number"):
            keywords.append(f"decision {item['number']}")
        if item.get("year"):
            keywords.append(f"{item['year']} decision")
        if item.get("type"):
            keywords.append(item["type"].lower())

    elif document_type == "guidances":
        keywords.extend(["tax guidance", "FTA guide", "compliance guide"])
        if item.get("uniqueCode"):
            keywords.append(item["uniqueCode"])
        if item.get("type"):
            keywords.append(item["type"].lower())

    elif document_type == "tax-treaties":
        keywords.extend(["tax treaty", "DTAA", "double taxation"])
        if item.get("country2Name"):
            keywords.append(f"{item['country2Name'].lower()} treaty")

    return ", ".join(keywords)


def ensure_dir(directory: str) -> None:
    """Ensure directory exists"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON file safely"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return []


def generate_blog_base_html(
    title: str,
    description: str,
    canonical: str,
    doc_meta: str,
    breadcrumb_html: str,
    content: str,
    structured_data: Dict[str, Any],
    blog: Dict[str, Any],
    formatted_date: str,
    internal_nav: str = "",
    related_content: str = "",
    meta_keywords: str = "",
) -> str:
    """Generate base HTML template for blog posts - delegates to unified HTML generator"""
    
    # Blog-specific additional meta tags
    additional_meta = f"""
    <meta property="article:author" content="{escape_html(blog.get('author', 'Team GTL'))}" />
    <meta property="article:published_time" content="{blog.get('publishedDate', '')}" />
    <meta property="article:section" content="{escape_html(blog.get('category', 'Tax Insights'))}" />
    
    <!-- LinkedIn specific -->
    <meta property="linkedin:owner" content="{CONFIG['TWITTER_HANDLE']}" />"""
    
    # Blog-specific CSS
    additional_styles = """
        .blog-header {
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }
        .blog-title {
            font-size: 2.5rem;
            font-weight: bold;
            color: #232536;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        .blog-subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 1rem;
            font-style: italic;
        }
        .blog-meta {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            color: #666;
            font-size: 0.9rem;
        }
        .blog-image {
            width: 100%;
            max-width: 600px;
            height: auto;
            margin: 2rem auto;
            display: block;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }"""
    
    return generate_unified_html(
        title=title,
        description=description,
        canonical=canonical,
        doc_meta=doc_meta,
        breadcrumb_html=breadcrumb_html,
        content=content,
        structured_data=structured_data,
        document_type="blogs",
        item=blog,
        internal_nav=internal_nav,
        related_content=related_content,
        meta_keywords=meta_keywords,
        additional_meta=additional_meta,
        additional_styles=additional_styles,
    )


def generate_blog_base_html_OLD_VERSION_DO_NOT_USE(
    title: str,
    description: str,
    canonical: str,
    doc_meta: str,
    breadcrumb_html: str,
    content: str,
    structured_data: Dict[str, Any],
    blog: Dict[str, Any],
    formatted_date: str,
    internal_nav: str = "",
    related_content: str = "",
    meta_keywords: str = "",
) -> str:
    """OLD VERSION - Generate base HTML template for blog posts"""

    # Use blog image or configured default
    og_image = blog.get("imageUrl", f"{CONFIG['SITE_URL']}{CONFIG['DEFAULT_OG_IMAGE']}")
    og_image_alt = f"{blog.get('title', '')} - {CONFIG['SITE_NAME']}"

    # Use provided meta_keywords or generate as fallback
    keywords = meta_keywords or generate_blog_keywords(blog)

    # Extract excerpt or create from description
    excerpt = blog.get("excerpt", description)
    if len(excerpt) > 300:
        excerpt = excerpt[:297] + "..."

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="robots" content="index, follow" />
    <meta name="theme-color" content="#232536" />
    
    <!-- SEO Meta Tags -->
    <title>{title}</title>    
    
    <meta name="description" content="{description}" />
    <meta name="keywords" content="{keywords}" />
    <link rel="canonical" href="{canonical}" />
    <link rel="sitemap" type="application/xml" title="Sitemap" href="{CONFIG['SITE_URL']}/sitemap.xml" />
    
    <!-- Blog Specific CSS -->
    <link rel='stylesheet' href='https://gtlcdn-eufeh8ffbvbvacgf.z03.azurefd.net/guide/stylesheets/prod/blogs.css'>
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{canonical}" />
    <meta property="og:title" content="{escape_html(blog.get('title', ''))}" />
    <meta property="og:description" content="{description}" />
    <meta property="og:image" content="{og_image}" />
    <meta property="og:image:alt" content="{og_image_alt}" />
    <meta property="fb:app_id" content="123456789012345" />
    <!-- random appid added so that User-agent: facebookexternalhit scrapes the thumbnail img value -->

    <meta property="og:site_name" content="{CONFIG['SITE_NAME']}" />
    <meta property="article:author" content="{escape_html(blog.get('author', 'Team GTL'))}" />
    <meta property="article:published_time" content="{blog.get('publishedDate', '')}" />
    <meta property="article:section" content="{escape_html(blog.get('category', 'Tax Insights'))}" />
    
    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:url" content="{canonical}" />
    <meta name="twitter:title" content="{escape_html(blog.get('title', ''))}" />
    <meta name="twitter:description" content="{description}" />
    <meta name="twitter:image" content="{og_image}" />
    <meta name="twitter:image:alt" content="{og_image_alt}" />
    <meta name="twitter:site" content="{CONFIG['TWITTER_HANDLE']}" />
    
    <!-- LinkedIn specific -->
    <meta property="linkedin:owner" content="{CONFIG['TWITTER_HANDLE']}" />
    
    <!-- Additional SEO -->
    <meta name="author" content="{escape_html(blog.get('author', 'Team GTL'))}" />
    <meta name="geo.region" content="AE" />
    <meta name="geo.placename" content="UAE" />
    
    <!-- Structured Data -->
    <script type="application/ld+json">
    {json.dumps(structured_data, indent=2)}
    </script>
    
    <!-- Critical CSS for Blog -->
    <style>
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            line-height: 1.6; 
            background: #f8f9fa;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .header {{ background: #232536; color: white; padding: 20px 0; }}
        .header p {{ margin: 0; font-size: 1.5rem; }}
        .header nav a {{ color: #ccc; margin-right: 20px; text-decoration: none; }}
        .header nav a:hover {{ color: white; }}
        .breadcrumb-nav {{ background: #e2eaf2;padding: 10px 0; border-bottom: 1px solid #e9ecef; }}
        .breadcrumb-nav a {{ color: #007bff; text-decoration: none; }}
        .breadcrumb-nav a:hover {{ text-decoration: underline; }}
        .main-content {{ padding: 30px 0; }}
        .document-meta {{ 
            background: #e8f4fd; 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            border-left: 4px solid #007bff;
        }}
        .blog-content {{ 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 2rem; 
            border-radius: 8px; 
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .blog-header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }}
        .blog-title {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #232536;
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }}
        .blog-subtitle {{
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 1rem;
            font-style: italic;
        }}
        .blog-meta {{
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
            color: #666;
            font-size: 0.9rem;
        }}
        .blog-image {{
            width: 100%;
            max-width: 600px;
            height: auto;
            margin: 2rem auto;
            display: block;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .bot-notice {{
            background: #e3f2fd;
            border: 1px solid #1976d2;
            padding: 12px;
            margin: 20px 0;
            border-radius: 4px;
            color: #1565c0;
            text-align: center;
        }}
        .footer {{ background: #232536; color: white; padding: 20px 0; text-align: center; }}
        .footer a {{ color: #ccc; }}
        .internal-navigation {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 30px 0;
            padding: 20px 0;
            border-top: 1px solid #e9ecef;
            border-bottom: 1px solid #e9ecef;
        }}
        .internal-navigation a {{
            color: #007bff;
            text-decoration: none;
            display: flex;
            align-items: center;
            padding: 15px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            transition: all 0.2s;
            min-height: 80px;
        }}
        .internal-navigation a:hover {{ 
            background: #e9ecef;
            border-color: #007bff;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .nav-link-content {{
            flex: 1;
            min-width: 0;
        }}
        .nav-link-label {{
            font-size: 12px;
            color: #666;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .nav-link-title {{
            font-weight: 500;
            color: #232536;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            line-height: 1.4;
        }}
        .prev-link {{
            justify-content: flex-start;
        }}
        .next-link {{
            justify-content: flex-end;
            text-align: right;
        }}
        @media (max-width: 768px) {{
            .internal-navigation {{
                grid-template-columns: 1fr;
                gap: 10px;
            }}
        }}
        .related-link {{
            color: #007bff;
            text-decoration: none;
            display: block;
            padding: 8px 0;
        }}
        .footer-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin-bottom: 20px;
        }}
        .footer-copyright {{
            border-top: 1px solid #444;
            padding-top: 20px;
            text-align: center;
        }}
        .excerpt-box {{
            background: #e2eaf2;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #007bff;
        }}
        .excerpt-text {{
            margin-bottom: 0;
            font-style: italic;
            line-height: 1.6;
        }}
        .social-share {{ 
            margin-top: 30px; 
            padding-top: 20px; 
            border-top: 1px solid #eee; 
            text-align: center;
        }}
        .share-btn {{
            margin: 0 5px;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 0.9rem;
        }}
        .btn-linkedin {{ background: #0077b5; color: white; }}
        .btn-twitter {{ background: #1da1f2; color: white; }}
        .btn-facebook {{ background: #4267B2; color: white; }}
        .btn-print {{ background: #6c757d; color: white; }}
    </style>
</head>
<body>
    <div id="root">
        <header class="header">
            <div class="container">
                <p>{CONFIG['SITE_NAME']}</p>
                <nav>
                <a href="/">Home</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/articles">Articles</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/decisions">Decisions</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/guidances">Guidance</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/tax-treaties">Treaties</a>
                    <a href="{CONFIG['PUBLIC_PATH']}/blogs">Blog</a>
                </nav>
            </div>
        </header>
        
        {breadcrumb_html}
        
        <main class="main-content">
            <div class="container">               
                
                <article class="blog-content">
                    <header class="blog-header">
                        <h1 class="blog-title">{escape_html(blog.get('title', ''))}</h1>
                        {f'<p class="blog-subtitle">{escape_html(blog.get("subtitle", ""))}</p>' if blog.get('subtitle') else ''}
                        
                        <div class="blog-meta">
                        <span>📅 {formatted_date}</span>
                            <span>👤 {escape_html(blog.get('author', 'Team GTL'))}</span>
                            <span>📂 {escape_html(blog.get('category', 'Tax Insights'))}</span>
                            {f'<span>⏱️ {estimate_reading_time(blog.get("content", ""))} min read</span>' if blog.get('content') else ''}
                        </div>
                    </header>                   
                    
    
                    {doc_meta}
                    
                    {f'<img src="{blog["imageUrl"]}" alt="{escape_html(blog.get("title", ""))}" class="blog-image" />' if blog.get('imageUrl') else ''}
                    
                    <div class="excerpt-box">
                        <h3 style="margin-top: 0; color: #232536;">Excerpt</h3>
                        <p class="excerpt-text">{escape_html(excerpt)}</p>
                    </div>
                    
                    <div class="blog-body">
                        {content}
                    </div>
                    
                    {internal_nav}
                    {related_content}
                    
                    <div class="social-share">
                        <h4>Share this article:</h4>
                        <a href="https://www.linkedin.com/sharing/share-offsite/?url={canonical}" target="_blank" class="share-btn btn-linkedin">
                            LinkedIn
                        </a>
                        <a href="https://twitter.com/intent/tweet?url={canonical}&text={escape_html(blog.get('title', ''))}" target="_blank" class="share-btn btn-twitter">
                            Twitter
                        </a>
                        <a href="https://www.facebook.com/sharer/sharer.php?u={canonical}" target="_blank" class="share-btn btn-facebook">
                            Facebook
                        </a>
                        <button onclick="window.print()" class="share-btn btn-print">
                            Print
                        </button>
                    </div>
            <div class="bot-notice">
                    <strong>Fast-loading version for search engines</strong> - 
                    <a href="{canonical}" style="color: #1565c0;">Click here for the interactive version</a>
                </div>
                </article>
            </div>
        </main>
        
        <footer class="footer">
            <div class="container">
            
                <div class="footer-grid">
                    <div>
                        <h3 style="margin-bottom: 10px;">About {CONFIG['SITE_NAME']}</h3>
                        <p style="font-size: 14px; line-height: 1.6;">Searchable GCC tax database: UAE VAT & Corporate Tax (CIT) Saudi/KSA VAT customs duty excise transfer pricing and tax treaties (DTAA). Kuwait Oman Qatar Bahrain.</p>
                    </div>
                    <div>
                        <h3 style="margin-bottom: 10px;">Get In Touch</h3>
                        <p style="font-size: 14px; margin-bottom: 8px;">Have questions or suggestions?</p>
                        <p style="font-size: 14px;"><strong> Email:</strong> <a href="mailto:support@gcctaxlaws.com" style="color: #ccc;">support@gcctaxlaws.com</a></p>
                    </div>
                </div>
                <div class="footer-copyright">
                    <p>&copy; {datetime.now().year} {CONFIG['SITE_NAME']}. All rights reserved.</p>
                    <p><a href="{CONFIG['SITE_URL']}">Visit our main website</a></p>
                </div>
            </div>
        </footer>
    </div>
    
    <!-- Data for React hydration -->
    <script>
        window.__STATIC_PAGE_DATA__ = {json.dumps({
            'type': 'blogs',
            'slug': generate_blog_slug(blog.get('title', '')),
            'url': f"{CONFIG['PUBLIC_PATH']}/blogs/{generate_blog_slug(blog.get('title', ''))}",
            'title': blog.get('title', ''),
            'canonical': canonical
        })};
    </script>
</body>
</html>"""


def process_laws_with_articles_and_decisions() -> Dict[str, Dict]:
    """Process laws and group their articles and decisions together"""
    laws_data = {}
    print(f"\n📄 Processing {len(law_files)} law files for articles and decisions...")

    for filename in law_files:
        print(f"\n🔍 Processing file: {filename}")
        file_path = Path(CONFIG["DATA_DIR"]) / filename

        data = load_json_file(str(file_path))
        if not data:
            print(f"⚠️ No data loaded from {filename}")
            continue

        # Handle both list and dict structures
        if isinstance(data, dict):
            data = [data]

        for i, country_data in enumerate(data):
            print(f"  📍 Processing country data {i+1}/{len(data)}")
            country_name = country_data.get("countryName", "UAE")
            country_info = {
                "countryName": country_name,
                "alpha3Code": country_data.get("alpha3Code", ""),
                "flagCode": country_data.get("flagCode", ""),
                "phoneCode": country_data.get("phoneCode", ""),
            }
            print(f"    🏳️ Country: {country_name}")

            laws = country_data.get("laws", [])
            print(f"    📚 Found {len(laws)} laws")

            for j, law in enumerate(laws):
                law_name = law.get("lawFullName", "Tax Law")
                law_short = law.get("lawShortName", "")
                print(f"      📖 Law {j+1}: {law_name}")

                # Create unique key for this law
                law_key = f"{country_name}-{law_short}"

                if law_key not in laws_data:
                    laws_data[law_key] = {
                        "law_info": {
                            "lawFullName": law_name,
                            "lawShortName": law_short,
                        },
                        "country_info": country_info,
                        "articles": [],
                        "decisions": [],
                    }

                # Process articles
                law_articles = law.get("articles", [])
                print(f"        📄 Found {len(law_articles)} articles")

                for k, article in enumerate(law_articles):
                    article_number = article.get("number", "")
                    if article_number and article.get("title"):
                        article_slug = generate_article_slug(
                            law_short, article_number, country_name
                        )

                        # Clean title from HTML tags but keep full content
                        clean_title = re.sub(r"<[^>]*>", "", article.get("title", ""))

                        # Get full description without truncation
                        description = ""
                        if article.get("metaDescription"):
                            description = article["metaDescription"]
                        else:
                            description = article["textOnly"]
                        # elif article.get("content"):
                        #     # Remove HTML and get text
                        #     clean_content = re.sub(r"<[^>]*>", "", article["content"])
                        #     description = clean_content

                        # Build path string from article path
                        path_parts = []
                        if article.get("path"):
                            for path_item in article["path"]:
                                path_parts.append(path_item.get("name", ""))
                        path_string = " › ".join(path_parts) if path_parts else ""

                        article_data = {
                            "title": clean_title,
                            "url": f"{CONFIG['PUBLIC_PATH']}/articles/{article_slug}",
                            "slug": article_slug,
                            "description": description,
                            "textOnly": article.get("textOnly", ""),
                            "number": article_number,
                            "orderIndex": article.get("orderIndex", 0),
                            "path": path_string,
                            "type": "Legislation",
                        }
                        laws_data[law_key]["articles"].append(article_data)

                # Process decisions
                law_decisions = law.get("decisions", [])
                print(f"        ⚖️ Found {len(law_decisions)} decisions")

                for decision in law_decisions:
                    decision_number = decision.get("number", "")
                    decision_year = decision.get("year", "")
                    decision_type = decision.get("type", "")

                    if decision_number or decision.get("title") or decision.get("year"):
                        decision_slug = generate_decision_slug(
                            law_short,
                            decision_number,
                            decision_year,
                            decision_type,
                            country_name,
                        )

                        # Clean title from HTML tags but keep full content
                        clean_title = re.sub(r"<[^>]*>", "", decision.get("title", ""))

                        # Get full description without truncation
                        description = ""
                        if decision.get("metaDescription"):
                            description = decision["metaDescription"]
                        elif decision.get("textOnly"):
                            description = decision["textOnly"]

                        decision_data = {
                            "title": clean_title,
                            "url": f"{CONFIG['PUBLIC_PATH']}/decisions/{decision_slug}",
                            "slug": decision_slug,
                            "description": description,
                            "textOnly": decision.get("textOnly", ""),
                            "number": decision_number,
                            "year": decision_year,
                            "type": decision_type,
                            "name": decision.get("name", ""),
                            
                        }
                        laws_data[law_key]["decisions"].append(decision_data)

    # Sort articles by orderIndex and decisions by year/number
    for law_key in laws_data:
        laws_data[law_key]["articles"].sort(
            key=lambda x: (x.get("orderIndex", 0), x.get("number", ""))
        )
        laws_data[law_key]["decisions"].sort(
            key=lambda x: (x.get("year", ""), x.get("number", "")), reverse=True
        )

    total_articles = sum(len(law_data["articles"]) for law_data in laws_data.values())
    total_decisions = sum(len(law_data["decisions"]) for law_data in laws_data.values())
    print(f"📊 Total articles found: {total_articles}")
    print(f"📊 Total decisions found: {total_decisions}")

    return laws_data


def generate_guidance_links() -> List[Dict]:
    """Generate guidance links from guidance files"""
    guidances = []
    print(f"\n📋 Processing {len(guidance_files)} guidance files...")

    for filename in guidance_files:
        print(f"\n🔍 Processing guidance file: {filename}")
        file_path = Path(CONFIG["DATA_DIR"]) / filename

        data = load_json_file(str(file_path))
        if not data:
            continue

        print(f"    📋 Found {len(data)} guidance items")

        for i, guidance in enumerate(data):
            # Generate slug for each guidance
            unique_code = guidance.get("uniqueCode", "")
            guidance_type = guidance.get("type", "")
            law_slug = guidance.get("lawSlug", "")

            if unique_code and guidance.get("title"):
                guidance_slug = generate_guidance_slug(
                    law_slug, guidance_type, unique_code
                )

                # Clean title from HTML tags but keep full content
                clean_title = re.sub(r"<[^>]*>", "", guidance.get("title", ""))

                # Get full description without truncation
                description = ""
                if guidance.get("metaDescription"):
                    description = guidance["metaDescription"]
                elif guidance.get("textOnly"):
                    description = guidance["textOnly"]
                    
                guidances.append(
                    {
                        "title": clean_title,
                        "url": f"{CONFIG['PUBLIC_PATH']}/guidances/{guidance_slug}",
                        "slug": guidance_slug,
                        "description": description,
                        "textOnly": guidance.get("textOnly", ""),
                        "unique_code": unique_code,
                        "type": guidance_type,
                        "year": guidance.get("year", ""),
                        "law_slug": law_slug,
                    }
                )

    # Second, process guidelines embedded in law files
    print(f"\n📋 Processing {len(law_files)} law files for embedded guidelines...")
    for filename in law_files:
        print(f"\n🔍 Processing law file: {filename}")
        file_path = Path(CONFIG["DATA_DIR"]) / filename

        if not file_path.exists():
            print(f"Warning: Could not load {file_path}")
            print(f"⚠️ No data loaded from {filename}\n")
            continue

        data = load_json_file(str(file_path))
        if not data:
            print(f"⚠️ No data loaded from {filename}\n")
            continue

        # Handle both single objects and lists
        if isinstance(data, dict):
            data = [data]

        for country_data in data:
            country_name = country_data.get("countryName", "")
            for law in country_data.get("laws", []):
                law_short = law.get("lawShortName", "")
                law_guidelines = law.get("guidelines", [])

                if law_guidelines:
                    print(
                        f"    📋 Found {len(law_guidelines)} guidelines in {law.get('lawFullName', 'law')}"
                    )

                for guideline in law_guidelines:
                    unique_code = guideline.get("uniqueCode", "")
                    guidance_type = guideline.get("type", "")

                    if unique_code and guideline.get("title"):
                        # Format: countryName-lawShortName-type-uniqueCode
                        country_prefix = country_name.lower().replace(" ", "-")
                        law_slug = f"{country_prefix}-{law_short}"
                        guidance_slug = generate_guidance_slug(
                            law_slug, guidance_type, unique_code
                        )

                        # Clean title from HTML tags but keep full content
                        clean_title = re.sub(r"<[^>]*>", "", guideline.get("title", ""))
                                   
                        guidances.append(
                            {
                                "title": clean_title,
                                "url": f"{CONFIG['PUBLIC_PATH']}/guidances/{guidance_slug}",
                                "slug": guidance_slug,
                                "description": description,
                                "unique_code": unique_code,
                                "type": guidance_type,
                                "year": guideline.get("year", ""),
                                "law_slug": f"{country_prefix}-{law_short}",
                            }
                        )

    # Sort guidances by law_slug and then by unique_code
    guidances.sort(key=lambda x: (x.get("law_slug", ""), x.get("unique_code", "")))
    print(f"📊 Total guidances found: {len(guidances)}")
    return guidances


def generate_treaty_links() -> List[Dict]:
    """Generate treaty links from treaty files"""
    treaties = []
    print(f"\n🤝 Processing {len(treaty_files)} treaty files...")

    for filename in treaty_files:
        print(f"\n🔍 Processing treaty file: {filename}")
        file_path = Path(CONFIG["DATA_DIR"]) / filename

        data = load_json_file(str(file_path))
        if not data:
            continue

        print(f"    🤝 Found {len(data)} treaty items")

        for i, treaty in enumerate(data):
            # Generate slug for each treaty
            country1_slug = treaty.get("country1Slug", "uae")
            country2_alpha3 = treaty.get("country2Alpha3Code", "")

            if country2_alpha3 and treaty.get("title"):
                treaty_slug = generate_treaty_slug(country1_slug, country2_alpha3)

                # Clean title from HTML tags but keep full content
                clean_title = re.sub(r"<[^>]*>", "", treaty.get("title", ""))
                country2Name = treaty.get("country2Name", "")
                country1Slug = treaty.get("country1Slug", "").capitalize()

                # Get full description without truncation
                description = treaty.get(
                    "metaDescription",
                    f"Double Taxation Avoidance Agreement between {country1Slug} and {country2Name}.",
                )
                
                # print(f"    ➡️➡️ Desc Treaty:➡️➡️ {description}")
                
                if treaty.get("officialTranslation") is False:
                    description += " Unofficial translation."

                treaties.append(
                    {
                        "title": clean_title,
                        "url": f"{CONFIG['PUBLIC_PATH']}/tax-treaties/{treaty_slug}",
                        "slug": treaty_slug,
                        "description": description,
                        "country2Name": country2Name,
                        "country1Slug": country1Slug,
                        "official_translation": treaty.get("officialTranslation", True),
                        "country2_alpha3": country2_alpha3,
                        "flag_code": treaty.get("flagCode", ""),
                        "year": treaty.get("year", ""),
                        "issue_date": treaty.get("issueDate", ""),
                    }
                )

    # Sort treaties by country name
    treaties.sort(key=lambda x: x.get("country1Slug", ""))
    print(f"📊 Total treaties found: {len(treaties)}")
    return treaties


def process_blogs() -> None:
    """Process blog documents"""
    blogs_dir = Path(CONFIG["OUTPUT_DIR"]) / "blogs"
    ensure_dir(str(blogs_dir))

    for filename in blog_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if not file_path.exists():
            print(f"Skipping {filename} - file not found")
            continue

        print(f"Processing {filename}...")
        blogs = load_json_file(str(file_path))

        # Collect all published blogs for internal linking
        blogs_data = []
        for blog in blogs:
            if blog.get("published", False) and blog.get("title"):
                blog_slug = generate_blog_slug(blog.get("title", ""))
                blogs_data.append(
                    {
                        "slug": blog_slug,
                        "title": blog.get("title", ""),
                        "publishedDate": blog.get("publishedDate", ""),
                    }
                )

        # Process each blog with navigation
        for blog in blogs:
            # Only process published blogs
            if not blog.get("published", False):
                print(f"Skipping unpublished blog: {blog.get('title', 'Unknown')}")
                continue

            if not blog.get("title"):
                continue

            try:
                html_content, blog_slug = generate_blog_html(blog, blogs_data)
                output_file = blogs_dir / f"{blog_slug}.html"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                print(f"Generated blog: {output_file}")
            except Exception as e:
                print(f"Error generating blog {blog.get('title', 'unknown')}: {e}")


def generate_blog_links() -> List[Dict]:
    """Generate blog links for noscript content"""
    blogs = []
    print(f"\n📝 Processing {len(blog_files)} blog files...")

    for filename in blog_files:
        print(f"\n🔍 Processing blog file: {filename}")
        file_path = Path(CONFIG["DATA_DIR"]) / filename

        data = load_json_file(str(file_path))
        if not data:
            continue

        print(f"    📝 Found {len(data)} blog items")

        for i, blog in enumerate(data):
            # Only include published blogs
            if not blog.get("published", False):
                continue

            title = blog.get("title", "")
            if title:
                blog_slug = generate_blog_slug(title)

                # Clean title and description
                clean_title = re.sub(r"<[^>]*>", "", title)
                description = blog.get("description", "") or blog.get("excerpt", "")

                blogs.append(
                    {
                        "title": clean_title,
                        "url": f"{CONFIG['PUBLIC_PATH']}/blogs/{blog_slug}",
                        "slug": blog_slug,
                        "description": description,
                        "author": blog.get("author", "Team GTL"),
                        "category": blog.get("category", "Tax Insights"),
                        "published_date": blog.get("publishedDate", ""),
                        "image_url": blog.get("imageUrl", ""),
                    }
                )

    # Sort blogs by published date (newest first)
    blogs.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    print(f"📊 Total published blogs found: {len(blogs)}")
    return blogs


def generate_comprehensive_noscript(
    laws_data: Dict, guidances: List[Dict], treaties: List[Dict], blogs: List[Dict]
) -> str:
    """Generate comprehensive noscript content with all documents grouped by law"""

    total_articles = sum(len(law_data["articles"]) for law_data in laws_data.values())
    total_decisions = sum(len(law_data["decisions"]) for law_data in laws_data.values())

    noscript_content = f"""
<noscript>
  <style>
    .index-container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
      font-family: Arial, sans-serif;
      line-height: 1.6;
    }}
    .index-header {{
      text-align: center;
      margin-bottom: 40px;
      padding: 20px;
      background: #e2eaf2;
      border-radius: 8px;
    }}
    .index-header h1 {{
      color: #232536;
      margin-bottom: 10px;
    }}
    .index-header p {{
      color: #666;
    }}
    .section-title {{
      color: #232536;
      border-bottom: 3px solid;
      padding-bottom: 10px;
      display: flex;
      align-items: center;
    }}
    .section-count {{
      font-size: 14px;
      margin-left: 15px;
      color: #666;
      font-weight: normal;
    }}
    .section-box {{
      background: #e2eaf2;
      padding: 20px;
      border-radius: 8px;
      margin-bottom: 20px;
    }}
    .subsection-title {{
      color: #232536;
      border-left: 4px solid;
      padding-left: 15px;
      margin-bottom: 15px;
    }}
    .document-item {{
      border-left: 4px solid;
      padding: 15px;
      background: white;
      border-radius: 0 8px 8px 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    .document-description {{
      margin: 0;
      color: #666;
      font-size: 14px;
      line-height: 1.4;
    }}
  </style>
  <div class="index-container">
    <header class="index-header">
      <h1>📋 {CONFIG["SITE_NAME"]}</h1>
      <p style="font-size: 18px;">Searchable GCC tax database: UAE VAT & Corporate Tax (CIT) Saudi/KSA VAT customs duty excise transfer pricing and tax treaties (DTAA). Kuwait Oman Qatar Bahrain.</p>
      <p style="font-size: 16px;">
        <strong>{total_articles} Articles</strong> • 
        <strong>{total_decisions} Decisions</strong> • 
        <strong>{len(guidances)} Guidelines</strong> • 
        <strong>{len(treaties)} Tax Treaties</strong> • 
        <strong>{len(blogs)} Blog Posts</strong>
      </p>
    </header>
    
    <main>"""

    # Process each law and its articles/decisions
    for law_key, law_data in laws_data.items():
        law_info = law_data["law_info"]
        country_info = law_data["country_info"]
        articles = law_data["articles"]
        decisions = law_data["decisions"]

        country_flag = get_country_flag(country_info.get("flagCode", ""))

        # Determine law type for styling
        law_short = law_info.get("lawShortName", "")
        if "cit" in law_short.lower():
            border_color = "#007bff"
            emoji = "📊"
            law_type = "Corporate Income Tax"
        elif "vat" in law_short.lower():
            border_color = "#28a745"
            emoji = "💰"
            law_type = "Value Added Tax"
        elif "excise" in law_short.lower():
            border_color = "#dc3545"
            emoji = "🚬"
            law_type = "Excise Tax"
        elif "tp" in law_short.lower():
            border_color = "#6f42c1"
            emoji = "🔄"
            law_type = "Transfer Pricing"
        else:
            border_color = "#6c757d"
            emoji = "📜"
            law_type = "Tax Law"

        noscript_content += f"""
      <!-- {law_info.get('lawFullName', '')} -->
      <section style="margin-bottom: 50px;">
        <h2 class="section-title" style="border-bottom-color: {border_color};">
          {emoji} {country_flag} {html.escape(law_info.get('lawFullName', ''))}
          <span class="section-count">
            ({len(articles)} Articles • {len(decisions)} Decisions)
          </span>
        </h2>
        
        <div class="section-box">
          <p style="margin: 0; color: #666;">
            <strong>Country:</strong> {country_flag} {html.escape(country_info.get('countryName', ''))} • 
            <strong>Type:</strong> {law_type} • 
            <strong>Short Name:</strong> {html.escape(law_short)}
          </p>
        </div>"""

        # Articles section
        if articles:
            noscript_content += f"""
        <div style="margin-bottom: 30px;">
          <h3 class="subsection-title" style="border-left-color: {border_color};">
            📄 Articles ({len(articles)})
          </h3>
          <div style="display: grid; gap: 12px;">"""

            for article in articles:
                path_display = (
                    f" • Path: {html.escape(article.get('path', ''))}"
                    if article.get("path")
                    else ""
                )
                noscript_content += f"""
            <div class="document-item" style="border-left-color: {border_color};">
              <h4 style="margin: 0 0 8px 0; font-size: 16px;">
                <a href="{article['url']}" style="color: {border_color}; text-decoration: none;">
                  {html.escape(article['title'])}
                </a>
              </h4>
              <p style="margin: 0 0 8px 0; color: #666; font-size: 13px;">
                <strong>Article {article.get('number', '')}</strong> • Order: {article.get('orderIndex', 'N/A')}{path_display}
              </p>
              {f'<p class="document-description">{html.escape(article.get("description", "")[:200])}{"..." if len(article.get("description", "")) > 200 else ""}</p>' if article.get('description') else ''}
            </div>"""

            noscript_content += """
          </div>
        </div>"""

        # Decisions section
        if decisions:
            noscript_content += f"""
        <div style="margin-bottom: 30px;">
          <h3 class="subsection-title" style="border-left-color: {border_color};">
            ⚖️ Decisions ({len(decisions)})
          </h3>
          <div style="display: grid; gap: 12px;">"""

            for decision in decisions:
                noscript_content += f"""
            <div class="document-item" style="border-left-color: {border_color};">
              <h4 style="margin: 0 0 8px 0; font-size: 16px;">
                <a href="{decision['url']}" style="color: {border_color}; text-decoration: none;">
                  {html.escape(decision['title'])}
                </a>
              </h4>
              <p style="margin: 0 0 8px 0; color: #666; font-size: 13px;">
                <strong>{html.escape(decision.get('type', 'Decision'))} {decision.get('number', '')} of {decision.get('year', '')}</strong>
              </p>
              {f'<p style="margin: 0 0 8px 0; color: #666; font-size: 13px;"><strong>Official Name:</strong> {html.escape(decision.get("name", ""))}</p>' if decision.get('name') else ''}
              {f'<p style="margin: 0; color: #666; font-size: 14px; line-height: 1.4;">{html.escape(decision.get("description", "")[:200])}{"..." if len(decision.get("description", "")) > 200 else ""}</p>' if decision.get('description') else ''}
            </div>"""

            noscript_content += """
          </div>
        </div>"""

        noscript_content += """
      </section>"""

    # Guidelines section - grouped by law
    if guidances:
        # Group guidances by law_slug
        guidances_by_law = {}
        for guidance in guidances:
            law_slug = guidance.get("law_slug", "unknown")
            if law_slug not in guidances_by_law:
                guidances_by_law[law_slug] = []
            guidances_by_law[law_slug].append(guidance)

        noscript_content += f"""
      <!-- FTA Guidelines & Public Clarifications -->
      <section style="margin-bottom: 50px;">
        <h2 class="section-title" style="border-bottom-color: #e74c3c;">
          📋 FTA Guidelines & Public Clarifications ({len(guidances)})
        </h2>"""

        for law_slug, law_guidances in guidances_by_law.items():
            noscript_content += f"""
        <div style="margin-bottom: 30px;">
          <h3 class="subsection-title" style="border-left-color: #e74c3c;">
            {html.escape(law_slug.replace('-', ' ').title())} Guidelines ({len(law_guidances)})
          </h3>
          <div style="display: grid; gap: 12px;">"""

            for guidance in law_guidances:
                noscript_content += f"""
            <div class="document-item" style="border-left-color: #e74c3c;">
              <h4 style="margin: 0 0 8px 0; font-size: 15px;">
                <a href="{guidance['url']}" style="color: #e74c3c; text-decoration: none;">
                  {guidance.get('unique_code', '')}: {html.escape(guidance['title'])}
                </a>
              </h4>
              <p style="margin: 0 0 8px 0; color: #666; font-size: 13px;">
                <strong>{html.escape(guidance.get('type', 'FTA Guide'))}</strong>{f" • {guidance.get('year', '')}" if guidance.get('year') else ""}
              </p>
              {f'<p class="document-description">{html.escape(guidance.get("description", "")[:200])}{"..." if len(guidance.get("description", "")) > 200 else ""}</p>' if guidance.get("description") else ''}
            </div>"""

            noscript_content += """
          </div>
        </div>"""

        noscript_content += """
      </section>"""

    # Tax Treaties section
    if treaties:
        noscript_content += f"""
      <!-- UAE Tax Treaties & DTAs -->
      <section style="margin-bottom: 50px;">
        <h2 class="section-title" style="border-bottom-color: #9b59b6;">
          🤝 UAE Tax Treaties & DTAs ({len(treaties)})
        </h2>
        <div class="section-box">
          <p style="margin: 0; color: #666;">Double Taxation Avoidance Agreements between UAE and treaty partner countries</p>
        </div>
        <div style="display: grid; gap: 12px;">"""

        for treaty in treaties:
            status = (
                "Official" if treaty.get("official_translation", True) else "Unofficial"
            )
            country_flag = get_country_flag(treaty.get("flag_code", ""))
            noscript_content += f"""
          <div class="document-item" style="border-left-color: #9b59b6;">
            <h4 style="margin: 0 0 8px 0; font-size: 15px;">
              <a href="{treaty['url']}" style="color: #9b59b6; text-decoration: none;">
                {treaty.get('country1Slug', '')} - {country_flag} {treaty.get('country2Name', '')} Tax Treaty
              </a>
            </h4>
            <p style="margin: 0 0 8px 0; color: #666; font-size: 13px;">
              <strong>Country Code:</strong> {treaty.get('country2_alpha3', '')} • 
              <strong>Translation:</strong> {status}
              {f" • <strong>Year:</strong> {treaty.get('year', '')}" if treaty.get('year') else ""}
              {f" • <strong>Issue Date:</strong> {treaty.get('issue_date', '')}" if treaty.get('issue_date') else ""}
            </p>
            <p class="document-description">
              {html.escape(treaty.get('description', ''))}
            </p>
            <p style="margin: 8px 0 0 0; color: #666; font-size: 14px; line-height: 1.4;">
              <strong>Full Title:</strong> {html.escape(treaty['title'][:150])}{'...' if len(treaty['title']) > 150 else ''}
            </p>
          </div>"""

        noscript_content += """
        </div>
      </section>"""

    if blogs:
        noscript_content += f"""
      <!-- Blog Posts & Tax Insights -->
      <section style="margin-bottom: 50px;">
        <h2 class="section-title" style="border-bottom-color: #17a2b8;">
          📝 Latest Blog Posts & Tax Insights ({len(blogs)})
        </h2>
        <div class="section-box">
          <p style="margin: 0; color: #666;">Expert insights, analysis, and updates on GCC tax matters, regulations, and compliance</p>
        </div>
        <div style="display: grid; gap: 12px;">"""

        # Show only first 10 blogs in noscript to avoid too much content: "for blog in blogs[:10]:"
        for blog in blogs:
            # Parse published date
            published_date = blog.get("published_date", "")
            try:
                if published_date:
                    from datetime import datetime

                    parsed_date = datetime.fromisoformat(
                        published_date.replace("Z", "+00:00")
                    )
                    formatted_date = parsed_date.strftime("%B %d, %Y")
                else:
                    formatted_date = "Recently"
            except:
                formatted_date = "Recently"

            noscript_content += f"""
          <div class="document-item" style="border-left-color: #17a2b8;">
            <h4 style="margin: 0 0 8px 0; font-size: 15px;">
              <a href="{blog['url']}" style="color: #17a2b8; text-decoration: none;">
                {html.escape(blog['title'])}
              </a>
            </h4>
            <p style="margin: 0 0 8px 0; color: #666; font-size: 13px;">
              <strong>📅 {formatted_date}</strong> • 
              <strong>👤 {html.escape(blog.get('author', 'Team GTL'))}</strong> • 
              <strong>📂 {html.escape(blog.get('category', 'Tax Insights'))}</strong>
            </p>
            {f'<p class="document-description">{html.escape(blog.get("description", "")[:200])}{"..." if len(blog.get("description", "")) > 200 else ""}</p>' if blog.get('description') else ''}
          </div>"""

        # If there are more than 10 blogs, show a "view all" message
        if len(blogs) > 10:
            noscript_content += f"""
          <div style="text-align: center; padding: 20px; background: #e9ecef; border-radius: 8px;">
            <p style="margin: 0; color: #666;">
              <strong>And {len(blogs) - 10} more blog posts...</strong><br>
              <a href="{CONFIG['PUBLIC_PATH']}/blogs" style="color: #17a2b8;">View all blog posts →</a>
            </p>
          </div>"""

        noscript_content += """
        </div>
      </section>"""

    # Quick Navigation (updated to include blogs)
    noscript_content += f"""
      <!-- Quick Summary -->
      <section style="margin-bottom: 30px;">
        <h2 style="color: #232536;">📚 Browse All Documents</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
          <a href="#" style="padding: 15px; background: #e2eaf2; color: white; text-decoration: none; border-radius: 5px; text-align: center; display: block;">
            📄 All Articles ({total_articles})
          </a>
          <a href="#" style="padding: 15px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; text-align: center; display: block;">
            ⚖️ All Decisions ({total_decisions})
          </a>
          <a href="#" style="padding: 15px; background: #ffc107; color: white; text-decoration: none; border-radius: 5px; text-align: center; display: block;">
            📋 All Guidelines ({len(guidances)})
          </a>
          <a href="#" style="padding: 15px; background: #e74c3c; color: white; text-decoration: none; border-radius: 5px; text-align: center; display: block;">
            🤝 Tax Treaties ({len(treaties)})
          </a>
          <a href="{CONFIG['PUBLIC_PATH']}/blogs" style="padding: 15px; background: #17a2b8; color: white; text-decoration: none; border-radius: 5px; text-align: center; display: block;">
            📝 Blog Posts ({len(blogs)})
          </a>
        </div>
      </section>
      
      <div style="background: #fffbf0; border: 1px solid #ffc107; padding: 15px; border-radius: 8px; text-align: center;">
        <p style="margin: 0; color: #856404;">
          <strong>⚠️ JavaScript Required:</strong> This site uses JavaScript for enhanced functionality and search capabilities.
          <br>Please enable JavaScript in your browser for the full interactive experience.
        </p>
        <p style="margin: 10px 0 0 0;">
          <a href="/sitemap.xml" style="color: #007bff;">View Complete Sitemap</a> | 
          <a href="/search-across-law" style="color: #007bff;">Advanced Search</a>
        </p>
      </div>
    </main>
    
    <footer style="margin-top: 40px; padding: 20px; background: #232536; color: white; border-radius: 8px;">
      <div class="footer-grid" style="text-align: left;">
        <div>
          <h3 style="margin-bottom: 10px; color: white;">About {CONFIG["SITE_NAME"]}</h3>
          <p style="font-size: 14px; line-height: 1.6; color: #ccc;">Searchable GCC tax database: UAE VAT & Corporate Tax (CIT) Saudi/KSA VAT customs duty excise transfer pricing and tax treaties (DTAA). Kuwait Oman Qatar Bahrain.</p>
        </div>
        <div>
          <h3 style="margin-bottom: 10px; color: white;">Get In Touch</h3>
          <p style="font-size: 14px; margin-bottom: 8px; color: #ccc;">Have questions or suggestions?</p>
          <p style="font-size: 14px; color: #ccc;"><strong>📧 Email:</strong> <a href="mailto:support@gcctaxlaws.com" style="color: #17a2b8;">support@gcctaxlaws.com</a></p>
        </div>
      </div>
      <div class="footer-copyright">
        <p>&copy; {datetime.now().year} {CONFIG["SITE_NAME"]}</p>
        <p><a href="{CONFIG["SITE_URL"]}" style="color: #ccc;">Visit our main website</a></p>
      </div>
    </footer>
  </div>
</noscript>"""

    return noscript_content


def update_index_html_with_noscript(
    laws_data: Dict, guidances: List[Dict], treaties: List[Dict], blogs: List[Dict]
) -> None:
    """Update React's index.html with comprehensive noscript content including blogs"""
    print(f"\n🔄 Updating React index.html with comprehensive noscript content...")

    index_path = Path(CONFIG["INDEX_HTML_PATH"])

    if not index_path.exists():
        print(f"❌ Index.html not found at: {index_path}")
        return

    # Read current index.html
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            current_content = f.read()
        print(f"✅ Read existing index.html from {index_path}")
    except Exception as e:
        print(f"❌ Error reading index.html: {e}")
        return

    # Generate comprehensive noscript content including blogs
    noscript_content = generate_comprehensive_noscript(
        laws_data, guidances, treaties, blogs
    )

    # Replace existing noscript content
    if "<noscript>" in current_content and "</noscript>" in current_content:
        # Find the start and end of the existing noscript tag
        start_pos = current_content.find("<noscript>")
        end_pos = current_content.find("</noscript>") + len("</noscript>")

        # Replace with new comprehensive content
        new_content = (
            current_content[:start_pos] + noscript_content + current_content[end_pos:]
        )
        print("✅ Replaced existing noscript content")
    else:
        # Find position after <body> tag to insert noscript
        body_pos = current_content.find("<body>")
        if body_pos != -1:
            insert_pos = current_content.find(">", body_pos) + 1
            new_content = (
                current_content[:insert_pos]
                + "\n"
                + noscript_content
                + "\n"
                + current_content[insert_pos:]
            )
            print("✅ Inserted noscript content after body tag")
        else:
            print("❌ Could not find <body> tag in index.html")
            return

    # Write updated content back to index.html
    try:
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        total_articles = sum(
            len(law_data["articles"]) for law_data in laws_data.values()
        )
        total_decisions = sum(
            len(law_data["decisions"]) for law_data in laws_data.values()
        )
        total_docs = (
            total_articles
            + total_decisions
            + len(guidances)
            + len(treaties)
            + len(blogs)
        )

        print(
            f"✅ Successfully updated index.html with {total_docs} documents in noscript"
        )
        print(f"   📄 Articles: {total_articles}")
        print(f"   ⚖️ Decisions: {total_decisions}")
        print(f"   📋 Guidelines: {len(guidances)}")
        print(f"   🤝 Treaties: {len(treaties)}")
        print(f"   📝 Blogs: {len(blogs)}")
        print(f"📍 Updated file: {index_path}")

    except Exception as e:
        print(f"❌ Error writing updated index.html: {e}")


def process_articles_and_decisions_from_law_files() -> None:
    """Process articles and decisions from law JSON files"""

    articles_dir = Path(CONFIG["OUTPUT_DIR"]) / "articles"
    decisions_dir = Path(CONFIG["OUTPUT_DIR"]) / "decisions"
    guidances_dir = Path(CONFIG["OUTPUT_DIR"]) / "guidances"
    ensure_dir(str(articles_dir))
    ensure_dir(str(decisions_dir))
    ensure_dir(str(guidances_dir))

    # First, load ALL law files for relatedDocs lookups
    all_laws_data = []
    for filename in law_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if file_path.exists():
            data = load_json_file(str(file_path))
            if data:
                if isinstance(data, dict):
                    all_laws_data.append(data)
                elif isinstance(data, list):
                    all_laws_data.extend(data)

    # Now process each file
    for filename in law_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if not file_path.exists():
            print(f"Skipping {filename} - file not found")
            continue

        print(f"Processing {filename}...")
        data = load_json_file(str(file_path))

        if not data:
            continue

        # Handle both single objects and lists
        if isinstance(data, dict):
            data = [data]

        for country_data in data:
            country_info = {
                "countryName": country_data.get("countryName", "Unknown"),
                "alpha3Code": country_data.get("alpha3Code", ""),
                "flagCode": country_data.get("flagCode", ""),
                "phoneCode": country_data.get("phoneCode", ""),
            }

            for law in country_data.get("laws", []):
                law_info = {
                    "lawFullName": law.get("lawFullName", "Unknown Law"),
                    "lawShortName": law.get("lawShortName", "unknown-law"),
                }

                # Collect all articles for internal linking
                law_articles = law.get("articles", [])
                articles_data = []
                for article in law_articles:
                    if article.get("number") and article.get("title"):
                        article_slug = generate_article_slug(
                            law_info["lawShortName"],
                            article["number"],
                            country_info["countryName"],
                        )
                        articles_data.append(
                            {
                                "slug": article_slug,
                                "title": article.get("title", ""),
                                "number": article.get("number", ""),
                            }
                        )

                # Collect all decisions for internal linking
                law_decisions = law.get("decisions", [])
                decisions_data = []
                for decision in law_decisions:
                    # some decisions dont have number OR during parsing we are not aware of them
                    if (
                        decision.get("number")
                        or decision.get("title")
                        or decision.get("year")
                    ):
                        decision_slug = generate_decision_slug(
                            law_info["lawShortName"],
                            decision.get("number", ""),
                            decision.get("year", ""),
                            decision.get("type", ""),
                            country_info["countryName"],
                        )
                        decisions_data.append(
                            {
                                "slug": decision_slug,
                                "title": decision.get("title", ""),
                                "number": decision.get("number", ""),
                                "year": decision.get("year", ""),
                            }
                        )
                    else:
                        print(f"  ✗ SKIPPED in collection - missing all identifiers")
                # Process articles with navigation
                for article in law_articles:
                    if not article.get("number"):
                        continue

                    try:
                        html_content, article_slug = generate_article_html(
                            article,
                            law_info,
                            country_info,
                            articles_data,
                            all_laws_data,
                        )
                        output_file = articles_dir / f"{article_slug}.html"

                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(html_content)

                        print(f"Generated article: {output_file}")
                    except Exception as e:
                        print(
                            f"Error generating article {article.get('number', 'unknown')}: {e}"
                        )

                # Process decisions with navigation
                for decision in law_decisions:
                    # if not decision.get("number"): # since some decisions may not have numbers, check title as well
                    if (
                        not decision.get("number")
                        and not decision.get("title")
                        and not decision.get("year")
                    ):
                        print(f"  ✗ SKIPPED in processing - missing all identifiers")
                        continue

                    try:
                        html_content, decision_slug = generate_decision_html(
                            decision,
                            law_info,
                            country_info,
                            decisions_data,
                            all_laws_data,
                        )
                        output_file = decisions_dir / f"{decision_slug}.html"

                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(html_content)

                        print(f"Generated decision: {output_file}")
                    except Exception as e:
                        print(
                            f"Error generating decision {decision.get('number', 'unknown')}: {e}"
                        )

                # Process guidelines embedded in law files
                law_guidelines = law.get("guidelines", [])
                if law_guidelines:
                    # Collect all guidelines for internal linking
                    guidelines_data = []
                    for guideline in law_guidelines:
                        if guideline.get("uniqueCode") or guideline.get("title"):
                            try:
                                # Format: countryName-lawShortName-type-uniqueCode
                                country_prefix = (
                                    country_info["countryName"].lower().replace(" ", "-")
                                )
                                law_slug = guideline.get("lawSlug", f"{country_prefix}-{law_info['lawShortName']}")
                                guidance_slug = generate_guidance_slug(
                                    law_slug,
                                    guideline.get("type", ""),
                                    guideline.get("uniqueCode", ""),
                                )
                                guidelines_data.append(
                                    {
                                        "slug": guidance_slug,
                                        "title": guideline.get("title", ""),
                                        "uniqueCode": guideline.get("uniqueCode", ""),
                                    }
                                )
                                # Guidelines already have lawSlug in their data
                                html_content, _ = generate_guidance_html(
                                    guideline, law_info, guidelines_data, all_laws_data
                                )
                                output_file = guidances_dir / f"{guidance_slug}.html"

                                with open(output_file, "w", encoding="utf-8") as f:
                                    f.write(html_content)

                                print(f"Generated guidance: {output_file}")
                            except Exception as e:
                                print(
                                    f"Error generating guidance {guideline.get('uniqueCode', 'unknown')}: {e}"
                                )


def process_guidances() -> None:
    """Process guidance documents"""

    guidances_dir = Path(CONFIG["OUTPUT_DIR"]) / "guidances"
    ensure_dir(str(guidances_dir))

    # First, load ALL law files for relatedDocs lookups
    all_laws_data = []
    for filename in law_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if file_path.exists():
            data = load_json_file(str(file_path))
            if data:
                if isinstance(data, dict):
                    all_laws_data.append(data)
                elif isinstance(data, list):
                    all_laws_data.extend(data)

    for filename in guidance_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if not file_path.exists():
            print(f"Skipping {filename} - file not found")
            continue

        print(f"Processing {filename}...")
        guidances = load_json_file(str(file_path))

        # Collect all guidances for internal linking
        guidances_data = []
        for guidance in guidances:
            if guidance.get("uniqueCode") or guidance.get("title"):
                law_slug = guidance.get("lawSlug", "")
                guidance_slug = generate_guidance_slug(
                    law_slug, guidance.get("type", ""), guidance.get("uniqueCode", "")
                )
                guidances_data.append(
                    {
                        "slug": guidance_slug,
                        "title": guidance.get("title", ""),
                        "uniqueCode": guidance.get("uniqueCode", ""),
                    }
                )

        # Process each guidance with navigation
        for guidance in guidances:
            if not guidance.get("uniqueCode") and not guidance.get("title"):
                continue

            try:
                html_content, guidance_slug = generate_guidance_html(
                    guidance, None, guidances_data, all_laws_data
                )
                output_file = guidances_dir / f"{guidance_slug}.html"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                print(f"Generated guidance: {output_file}")
            except Exception as e:
                print(
                    f"Error generating guidance {guidance.get('uniqueCode', 'unknown')}: {e}"
                )

def process_treaties() -> None:
    """Process tax treaty documents"""

    treaties_dir = Path(CONFIG["OUTPUT_DIR"]) / "tax-treaties"
    ensure_dir(str(treaties_dir))

    # First, load ALL law files for relatedDocs lookups
    all_laws_data = []
    for filename in law_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if file_path.exists():
            data = load_json_file(str(file_path))
            if data:
                if isinstance(data, dict):
                    all_laws_data.append(data)
                elif isinstance(data, list):
                    all_laws_data.extend(data)

    for filename in treaty_files:
        file_path = Path(CONFIG["DATA_DIR"]) / filename
        if not file_path.exists():
            print(f"Skipping {filename} - file not found")
            continue

        print(f"Processing {filename}...")
        treaties = load_json_file(str(file_path))

        # Collect all treaties for internal linking
        treaties_data = []
        for treaty in treaties:
            if treaty.get("country2Name"):
                treaty_slug = generate_treaty_slug(
                    treaty.get("country1Slug", "uae").lower(),
                    treaty.get("country2Alpha3Code", "").lower(),
                )
                treaties_data.append(
                    {
                        "slug": treaty_slug,
                        "title": f"{treaty.get('country1Slug', 'uae')}-{treaty.get('country2Name', '')} DTAA",
                        "country2Name": treaty.get("country2Name", ""),
                    }
                )

        # Process each treaty with navigation
        for treaty in treaties:
            if not treaty.get("country2Name"):
                continue

            try:
                html_content, treaty_slug = generate_treaty_html(
                    treaty, treaties_data, all_laws_data
                )
                output_file = treaties_dir / f"{treaty_slug}.html"

                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                print(f"Generated treaty: {output_file}")
            except Exception as e:
                print(
                    f"Error generating treaty {treaty.get('country2Name', 'unknown')}: {e}"
                )


def create_index_pages(
    laws_data=None, guidances=None, treaties=None, blogs=None
) -> None:
    """Create index pages for each document type with rich information"""
    document_types = {
        "articles": laws_data,
        "decisions": laws_data,
        "guidances": guidances,
        "tax-treaties": treaties,
        "blogs": blogs,
    }

    for doc_type, data_source in document_types.items():
        type_dir = Path(CONFIG["OUTPUT_DIR"]) / doc_type
        if not type_dir.exists():
            continue

        # Get all HTML files in the directory
        html_files = list(type_dir.glob("*.html"))

        if not html_files:
            continue

        # Generate links for index page with rich information
        links = []

        if doc_type == "articles" and laws_data:
            # Rich article listing
            for law_key, law_data in laws_data.items():
                law_name = law_data["law_info"]["lawFullName"]
                articles = law_data.get("articles", [])

                if articles:
                    links.append(
                        f'<li class="law-section"><h3>{escape_html(law_name)}</h3><ul>'
                    )
                    for article in articles:
                        path_str = article.get("path", "")
                        preview_text = (
                            article.get("description", "")[:200]
                            if article.get("description")
                            else article.get("textOnly", "")[:200]
                        )
                    
                        links.append(
                            f"""
                        <li class="document-item">
                            <a href="{article.get('url', '')}">
                                <strong>{escape_html(article.get('title', 'Untitled'))}</strong>
                            </a>
                            <div class="document-description">
                                Article {article.get('number', '')} • Order: {article.get('orderIndex', '')}
                                {f" • Path: {escape_html(path_str)}" if path_str else ""}
                            </div>
                            <div class="document-preview">{escape_html(preview_text)}...</div>
                        </li>
                        """
                        )
                    links.append("</ul></li>")

        elif doc_type == "decisions" and laws_data:
            # Rich decision listing
            for law_key, law_data in laws_data.items():
                law_name = law_data["law_info"]["lawFullName"]
                decisions = law_data.get("decisions", [])
                if decisions:
                    links.append(
                        f'<li class="law-section"><h3>{escape_html(law_name)}</h3><ul>'
                    )
                    for decision in decisions:
                        preview_text = (
                            decision.get("description", "")[:200]
                            if decision.get("description")
                            else decision.get("textOnly", "")[:200]
                        )
                        decision_type = decision.get("type", "Decision")
                        links.append(
                            f"""
                        <li class="document-item">
                            <a href="{decision.get('url', '')}">
                                <strong>{escape_html(decision.get('title', 'Untitled'))}</strong>
                            </a>
                            <div class="document-description">
                                {decision_type} • Number: {decision.get('number', '')} • Year: {decision.get('year', '')}
                            </div>
                            <div class="document-preview">{escape_html(preview_text)}...</div>
                        </li>
                        """
                        )
                    links.append("</ul></li>")

        elif doc_type == "guidances" and guidances:
            # Rich guidance listing
            for guidance in guidances:
                preview_text = (
                    guidance.get("description", "")[:200]
                    if guidance.get("description")
                    else guidance.get("textOnly", "")[:200]
                )
                guidance_type = guidance.get("type", "Guidance")
                links.append(
                    f"""
                <li class="document-item">
                    <a href="{guidance.get('url', '')}">
                        <strong>{escape_html(guidance.get('title', 'Untitled'))}</strong>
                    </a>
                    <div class="document-description">
                        {guidance_type} • Code: {guidance.get('unique_code', '')}
                    </div>
                    <div class="document-preview">{escape_html(preview_text)}...</div>
                </li>
                """
                )

        elif doc_type == "tax-treaties" and treaties:
           
            for treaty in treaties:
                preview_text = (
                    treaty.get("description", "")[:200]
                    if treaty.get("description")
                    else treaty.get("textOnly", "")[:200]
                )

                # Get translation status
                is_official = treaty.get('official_translation')

                if is_official is True:
                    translation_status = "Translation: Official"
                elif is_official is False:
                    translation_status = "Translation: Unofficial"
                else:
                    translation_status = ""
                
                treaty_title = treaty.get('title', 'Tax Treaty')
                flag_code = treaty.get('flag_code', '')
                
                links.append(
                    f"""
                <li class="document-item">
                    <a href="{treaty.get('url', '')}">
                        <strong>{escape_html(treaty_title)}</strong>
                    </a>
                    <div class="document-description">
                        {treaty.get('country1Slug', 'Unknown')} - {treaty.get('flag_code', '')} {treaty.get('country2Name', 'Unknown')} {f"| {translation_status}" if translation_status else ""}
                    </div>
                    <div class="document-preview">{escape_html(preview_text)}...</div>
                </li>
                """
                )

        elif doc_type == "blogs" and blogs:
            # Rich blog listing
            for blog in blogs:
                preview_text = (
                    blog.get("description", "")[:200] if blog.get("description") else ""
                )
                links.append(
                    f"""
                <li class="document-item">
                    <a href="{blog.get('url', '')}">
                        <strong>{escape_html(blog.get('title', 'Untitled'))}</strong>
                    </a>
                    <div class="document-description">
                        Published: {blog.get('published_date', 'N/A')[:10]} • Category: {blog.get('category', '')}
                    </div>
                    <div class="document-preview">{escape_html(preview_text)}...</div>
                </li>
                """
                )
        else:
            # Fallback to basic listing if no data
            for html_file in html_files:
                file_slug = html_file.stem
                display_name = file_slug.replace("-", " ").title()
                links.append(
                    f'<li><a href="{CONFIG["PUBLIC_PATH"]}/{doc_type}/{file_slug}">{display_name}</a></li>'
                )

        # Create index page content
        index_content = f"""
        <div class="index-page">
            <h1>{doc_type.replace('-', ' ').title()}</h1>
            <p>Browse all {doc_type.replace('-', ' ')} in our database:</p>
            <ul class="document-list" style="list-style-type: none; padding: 0;">
                {''.join(links)}
            </ul>
        </div>
        """

        # Generate index page HTML
        title = f"All {doc_type.replace('-', ' ').title()} | {CONFIG['SITE_NAME']}"
        description = f"Browse comprehensive collection of {doc_type.replace('-', ' ')} for the GCC region (UAE, Saudi Arabia, Bahrain, Kuwait, Qatar and Oman) covering Corporate Income Tax, VAT, Excise, Customs, Zakat, FATCA, CRS and Double Taxation Avoidance Agreements."
        canonical = f"{CONFIG['SITE_URL']}/{doc_type}"

        structured_data = {
            "@context": "https://schema.org",
            "@type": "CollectionPage",
            "name": title,
            "description": description,
            "url": canonical,
            "mainEntity": {
                "@type": "ItemList",
                "numberOfItems": len(html_files),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i + 1,
                        "name": html_file.stem.replace("-", " ").title(),
                        "url": f"{CONFIG['SITE_URL']}{CONFIG['PUBLIC_PATH']}/{doc_type}/{html_file.stem}",
                    }
                    for i, html_file in enumerate(html_files)
                ],
            },
        }

        breadcrumb_html = f"""
        <nav class="breadcrumb-nav" aria-label="Breadcrumb">
            <div class="container">
                <a href="/">Home</a> › <strong>{doc_type.replace('-', ' ').title()}</strong>
            </div>
        </nav>"""

        doc_meta = f"""
        <div class="document-meta">
            <strong>Total Documents:</strong> {len(html_files)}<br>
            <strong>Category:</strong> {doc_type.replace('-', ' ').title()}<br>
            <strong>Last Updated:</strong> {datetime.now().strftime('%B %d, %Y')}
        </div>"""

        index_html = generate_base_html(
            title=title,
            description=description,
            canonical=canonical,
            doc_meta=doc_meta,
            breadcrumb_html=breadcrumb_html,
            content=index_content,
            structured_data=structured_data,
            document_type=doc_type,
            item={"title": title, "slug": "index"},
        )

        # Save index page
        index_file = type_dir / "index.html"
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(index_html)

        print(f"Generated index: {index_file}")


def create_main_sitemap() -> None:
    """Create main sitemap.xml file"""
    sitemap_dir = Path(CONFIG["OUTPUT_DIR"])
    ensure_dir(str(sitemap_dir))

    urls = []

    # Add main pages
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/",
            "changefreq": "daily",
            "priority": "1.0",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/search-across-law",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/cookie-policy",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/privacy-policy",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/terms-and-conditions",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/about-us",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/contact-us",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )
    urls.append(
        {
            "loc": f"{CONFIG['SITE_URL']}/features",
            "changefreq": "weekly",
            "priority": "0.8",
        }
    )

    # Add category pages
    for category in ["articles", "decisions", "guidances", "tax-treaties"]:
        urls.append(
            {
                "loc": f"{CONFIG['SITE_URL']}/{category}",
                "changefreq": "weekly",
                "priority": "0.8",
            }
        )

        # Add individual documents
        category_dir = Path(CONFIG["OUTPUT_DIR"]) / category
        if category_dir.exists():
            for html_file in category_dir.glob("*.html"):
                if html_file.name != "index.html":
                    urls.append(
                        {
                            "loc": f"{CONFIG['SITE_URL']}/{category}/{html_file.stem}",
                            "changefreq": "monthly",
                            "priority": "0.6",
                        }
                    )

    # Generate sitemap XML
    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">"""

    for url in urls:
        sitemap_xml += f"""
    <url>
        <loc>{url['loc']}</loc>
        <changefreq>{url['changefreq']}</changefreq>
        <priority>{url['priority']}</priority>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    </url>"""

    sitemap_xml += "\n</urlset>"

    # Save sitemap
    sitemap_file = sitemap_dir / "sitemap.xml"
    with open(sitemap_file, "w", encoding="utf-8") as f:
        f.write(sitemap_xml)

    print(f"Generated sitemap: {sitemap_file}")


def create_robots_txt() -> None:
    """Create robots.txt file"""
    robots_content = f"""User-agent: *
Allow: /

# Sitemaps
Sitemap: {CONFIG['SITE_URL']}/sitemap.xml

# Block access to SEO directory for humans
User-agent: *
Disallow: /register
Disallow: /login
Disallow: /seo/

# Allow bots to access all content
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: Slurp
Allow: /

# Block development paths
Disallow: /internal-seo/
"""

    robots_file = Path(CONFIG["OUTPUT_DIR"]) / "robots.txt"
    with open(robots_file, "w", encoding="utf-8") as f:
        f.write(robots_content)

    print(f"Generated robots.txt: {robots_file}")


def generate_manifest_json() -> None:
    """Generate web app manifest for SEO pages"""
    manifest = {
        "name": CONFIG["SITE_NAME"],
        "short_name": "GTL",
        "description": "Explore up-to-date GCC tax insights including VAT updates, corporate tax regulations, Zakat rules, Double Taxation Avoidance Agreements, and compliance guidance across UAE, Saudi Arabia, Bahrain, Kuwait, Qatar and Oman",
        "start_url": "/",
        "display": "minimal-ui",
        "theme_color": "#ffffff",
        "background_color": "#29497e",
        "icons": [
            {
                "src": "/web-app-manifest-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
            },
            {
                "src": "/web-app-manifest-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
            },
        ],
    }

    manifest_file = Path(CONFIG["OUTPUT_DIR"]) / "site.webmanifest"
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated manifest.json: {manifest_file}")


def cleanup_output_directory() -> None:
    """Clean up the output directory before generation"""
    output_path = Path(CONFIG["OUTPUT_DIR"])
    if output_path.exists():
        print(f"Cleaning up existing directory: {output_path}")
        shutil.rmtree(output_path)

    ensure_dir(str(output_path))
    print(f"Created clean output directory: {output_path}")


def main() -> None:
    """Main function to generate all SEO pages and update index.html"""
    print("🚀 Starting SEO HTML generation...")
    print(f"📁 Output directory: {CONFIG['OUTPUT_DIR']}")
    print(f"📁 Data directory: {CONFIG['DATA_DIR']}")
    print(f"📄 Index.html path: {CONFIG['INDEX_HTML_PATH']}")

    # Clean up and create output directory
    cleanup_output_directory()

    try:
        # Process all document types
        print("\n📄 Processing articles and decisions from law files...")
        process_articles_and_decisions_from_law_files()

        print("\n📋 Processing guidance documents...")
        process_guidances()

        print("\n🤝 Processing tax treaties...")
        process_treaties()

        print("\n📝 Processing blog posts...")
        process_blogs()

        print("\n" + "=" * 60)
        print("🔄 COLLECTING DATA FOR INDEX PAGES AND NOSCRIPT")
        print("=" * 60)

        # Process data once for both index pages and noscript generation
        laws_data = process_laws_with_articles_and_decisions()
        guidances = generate_guidance_links()
        treaties = generate_treaty_links()
        blogs = generate_blog_links()

        print("\n📑 Creating index pages...")
        create_index_pages(laws_data, guidances, treaties, blogs)

        print("\n🗺️ Creating sitemap...")
        create_main_sitemap()

        print("\n🤖 Creating robots.txt...")
        create_robots_txt()

        print("\n📱 Creating manifest.json...")
        generate_manifest_json()

        print("\n" + "=" * 60)
        print("🔄 UPDATING REACT INDEX.HTML WITH NOSCRIPT CONTENT")
        print("=" * 60)

        # Update index.html with comprehensive noscript
        update_index_html_with_noscript(laws_data, guidances, treaties, blogs)

        # Count generated files
        total_files = 0
        for doc_type in ["articles", "decisions", "guidances", "tax-treaties", "blogs"]:
            type_dir = Path(CONFIG["OUTPUT_DIR"]) / doc_type
            if type_dir.exists():
                count = len(list(type_dir.glob("*.html")))
                total_files += count
                print(f"   {doc_type}: {count} files")

        print(f"\n✅ SEO generation completed successfully!")
        print(f"📊 Total HTML files generated: {total_files}")
        print(f"📍 Files location: {CONFIG['OUTPUT_DIR']}")
        print(f"🌐 Your nginx config will serve bots from: {CONFIG['OUTPUT_DIR']}")
        print(f"📄 Updated React index.html: {CONFIG['INDEX_HTML_PATH']}")

        # Show some example URLs
        print(f"\n🔗 Example URLs that will work:")
        print(
            f"   Articles: {CONFIG['SITE_URL']}/articles/uae-cit-fdl-47-of-2022-article-1"
        )
        print(
            f"   Decisions: {CONFIG['SITE_URL']}/decisions/uae-cit-fdl-47-of-2022-cd-35-of-2025"
        )
        print(
            f"   Guidances: {CONFIG['SITE_URL']}/guidances/uae-cit-fdl-47-of-2022-guide-CTGFF1"
        )
        print(f"   Treaties: {CONFIG['SITE_URL']}/tax-treaties/uae-alb-dtaa")
        print(
            f"   Blogs: {CONFIG['SITE_URL']}/blogs/the-double-irish-with-a-dutch-sandwich"
        )

    except Exception as e:
        print(f"\n❌ Error during generation: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
