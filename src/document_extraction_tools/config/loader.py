"""Configuration Loader."""

import logging
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

from .settings import (
    BaseConverterConfig,
    BaseExporterConfig,
    BaseExtractorConfig,
    BaseFileListerConfig,
    BaseOrchestratorConfig,
    BaseReaderConfig,
    PipelineConfig,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def _load_yaml(path: Path, model_class: type[T]) -> T:
    """Helper to load a YAML file into a specific Pydantic model."""
    if not path.exists():
        try:
            return model_class()
        except Exception:
            raise FileNotFoundError(f"Missing required config file: {path}")

    with open(path) as f:
        data = yaml.safe_load(f) or {}

    return model_class(**data)


def load_config(
    config_dir: str = "config",
    orchestrator_cls: type[BaseOrchestratorConfig] = BaseOrchestratorConfig,
    lister_cls: type[BaseFileListerConfig] = BaseFileListerConfig,
    reader_cls: type[BaseReaderConfig] = BaseReaderConfig,
    converter_cls: type[BaseConverterConfig] = BaseConverterConfig,
    extractor_cls: type[BaseExtractorConfig] = BaseExtractorConfig,
    exporter_cls: type[BaseExporterConfig] = BaseExporterConfig,
) -> PipelineConfig:
    """Loads configuration from a directory of YAML files.

    Allows injecting custom configuration subclasses for specific implementations.

    Args:
        config_dir: Directory containing the .yaml files.
        orchestrator_cls: The Pydantic model class for orchestrator config.
        lister_cls: The Pydantic model class for file lister config.
        reader_cls: The Pydantic model class for reader config.
        converter_cls: The Pydantic model class for converter config.
        extractor_cls: The Pydantic model class for extractor config.
        exporter_cls: The Pydantic model class for exporter config.

    Returns:
        PipelineConfig: Aggregated config object containing instances of the passed classes.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    return PipelineConfig(
        orchestrator=_load_yaml(base_dir / "orchestrator.yaml", orchestrator_cls),
        file_lister=_load_yaml(base_dir / "lister.yaml", lister_cls),
        reader=_load_yaml(base_dir / "reader.yaml", reader_cls),
        converter=_load_yaml(base_dir / "converter.yaml", converter_cls),
        extractor=_load_yaml(base_dir / "extractor.yaml", extractor_cls),
        exporter=_load_yaml(base_dir / "exporter.yaml", exporter_cls),
    )
