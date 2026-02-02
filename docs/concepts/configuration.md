# Configuration

Document Extraction Tools uses Pydantic models with YAML files for configuration.

## Configuration System

Each component has a matching base config class that you subclass to add your own fields.

### Base Config Classes

**Extraction Pipeline:**

- `BaseFileListerConfig`
- `BaseReaderConfig`
- `BaseConverterConfig`
- `BaseExtractorConfig`
- `BaseExtractionExporterConfig`
- `ExtractionOrchestratorConfig`

**Evaluation Pipeline:**

- `BaseTestDataLoaderConfig`
- `BaseEvaluatorConfig`
- `BaseEvaluationExporterConfig`
- `EvaluationOrchestratorConfig`

## Creating Custom Configs

Subclass the base config to add your specific fields:

```python
from document_extraction_tools.config import BaseExtractorConfig

class MyExtractorConfig(BaseExtractorConfig):
    model_name: str
    temperature: float = 0.0
    max_tokens: int = 4096
```

## YAML Files

Create YAML files in your config directory (default: `config/yaml/`):

### Default Filenames

| Config Class | Default Filename |
|--------------|------------------|
| FileListerConfig | `file_lister.yaml` |
| ReaderConfig | `reader.yaml` |
| ConverterConfig | `converter.yaml` |
| ExtractorConfig | `extractor.yaml` |
| ExtractionExporterConfig | `extraction_exporter.yaml` |
| ExtractionOrchestratorConfig | `extraction_orchestrator.yaml` |
| TestDataLoaderConfig | `test_data_loader.yaml` |
| EvaluatorConfig | `evaluator.yaml` |
| EvaluationExporterConfig | `evaluation_exporter.yaml` |
| EvaluationOrchestratorConfig | `evaluation_orchestrator.yaml` |

### Example YAML Files

```yaml title="config/yaml/extractor.yaml"
model_name: "gpt-4"
temperature: 0.0
max_tokens: 4096
```

```yaml title="config/yaml/extraction_orchestrator.yaml"
max_workers: 4
max_concurrency: 10
```

### Evaluator Config Format

Evaluator configs use a special format where the top-level key matches the config class name:

```yaml title="config/yaml/evaluator.yaml"
FieldAccuracyEvaluatorConfig:
  threshold: 0.8

LevenshteinEvaluatorConfig:
  normalize: true
```

## Loading Configuration

### Extraction Config

```python
from pathlib import Path
from document_extraction_tools.config import load_config, ExtractionOrchestratorConfig

config = load_config(
    lister_config_cls=MyFileListerConfig,
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    exporter_config_cls=MyExtractionExporterConfig,
    orchestrator_config_cls=ExtractionOrchestratorConfig,
    config_dir=Path("config/yaml"),
)

# Access individual configs
print(config.extractor.model_name)
print(config.orchestrator.max_workers)
```

### Evaluation Config

```python
from document_extraction_tools.config import load_evaluation_config

config = load_evaluation_config(
    test_data_loader_config_cls=MyTestDataLoaderConfig,
    evaluator_config_classes=[
        FieldAccuracyEvaluatorConfig,
        LevenshteinEvaluatorConfig,
    ],
    reader_config_cls=MyReaderConfig,
    converter_config_cls=MyConverterConfig,
    extractor_config_cls=MyExtractorConfig,
    evaluation_exporter_config_cls=MyEvaluationExporterConfig,
    orchestrator_config_cls=EvaluationOrchestratorConfig,
    config_dir=Path("config/yaml"),
)
```

## Environment Variables

You can use environment variables in YAML files with the `!env` tag (if you implement a custom YAML loader) or by using Pydantic's environment variable support in your config classes.
