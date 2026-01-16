"""Configuration Loader."""

import logging
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.config.exporter_config import BaseExporterConfig
from document_extraction_tools.config.extractor_config import BaseExtractorConfig
from document_extraction_tools.config.file_lister_config import BaseFileListerConfig
from document_extraction_tools.config.orchestrator_config import OrchestratorConfig
from document_extraction_tools.config.pipeline_config import PipelineConfig
from document_extraction_tools.config.reader_config import BaseReaderConfig

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _load_yaml(path: Path, model_class: type[T]) -> T:
    """Helper to load a YAML file into a specific Pydantic model.

    Args:
        path (Path): Path to the .yaml file.
        model_class (type[T]): The Pydantic model class to validate against.

    Returns:
        T: An instance of the model class populated with data.

    Raises:
        FileNotFoundError: If the file is missing and the model has required fields.
    """
    if not path.exists():
        try:
            return model_class()
        except Exception:
            raise FileNotFoundError(
                f"Config file not found at '{path}' and the configuration "
                f"class '{model_class.__name__}' requires mandatory fields."
            )

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return model_class(**data)


def load_config(
    config_dir: str = "config",
    orchestrator_cls: type[OrchestratorConfig] = OrchestratorConfig,
    lister_cls: type[BaseFileListerConfig] = BaseFileListerConfig,
    reader_cls: type[BaseReaderConfig] = BaseReaderConfig,
    converter_cls: type[BaseConverterConfig] = BaseConverterConfig,
    extractor_cls: type[BaseExtractorConfig] = BaseExtractorConfig,
    exporter_cls: type[BaseExporterConfig] = BaseExporterConfig,
) -> PipelineConfig:
    """Loads configuration from a directory of YAML files.

    This function allows dependency injection of configuration classes.
    You can pass subclasses of the Base configs to validate extra fields
    present in your implementation-specific YAMLs.

    Args:
        config_dir: Directory containing the .yaml files.
        orchestrator_cls: The class to use for orchestrator config.
        lister_cls: The class to use for file lister config.
        reader_cls: The class to use for reader config.
        converter_cls: The class to use for converter config.
        extractor_cls: The class to use for extractor config.
        exporter_cls: The class to use for exporter config.

    Returns:
        PipelineConfig: Aggregated config object containing instances of the passed classes.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    component_map = {
        "orchestrator": ("orchestrator.yaml", orchestrator_cls),
        "file_lister": ("lister.yaml", lister_cls),
        "reader": ("reader.yaml", reader_cls),
        "converter": ("converter.yaml", converter_cls),
        "extractor": ("extractor.yaml", extractor_cls),
        "exporter": ("exporter.yaml", exporter_cls),
    }

    loaded_components = {
        field: _load_yaml(base_dir / filename, cls)
        for field, (filename, cls) in component_map.items()
    }

    return PipelineConfig(**loaded_components)
