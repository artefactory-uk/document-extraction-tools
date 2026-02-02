# Examples

For complete, working implementations of document extraction pipelines, see the **examples repository**:

<div class="grid cards" markdown>

-   :material-github:{ .lg .middle } **document-extraction-examples**

    ---

    Full working examples including:

    - Invoice extraction with LLM
    - PDF processing pipeline
    - Evaluation setup with metrics
    - Configuration examples

    [:octicons-arrow-right-24: View Examples Repository](https://github.com/artefactory-uk/document-extraction-examples)

</div>

## What's in the Examples Repository

The examples repository contains complete, runnable implementations that demonstrate:

### Invoice Extraction Pipeline

A complete pipeline for extracting structured data from invoice PDFs:

- Custom `InvoiceSchema` with line items
- PDF reader and converter implementations
- LLM-based extractor using OpenAI/Anthropic
- JSON file exporter

### Evaluation Pipeline

How to measure extraction quality:

- Ground truth dataset setup
- Multiple evaluators (field accuracy, numeric tolerance)
- Results export to CSV

### Configuration

Example YAML configuration files for all components:

```
config/yaml/
├── extraction_orchestrator.yaml
├── file_lister.yaml
├── reader.yaml
├── converter.yaml
├── extractor.yaml
└── extraction_exporter.yaml
```

## Running the Examples

```bash
# Clone the examples repository
git clone https://github.com/artefactory-uk/document-extraction-examples.git
cd document-extraction-examples

# Install dependencies
uv sync

# Run the extraction pipeline
uv run python -m examples.invoice_extraction

# Run the evaluation pipeline
uv run python -m examples.invoice_evaluation
```

## Using Examples as Templates

The examples repository is designed to be used as a starting point for your own pipelines:

1. Fork or clone the repository
2. Modify the schema to match your document type
3. Implement custom reader/converter for your file formats
4. Configure your LLM extractor
5. Set up evaluation with your ground truth data
