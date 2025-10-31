# Integration Guide: Using New Modules with seo.py

This guide shows how to integrate the new modular components (Pydantic config, Jinja2 templates, caching, logging) with the existing `seo.py` file.

## Overview

The new modules provide:
- **config.py**: Type-safe configuration with Pydantic
- **logger.py**: Centralized logging
- **utils.py**: Cached utility functions
- **template_renderer.py**: Jinja2 template rendering
- **interfaces.py**: Type-checked protocols

## Step-by-Step Integration

### 1. Replace CONFIG Dict with Pydantic Config

**Before (in seo.py):**
```python
CONFIG = {
    "SITE_URL": "https://gcctaxlaws.com",
    "SITE_NAME": "GCC Tax Laws",
    # ...
}
```

**After:**
```python
from config import get_default_config

CONFIG = get_default_config()

# Access config values
site_url = CONFIG.site_url
site_name = CONFIG.site_name
output_dir = CONFIG.output_dir  # This is a Path object
```

### 2. Replace Print Statements with Logger

**Before:**
```python
print("Processing article...")
print(f"Generated {count} files")
```

**After:**
```python
from logger import get_logger

logger = get_logger()

logger.info("Processing article...")
logger.info(f"Generated {count} files")

# For errors
try:
    # some code
except Exception as e:
    logger.error(f"Failed to process: {e}", exc_info=e)
```

### 3. Use Cached Utility Functions

**Before:**
```python
def get_country_flag(country_code: str) -> str:
    flag_map = {...}
    return flag_map.get(country_code.upper(), "🏳️")
```

**After:**
```python
from utils import get_country_flag, get_authority_name

# These functions are now cached
flag = get_country_flag("AE")
authority = get_authority_name("uae-cit-law")
```

### 4. Use Jinja2 Templates for HTML Generation

**Before (string concatenation):**
```python
def generate_unified_html(title, description, ...):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>{title}</title>
    ...
</head>
<body>
    {content}
</body>
</html>"""
```

**After (Jinja2 templates):**
```python
from template_renderer import TemplateRenderer

renderer = TemplateRenderer(CONFIG)

context = {
    "meta_title": title,
    "description": description,
    "content": content,
    # ... other context variables
}

html = renderer.render_base_html(context)
```

## Migration Strategy

### Option 1: Gradual Migration (Recommended)

Keep the existing `seo.py` working as-is, but start using new modules for new features:

```python
# At the top of seo.py
from config import get_default_config
from logger import get_logger
from utils import get_country_flag, get_authority_name

# Initialize
CONFIG = get_default_config()
logger = get_logger()

# Replace print statements gradually
# print("Starting...") -> logger.info("Starting...")

# Use cached functions where available
# Direct calls to original functions still work
```

### Option 2: Full Refactor

Create a new `seo_v2.py` that uses all new modules:

```python
#!/usr/bin/env python3
"""
SEO HTML Generator v2 - Using modular components
"""

from config import get_default_config, get_default_file_list_config
from logger import get_logger
from template_renderer import TemplateRenderer
from utils import (
    get_country_flag,
    get_authority_name,
    escape_html,
    truncate_text,
    generate_slug,
)

# Initialize
config = get_default_config()
file_config = get_default_file_list_config()
logger = get_logger()
renderer = TemplateRenderer(config)

# Use throughout your code
logger.info(f"Starting SEO generation for {config.site_name}")

# ... rest of your code
```

## Benefits of Migration

1. **Type Safety**: Pydantic validates configuration at startup
2. **IDE Support**: Better autocomplete and type hints
3. **Performance**: LRU cache on frequently called functions
4. **Debugging**: Centralized logging makes debugging easier
5. **Maintainability**: Separation of concerns, cleaner code
6. **Testing**: Easier to test individual components

## Example: Converting a Function

**Before:**
```python
def generate_article_html(article, law_info, country_info):
    flag = get_country_flag(country_info['flagCode'])
    authority = get_authority_name(law_info['lawSlug'])
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>{article['title']}</title>
    </head>
    <body>
        <h1>{article['title']}</h1>
        <p>Flag: {flag}</p>
        <p>Authority: {authority}</p>
    </body>
    </html>"""
    
    print(f"Generated article: {article['title']}")
    return html
```

**After:**
```python
from config import get_default_config
from logger import get_logger
from template_renderer import TemplateRenderer
from utils import get_country_flag, get_authority_name, escape_html

config = get_default_config()
logger = get_logger()
renderer = TemplateRenderer(config)

def generate_article_html(article, law_info, country_info):
    # Cached functions - faster on repeated calls
    flag = get_country_flag(country_info['flagCode'])
    authority = get_authority_name(law_info['lawSlug'])
    
    # Use templates
    context = {
        "meta_title": escape_html(article['title']),
        "description": article.get('metaDescription', ''),
        "content": f"""
            <h1>{article['title']}</h1>
            <p>Flag: {flag}</p>
            <p>Authority: {authority}</p>
        """,
        # ... other required context
    }
    
    html = renderer.render_base_html(context)
    
    logger.info(f"Generated article: {article['title']}")
    return html
```

## Testing Your Changes

After integration:

```bash
# Run tests
pytest tests/ -v

# Check formatting
black seo.py

# Lint
ruff check seo.py

# Type check
mypy seo.py --ignore-missing-imports
```

## Need Help?

- Check `example_usage.py` for working examples
- Run `python example_usage.py` to see the modules in action
- Refer to test files in `tests/` for usage patterns
