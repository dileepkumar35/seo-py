"""
Configuration module using Pydantic for validation and type safety.
"""

from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict, field_validator


class SEOConfig(BaseModel):
    """Configuration model for SEO HTML Generator with validation."""

    model_config = ConfigDict(frozen=False)

    # Site configuration
    site_url: str  # Changed from HttpUrl to str for flexibility with trailing slashes
    site_name: str
    twitter_handle: str
    default_og_image: str

    # Paths
    output_dir: Path
    public_path: str
    data_dir: Path
    index_html_path: Path

    @field_validator("output_dir", "data_dir", "index_html_path", mode="before")
    @classmethod
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        if isinstance(v, str):
            return Path(v)
        return v

    @field_validator("twitter_handle")
    @classmethod
    def validate_twitter_handle(cls, v: str) -> str:
        """Ensure twitter handle starts with @."""
        if not v.startswith("@"):
            return f"@{v}"
        return v


class FileListConfig(BaseModel):
    """Configuration for data file lists."""

    law_files: List[str]
    guidance_files: List[str]
    treaty_files: List[str]
    blog_files: List[str]


# Default configuration
def get_default_config() -> SEOConfig:
    """Get the default SEO configuration."""
    return SEOConfig(
        site_url="https://gcctaxlaws.com",
        site_name="GCC Tax Laws",
        twitter_handle="@gcctaxlaws",
        default_og_image="/web-app-manifest-512x512.png",
        output_dir=Path("./public/seo"),
        public_path="",
        data_dir=Path("./data"),
        index_html_path=Path("./public/index.html"),
    )


def get_default_file_list_config() -> FileListConfig:
    """Get the default file list configuration."""
    return FileListConfig(
        law_files=[
            "1-gcc-vat-agreement.json",
            "2-gcc-excise-agreement.json",
            "3-uae-cit-47-country-law-articles-decisions.json",
            "6-uae-vat-country-law-articles-decisions.json",
            "8-uae-tp-country-law-articles.json",
            "13-ksa-incometax-country-law-articles-guides.json",
            "20-kwt-ktl-country-law-articles.json",
            "21-kwt-dl-157-country-law-articles.json",
        ],
        guidance_files=[
            "4-uae-cit-guidelines-guide.json",
            "4-uae-cit-guidelines-pc.json",
            "7-uae-vat-guidelines-guide-pc.json",
            "9-uae-tp-guidelines-guide-pc.json",
        ],
        treaty_files=[
            "dtaa-uae-1.json",
            "dtaa-uae-2.json",
            "dtaa-ksa.json",
            "dtaa-kuwait.json",
            "dtaa-qatar.json",
            "dtaa-oman.json",
            "dtaa-bahrain.json",
        ],
        blog_files=[
            "blogs.json",
        ],
    )
