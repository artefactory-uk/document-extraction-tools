"""Configuration Loader."""

import logging
from pathlib import Path
from typing import Any

import yaml

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.config.exporter_config import BaseExporterConfig
from document_extraction_tools.config.extractor_config import BaseExtractorConfig
from document_extraction_tools.config.file_lister_config import BaseFileListerConfig
from document_extraction_tools.config.orchestrator_config import OrchestratorConfig
from document_extraction_tools.config.pipeline_config import PipelineConfig
from document_extraction_tools.config.reader_config import BaseReaderConfig

logger = logging.getLogger(__name__)


def _load_yaml(path: Path) -> dict[str, Any]:
    """Helper to load a YAML file into a dictionary.

    Args:
        path (Path): Path to the .yaml file.

    Returns:
        dict[str, Any]: The parsed YAML data. Returns an empty dict if the file
        does not exist or is empty.
    """
    if not path.exists():
        return {}

    with open(path) as f:
        return yaml.safe_load(f) or {}


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

    loaded_components = {}

    for field, (filename, cls) in component_map.items():
        file_path = base_dir / filename
        data = _load_yaml(file_path)

        try:
            loaded_components[field] = cls(**data)
        except Exception as e:
            if not file_path.exists():
                raise FileNotFoundError(
                    f"Config file not found at '{file_path}' and the configuration "
                    f"class '{cls.__name__}' requires mandatory fields."
                ) from e
            raise e

    return PipelineConfig(**loaded_components)
