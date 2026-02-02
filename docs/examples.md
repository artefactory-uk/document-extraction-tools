# Examples

For complete, working implementations of document extraction pipelines, see the **examples repository**:

<div class="grid cards" markdown>

-   :material-github:{ .lg .middle } **document-extraction-examples**

    ---

    Full working examples including:

    - Lease document extraction with Gemini
    - PDF-to-image conversion pipeline
    - Evaluation with accuracy and F1 metrics
    - MLflow integration for tracing
    - YAML-based configuration

    [:octicons-arrow-right-24: View Examples Repository](https://github.com/artefactory-uk/document-extraction-examples)

</div>

## What's in the Examples Repository

The examples repository contains complete, runnable implementations that demonstrate:

### Simple Lease Extraction

A complete pipeline for extracting structured lease details from PDF documents using Google's Gemini API with image inputs:

```
src/document_extraction_examples/simple_lease_extraction/
├── components/          # Interface implementations
│   ├── file_lister.py   # Local file discovery
│   ├── reader.py        # PDF file reading
│   ├── converter.py     # PDF-to-image conversion
│   ├── extractor.py     # Gemini-based extraction
│   └── exporter.py      # JSON output
├── config/              # Pydantic config classes
├── data/                # Sample inputs and evaluation data
├── prompts/             # Prompt templates
├── schemas/             # Extraction schemas (lease details)
├── utils/               # MLflow and LLM utilities
├── extraction_main.py   # Extraction workflow entry point
└── evaluation_main.py   # Evaluation workflow entry point
```

**Target Fields:**

The `SimpleLeaseDetails` schema captures:

- Landlord and tenant information
- Property address details
- Lease start and end dates
- Financial terms (rent, deposit, payment frequency)

### Evaluation Pipeline

How to measure extraction quality against a labeled dataset:

- Test data loader for ground truth JSON
- Accuracy evaluator for exact field matching
- F1 evaluator with optional LLM-as-a-judge capability
- Results export to JSON

### MLflow Integration

The example demonstrates MLflow tracing for observability:

- Span tracking for the overall pipeline
- Individual document processing traces
- Connection to MLflow tracking server

## Prerequisites

Before running the examples:

- Python (version specified in `pyproject.toml`)
- [Poppler](https://poppler.freedesktop.org/) for PDF processing
- Docker for MLflow server (optional)
- Gemini API key

## Running the Examples

```bash
# Clone the examples repository
git clone https://github.com/artefactory-uk/document-extraction-examples.git
cd document-extraction-examples

# Install dependencies
make install
# Or: uv sync

# Create .env file with your API key
echo "GEMINI_API_KEY=your-key-here" > .env

# Start MLflow server (optional, for tracing)
make start-mlflow

# Run the extraction pipeline
make run

# Run the evaluation pipeline
make evaluate
```

## Using Examples as Templates

The examples repository is designed to be used as a starting point for your own pipelines:

1. **Fork or clone** the repository
2. **Create your schema** - Define a Pydantic model for your target output (e.g., invoices, contracts, receipts)
3. **Implement components** - Subclass the base interfaces for your specific needs:
    - Custom reader for your file source (local, S3, GCS, etc.)
    - Converter for your document format (PDF, images, DOCX)
    - Extractor using your preferred LLM (Gemini, OpenAI, Anthropic)
4. **Configure the pipeline** - Add YAML configuration files
5. **Set up evaluation** - Create ground truth data and implement evaluators
