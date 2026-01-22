"""Configuration Loader."""

import logging
from pathlib import Path
from typing import Any

import yaml

from document_extraction_tools.config.converter_config import BaseConverterConfig
from document_extraction_tools.config.evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.config.extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.config.extraction_orchestrator_config import (
    ExtractionOrchestratorConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)
from document_extraction_tools.config.extractor_config import BaseExtractorConfig
from document_extraction_tools.config.file_lister_config import BaseFileListerConfig
from document_extraction_tools.config.reader_config import BaseReaderConfig
from document_extraction_tools.config.test_data_loader_config import (
    BaseTestDataLoaderConfig,
)

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
    orchestrator_cls: type[ExtractionOrchestratorConfig] = ExtractionOrchestratorConfig,
    lister_cls: type[BaseFileListerConfig] = BaseFileListerConfig,
    reader_cls: type[BaseReaderConfig] = BaseReaderConfig,
    converter_cls: type[BaseConverterConfig] = BaseConverterConfig,
    extractor_cls: type[BaseExtractorConfig] = BaseExtractorConfig,
    exporter_cls: type[BaseExtractionExporterConfig] = BaseExtractionExporterConfig,
) -> ExtractionPipelineConfig:
    """Loads configuration based on a mapping file.

    Args:
        config_dir (str): Directory containing the configs.
        orchestrator_cls (type[ExtractionOrchestratorConfig]): The ExtractionOrchestratorConfig subclass to use.
        lister_cls (type[BaseFileListerConfig]): The FileListerConfig subclass to use.
        reader_cls (type[BaseReaderConfig]): The ReaderConfig subclass to use.
        converter_cls (type[BaseConverterConfig]): The ConverterConfig subclass to use.
        extractor_cls (type[BaseExtractorConfig]): The ExtractorConfig subclass to use.
        exporter_cls (type[BaseExtractionExporterConfig]): The ExporterConfig subclass to use.

    Returns:
        ExtractionPipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    return ExtractionPipelineConfig(
        orchestrator=orchestrator_cls(
            **_load_yaml(base_dir / orchestrator_cls.filename)
        ),
        file_lister=lister_cls(**_load_yaml(base_dir / lister_cls.filename)),
        reader=reader_cls(**_load_yaml(base_dir / reader_cls.filename)),
        converter=converter_cls(**_load_yaml(base_dir / converter_cls.filename)),
        extractor=extractor_cls(**_load_yaml(base_dir / extractor_cls.filename)),
        exporter=exporter_cls(**_load_yaml(base_dir / exporter_cls.filename)),
    )


def load_evaluation_config(
    config_dir: str = "config",
    orchestrator_cls: type[EvaluationOrchestratorConfig] = EvaluationOrchestratorConfig,
    test_data_loader_cls: type[BaseTestDataLoaderConfig] = BaseTestDataLoaderConfig,
    reader_cls: type[BaseReaderConfig] = BaseReaderConfig,
    converter_cls: type[BaseConverterConfig] = BaseConverterConfig,
    extractor_cls: type[BaseExtractorConfig] = BaseExtractorConfig,
    evaluation_exporter_cls: type[
        BaseEvaluationExporterConfig
    ] = BaseEvaluationExporterConfig,
) -> EvaluationPipelineConfig:
    """Loads evaluation configuration based on default filenames.

    Args:
        config_dir (str): Directory containing the configs.
        orchestrator_cls (type[EvaluationOrchestratorConfig]): The EvaluationOrchestratorConfig subclass to use.
        test_data_loader_cls (type[BaseTestDataLoaderConfig]): The TestDataLoaderConfig subclass to use.
        reader_cls (type[BaseReaderConfig]): The ReaderConfig subclass to use.
        converter_cls (type[BaseConverterConfig]): The ConverterConfig subclass to use.
        extractor_cls (type[BaseExtractorConfig]): The ExtractorConfig subclass to use.
        evaluation_exporter_cls (type[BaseEvaluationExporterConfig]): The EvaluationExporterConfig subclass to use.

    Returns:
        EvaluationPipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    return EvaluationPipelineConfig(
        orchestrator=orchestrator_cls(
            **_load_yaml(base_dir / orchestrator_cls.filename)
        ),
        test_data_loader=test_data_loader_cls(
            **_load_yaml(base_dir / test_data_loader_cls.filename)
        ),
        reader=reader_cls(**_load_yaml(base_dir / reader_cls.filename)),
        converter=converter_cls(**_load_yaml(base_dir / converter_cls.filename)),
        extractor=extractor_cls(**_load_yaml(base_dir / extractor_cls.filename)),
        evaluation_exporter=evaluation_exporter_cls(
            **_load_yaml(base_dir / evaluation_exporter_cls.filename)
        ),
    )
