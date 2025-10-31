# seo-py

SEO HTML Generator for UAE Tax Consulting Platform - Generates static HTML pages from JSON data with world-class engineering practices.

## Features

- ✅ **Pydantic Config**: Type-safe configuration with validation and IDE autocompletion
- ✅ **Jinja2 Templates**: Clean separation of presentation from logic
- ✅ **LRU Caching**: Performance optimization for deterministic functions
- ✅ **Centralized Logging**: Unified error reporting and logging
- ✅ **Type-Checked Interfaces**: Protocol-based interfaces for better IDE hints
- ✅ **Unit Tests**: Comprehensive test coverage with pytest
- ✅ **CI/CD Pipeline**: Automated testing with GitHub Actions
- ✅ **Code Quality**: Black, Ruff, and mypy for formatting, linting, and type checking

## Installation

```bash
pip install -r requirements.txt
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Format code
black .

# Lint code
ruff check --fix .

# Type check
mypy --ignore-missing-imports config.py logger.py utils.py template_renderer.py interfaces.py

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Usage

```python
from config import get_default_config, get_default_file_list_config
from logger import get_logger
from template_renderer import TemplateRenderer

# Get configuration
config = get_default_config()
logger = get_logger()

# Initialize template renderer
renderer = TemplateRenderer(config)

# Render HTML
context = {
    "meta_title": "Your Page Title",
    "description": "Page description",
    # ... other context variables
}
html = renderer.render_base_html(context)
```

## Project Structure

```
seo-py/
├── config.py              # Pydantic configuration models
├── logger.py              # Centralized logging
├── utils.py               # Utility functions with caching
├── template_renderer.py   # Jinja2 template rendering
├── interfaces.py          # Type-checked protocols
├── seo.py                 # Main application (legacy)
├── templates/             # Jinja2 templates
│   ├── base.html
│   └── meta_tags.html
├── tests/                 # Unit tests
│   ├── test_config.py
│   ├── test_logger.py
│   ├── test_utils.py
│   └── test_template_renderer.py
├── requirements.txt       # Dependencies
├── pyproject.toml         # Project configuration
└── .pre-commit-config.yaml # Pre-commit hooks
```

## CI/CD

The project uses GitHub Actions for continuous integration:
- Runs tests on Python 3.8, 3.9, 3.10, 3.11, and 3.12
- Checks code formatting with Black
- Lints code with Ruff
- Type checks with mypy

## Contributing

1. Install pre-commit hooks: `pre-commit install`
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Commit your changes (pre-commit will run automatically)
5. Push and create a pull request

## License

All rights reserved.