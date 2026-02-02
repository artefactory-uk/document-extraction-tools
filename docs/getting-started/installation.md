# Installation

## Requirements

- Python 3.12 or higher

## Install from PyPI

=== "pip"

    ```bash
    pip install document-extraction-tools
    ```

=== "uv"

    ```bash
    uv add document-extraction-tools
    ```

=== "poetry"

    ```bash
    poetry add document-extraction-tools
    ```

## Install from Source

For development or to get the latest changes:

```bash
git clone https://github.com/artefactory-uk/document-extraction-tools.git
cd document-extraction-tools
uv sync
```

## Verify Installation

```python
import document_extraction_tools
print(document_extraction_tools.__version__)
```

## Dependencies

The library has minimal core dependencies:

- `pydantic>=2.0.0` - Data validation and settings management
- `PyYAML>=6.0.3` - YAML configuration support
- `numpy>=2.4.1` - Numerical operations
- `pillow>=12.1.0` - Image processing

Additional dependencies may be required depending on your specific extractors and converters (e.g., PDF libraries, OCR engines, LLM clients).
