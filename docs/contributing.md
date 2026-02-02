# Contributing

Contributions to Document Extraction Tools are welcome!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/document-extraction-tools.git
   cd document-extraction-tools
   ```
3. Install dependencies:
   ```bash
   uv sync
   ```

## Development Workflow

### Branch Naming

Use descriptive branch names with prefixes:

- `feat/short-description` - New features
- `fix/short-description` - Bug fixes
- `docs/short-description` - Documentation updates
- `refactor/short-description` - Code refactoring
- `test/short-description` - Test additions/updates

### Running Tests

```bash
uv run pytest
```

### Linting and Formatting

Run pre-commit hooks before committing:

```bash
uv run pre-commit run --all-files
```

This runs:

- **Ruff** - Linting and formatting
- **Type checking** - Via pyright/mypy

### Code Style

The project uses:

- **Ruff** for linting and formatting
- **Google-style docstrings**
- **Type hints** throughout

Example:

```python
class BaseExtractor(ABC):
    """Abstract interface for data extraction."""

    def __init__(self, config: BaseExtractorConfig) -> None:
        """Initialize with a configuration object.

        Args:
            config: Configuration specific to the extractor implementation.
        """
        self.config = config

    @abstractmethod
    async def extract(
        self, document: Document, schema: type[ExtractionSchema]
    ) -> ExtractionSchema:
        """Extracts structured data from a Document to match the provided Schema.

        Args:
            document: The fully parsed document.
            schema: The Pydantic model class defining the target structure.

        Returns:
            An instance of the schema populated with the extracted data.
        """
        pass
```

## Pull Request Process

1. Create a new branch from `main`
2. Make your changes
3. Run tests and linting:
   ```bash
   uv run pre-commit run --all-files
   uv run pytest
   ```
4. Commit with clear, descriptive messages
5. Push to your fork
6. Open a PR against `main`
7. Fill out the PR template with:
   - Description of changes
   - Related issues
   - Testing performed

## Reporting Issues

Open an issue on GitHub with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (Python version, OS, etc.)

## Maintainers

- [Ollie Kemp](https://github.com/ollie-artefact)
- [Nikolas Moatsos](https://github.com/nmoatsos)

Feel free to reach out if you have questions about contributing!
