"""
Template rendering module using Jinja2.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from config import SEOConfig


class TemplateRenderer:
    """Template renderer for HTML generation using Jinja2."""

    def __init__(self, config: SEOConfig, template_dir: str = "templates"):
        """
        Initialize the template renderer.

        Args:
            config: SEO configuration
            template_dir: Directory containing templates
        """
        self.config = config
        self.template_dir = Path(__file__).parent / template_dir

        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Add custom filters
        self._add_custom_filters()

    def _add_custom_filters(self) -> None:
        """Add custom Jinja2 filters."""

        def truncate_text(text: str, max_length: int) -> str:
            """Truncate text to specified length."""
            if not text or len(text) <= max_length:
                return text or ""
            return text[:max_length].strip() + "..."

        self.env.filters["truncate_text"] = truncate_text

    def render_base_html(self, context: Dict[str, Any]) -> str:
        """
        Render the base HTML template.

        Args:
            context: Template context dictionary

        Returns:
            Rendered HTML string
        """
        # Add config values to context
        context.update(
            {
                "site_url": self.config.site_url,
                "site_name": self.config.site_name,
                "public_path": self.config.public_path,
                "twitter_handle": self.config.twitter_handle,
                "current_year": datetime.now(timezone.utc).year,
            }
        )

        template = self.env.get_template("base.html")
        return template.render(**context)

    def render_meta_tags(self, **kwargs) -> str:
        """
        Render meta tags template.

        Args:
            **kwargs: Meta tag parameters

        Returns:
            Rendered meta tags HTML
        """
        template = self.env.get_template("meta_tags.html")
        return template.render(**kwargs)
