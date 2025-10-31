"""
Type-checked interfaces for SEO document generation.
"""

from typing import Any, Dict, Protocol, Tuple


class SEODocumentGenerator(Protocol):
    """Protocol for SEO document generators."""

    def generate_html(self, item: Dict[str, Any], **kwargs) -> Tuple[str, str]:
        """
        Generate HTML for a document.

        Args:
            item: Document data dictionary
            **kwargs: Additional parameters

        Returns:
            Tuple of (html_content, slug)
        """
        ...


class SEOBaseDocument(Protocol):
    """Protocol for base document structure."""

    title: str
    slug: str
    content: str
    meta_description: str
    meta_keywords: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        ...
