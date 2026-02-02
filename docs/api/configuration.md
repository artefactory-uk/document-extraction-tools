# Configuration API

Configuration classes and loading utilities.

## Config Loaders

### load_config

::: document_extraction_tools.config.load_config
    options:
      show_root_heading: true
      heading_level: 4

### load_evaluation_config

::: document_extraction_tools.config.load_evaluation_config
    options:
      show_root_heading: true
      heading_level: 4

## Extraction Pipeline Configs

### BaseFileListerConfig

::: document_extraction_tools.config.BaseFileListerConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseReaderConfig

::: document_extraction_tools.config.BaseReaderConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseConverterConfig

::: document_extraction_tools.config.BaseConverterConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseExtractorConfig

::: document_extraction_tools.config.BaseExtractorConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseExtractionExporterConfig

::: document_extraction_tools.config.BaseExtractionExporterConfig
    options:
      show_root_heading: true
      heading_level: 4

### ExtractionOrchestratorConfig

::: document_extraction_tools.config.ExtractionOrchestratorConfig
    options:
      show_root_heading: true
      heading_level: 4

## Evaluation Pipeline Configs

### BaseTestDataLoaderConfig

::: document_extraction_tools.config.BaseTestDataLoaderConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseEvaluatorConfig

::: document_extraction_tools.config.BaseEvaluatorConfig
    options:
      show_root_heading: true
      heading_level: 4

### BaseEvaluationExporterConfig

::: document_extraction_tools.config.BaseEvaluationExporterConfig
    options:
      show_root_heading: true
      heading_level: 4

### EvaluationOrchestratorConfig

::: document_extraction_tools.config.EvaluationOrchestratorConfig
    options:
      show_root_heading: true
      heading_level: 4

## Creating Custom Configs

Subclass the base config to add your fields:

```python
from document_extraction_tools.config import BaseExtractorConfig

class MyExtractorConfig(BaseExtractorConfig):
    model_name: str
    temperature: float = 0.0
    max_tokens: int = 4096
    api_key: str | None = None
```

Then create the corresponding YAML file:

```yaml title="config/yaml/extractor.yaml"
model_name: "gpt-4"
temperature: 0.1
max_tokens: 8192
```
