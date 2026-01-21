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

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path.absolute()}")

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
    """Loads configuration based on a mapping file.

    It first reads the mapping file to determine which YAML file corresponds
    to which pipeline component. Then it loads those files.

    Args:
        config_dir: Directory containing the configs.
        mapping_file: The YAML file that maps component keys to filenames.
        orchestrator_cls: The OrchestratorConfig subclass to use.
        lister_cls: The FileListerConfig subclass to use.
        reader_cls: The ReaderConfig subclass to use.
        converter_cls: The ConverterConfig subclass to use.
        extractor_cls: The ExtractorConfig subclass to use.
        exporter_cls: The ExporterConfig subclass to use.

    Returns:
        PipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    return PipelineConfig(
        orchestrator=orchestrator_cls(
            **_load_yaml(base_dir / orchestrator_cls.filename)
        ),
        file_lister=lister_cls(**_load_yaml(base_dir / lister_cls.filename)),
        reader=reader_cls(**_load_yaml(base_dir / reader_cls.filename)),
        converter=converter_cls(**_load_yaml(base_dir / converter_cls.filename)),
        extractor=extractor_cls(**_load_yaml(base_dir / extractor_cls.filename)),
        exporter=exporter_cls(**_load_yaml(base_dir / exporter_cls.filename)),
    )
