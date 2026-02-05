"""Configuration Loader."""

from pathlib import Path
from typing import Any

import yaml

from document_extraction_tools.config.base_converter_config import BaseConverterConfig
from document_extraction_tools.config.base_evaluation_exporter_config import (
    BaseEvaluationExporterConfig,
)
from document_extraction_tools.config.base_evaluator_config import BaseEvaluatorConfig
from document_extraction_tools.config.base_extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.config.base_extractor_config import BaseExtractorConfig
from document_extraction_tools.config.base_file_lister_config import (
    BaseFileListerConfig,
)
from document_extraction_tools.config.base_reader_config import BaseReaderConfig
from document_extraction_tools.config.base_test_data_loader_config import (
    BaseTestDataLoaderConfig,
)
from document_extraction_tools.config.evaluation_orchestrator_config import (
    EvaluationOrchestratorConfig,
)
from document_extraction_tools.config.evaluation_pipeline_config import (
    EvaluationPipelineConfig,
)
from document_extraction_tools.config.extraction_orchestrator_config import (
    ExtractionOrchestratorConfig,
)
from document_extraction_tools.config.extraction_pipeline_config import (
    ExtractionPipelineConfig,
)


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


def load_extraction_config(
    lister_config_cls: type[BaseFileListerConfig],
    reader_config_cls: type[BaseReaderConfig],
    converter_config_cls: type[BaseConverterConfig],
    extractor_config_cls: type[BaseExtractorConfig],
    extraction_exporter_config_cls: type[BaseExtractionExporterConfig],
    extraction_orchestrator_config_cls: type[
        ExtractionOrchestratorConfig
    ] = ExtractionOrchestratorConfig,
    config_dir: Path = Path("config/yaml"),
) -> ExtractionPipelineConfig:
    """Loads extraction configuration based on component filenames.

    Args:
        lister_config_cls (type[BaseFileListerConfig]): The FileListerConfig subclass to use.
        reader_config_cls (type[BaseReaderConfig]): The ReaderConfig subclass to use.
        converter_config_cls (type[BaseConverterConfig]): The ConverterConfig subclass to use.
        extractor_config_cls (type[BaseExtractorConfig]): The ExtractorConfig subclass to use.
        extraction_exporter_config_cls (type[BaseExtractionExporterConfig]): The
            ExtractionExporterConfig subclass to use.
        extraction_orchestrator_config_cls (type[ExtractionOrchestratorConfig]): The
            ExtractionOrchestratorConfig class to use.
        config_dir (Path): Directory containing the configs.

    Returns:
        ExtractionPipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    if not config_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {config_dir.absolute()}")

    return ExtractionPipelineConfig(
        extraction_orchestrator=extraction_orchestrator_config_cls(
            **_load_yaml(config_dir / extraction_orchestrator_config_cls.filename)
        ),
        file_lister=lister_config_cls(
            **_load_yaml(config_dir / lister_config_cls.filename)
        ),
        reader=reader_config_cls(**_load_yaml(config_dir / reader_config_cls.filename)),
        converter=converter_config_cls(
            **_load_yaml(config_dir / converter_config_cls.filename)
        ),
        extractor=extractor_config_cls(
            **_load_yaml(config_dir / extractor_config_cls.filename)
        ),
        extraction_exporter=extraction_exporter_config_cls(
            **_load_yaml(config_dir / extraction_exporter_config_cls.filename)
        ),
    )


def load_evaluation_config(
    test_data_loader_config_cls: type[BaseTestDataLoaderConfig],
    evaluator_config_classes: list[type[BaseEvaluatorConfig]],
    reader_config_cls: type[BaseReaderConfig],
    converter_config_cls: type[BaseConverterConfig],
    extractor_config_cls: type[BaseExtractorConfig],
    evaluation_exporter_config_cls: type[BaseEvaluationExporterConfig],
    evaluation_orchestrator_config_cls: type[
        EvaluationOrchestratorConfig
    ] = EvaluationOrchestratorConfig,
    config_dir: Path = Path("config/yaml"),
) -> EvaluationPipelineConfig:
    """Loads evaluation configuration based on component filenames.

    Args:
        test_data_loader_config_cls (type[BaseTestDataLoaderConfig]): The TestDataLoaderConfig subclass to use.
        evaluator_config_classes (list[type[BaseEvaluatorConfig]]): EvaluatorConfig
            subclasses to load using the top-level keys in evaluator.yaml.
        reader_config_cls (type[BaseReaderConfig]): The ReaderConfig subclass to use.
        converter_config_cls (type[BaseConverterConfig]): The ConverterConfig subclass to use.
        extractor_config_cls (type[BaseExtractorConfig]): The ExtractorConfig subclass to use.
        evaluation_exporter_config_cls (type[BaseEvaluationExporterConfig]): The EvaluationExporterConfig
            subclass to use.
        evaluation_orchestrator_config_cls (type[EvaluationOrchestratorConfig]): The
            EvaluationOrchestratorConfig class to use.
        config_dir (Path): Directory containing the configs.

    Returns:
        EvaluationPipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    if not config_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {config_dir.absolute()}")

    return EvaluationPipelineConfig(
        evaluation_orchestrator=evaluation_orchestrator_config_cls(
            **_load_yaml(config_dir / evaluation_orchestrator_config_cls.filename)
        ),
        test_data_loader=test_data_loader_config_cls(
            **_load_yaml(config_dir / test_data_loader_config_cls.filename)
        ),
        evaluators=_load_evaluator_configs(config_dir, evaluator_config_classes),
        reader=reader_config_cls(**_load_yaml(config_dir / reader_config_cls.filename)),
        converter=converter_config_cls(
            **_load_yaml(config_dir / converter_config_cls.filename)
        ),
        extractor=extractor_config_cls(
            **_load_yaml(config_dir / extractor_config_cls.filename)
        ),
        evaluation_exporter=evaluation_exporter_config_cls(
            **_load_yaml(config_dir / evaluation_exporter_config_cls.filename)
        ),
    )


def _load_evaluator_configs(
    config_dir: Path, evaluator_config_classes: list[type[BaseEvaluatorConfig]]
) -> list[BaseEvaluatorConfig]:
    """Helper to load multiple evaluator configs from evaluator.yaml.

    Args:
        config_dir (Path): Directory containing the configs.
        evaluator_config_classes (list[type[BaseEvaluatorConfig]]): EvaluatorConfig
            subclasses keyed by their class names.

    Returns:
        list[BaseEvaluatorConfig]: The loaded evaluator configurations.
    """
    evaluator_lookup = {cls.__name__: cls for cls in evaluator_config_classes}
    evaluator_yaml = _load_yaml(config_dir / BaseEvaluatorConfig.filename)
    if not evaluator_yaml:
        raise ValueError("No evaluator configuration found in evaluator.yaml.")
    if not isinstance(evaluator_yaml, dict):
        raise ValueError(
            "Expected evaluator.yaml to contain a mapping of config class names."
        )

    evaluators: list[BaseEvaluatorConfig] = []
    for evaluator_key, evaluator_data in evaluator_yaml.items():
        evaluator_cls = evaluator_lookup.get(evaluator_key)
        if evaluator_cls is None:
            raise ValueError(
                f"Unknown evaluator config class '{evaluator_key}' in evaluator.yaml."
            )
        if evaluator_data is None:
            evaluator_data = {}
        if not isinstance(evaluator_data, dict):
            raise ValueError(
                f"Expected evaluator data for '{evaluator_key}' to be a mapping."
            )
        evaluators.append(evaluator_cls(**evaluator_data))
    return evaluators
