"""Tests for config loader utilities."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from document_extraction_tools.config import (
    BaseConverterConfig,
    BaseEvaluationExporterConfig,
    BaseEvaluatorConfig,
    BaseExtractionExporterConfig,
    BaseExtractorConfig,
    BaseFileListerConfig,
    BaseReaderConfig,
    BaseTestDataLoaderConfig,
    _load_evaluator_configs,
    _load_yaml,
    load_config,
    load_evaluation_config,
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


class DummyEvaluatorConfig(BaseEvaluatorConfig):
    """Config placeholder for evaluator tests."""


def _write_yaml(path: Path, data: dict | None) -> None:
    """Write YAML content to disk for test setup."""
    path.write_text(yaml.safe_dump(data))


def test_load_yaml_missing_raises(tmp_path: Path) -> None:
    """Raise when the YAML file does not exist."""
    with pytest.raises(FileNotFoundError):
        _load_yaml(tmp_path / "missing.yaml")


def test_load_yaml_empty_returns_empty_dict(tmp_path: Path) -> None:
    """Return an empty dict when the YAML file is empty."""
    target = tmp_path / "empty.yaml"
    target.write_text("")
    assert _load_yaml(target) == {}


def test_load_config_builds_pipeline_config(tmp_path: Path) -> None:
    """Build an extraction pipeline config from per-component YAML files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    _write_yaml(
        config_dir / ExtractionOrchestratorConfig.filename,
        {"max_workers": 2, "max_concurrency": 3},
    )
    _write_yaml(config_dir / BaseFileListerConfig.filename, {})
    _write_yaml(config_dir / BaseReaderConfig.filename, {})
    _write_yaml(config_dir / BaseConverterConfig.filename, {})
    _write_yaml(config_dir / BaseExtractorConfig.filename, {})
    _write_yaml(config_dir / BaseExtractionExporterConfig.filename, {})

    config = load_config(
        lister_config_cls=BaseFileListerConfig,
        reader_config_cls=BaseReaderConfig,
        converter_config_cls=BaseConverterConfig,
        extractor_config_cls=BaseExtractorConfig,
        exporter_config_cls=BaseExtractionExporterConfig,
        config_dir=config_dir,
    )

    assert isinstance(config, ExtractionPipelineConfig)
    assert config.orchestrator.max_workers == 2
    assert config.orchestrator.max_concurrency == 3
    assert isinstance(config.file_lister, BaseFileListerConfig)


def test_load_config_missing_dir_raises(tmp_path: Path) -> None:
    """Raise when the config directory is missing."""
    missing_dir = tmp_path / "missing"
    with pytest.raises(FileNotFoundError):
        load_config(
            lister_config_cls=BaseFileListerConfig,
            reader_config_cls=BaseReaderConfig,
            converter_config_cls=BaseConverterConfig,
            extractor_config_cls=BaseExtractorConfig,
            exporter_config_cls=BaseExtractionExporterConfig,
            config_dir=missing_dir,
        )


def test_load_evaluation_config_builds_pipeline_config(tmp_path: Path) -> None:
    """Build an evaluation pipeline config from per-component YAML files."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()

    _write_yaml(
        config_dir / EvaluationOrchestratorConfig.filename,
        {"max_workers": 5, "max_concurrency": 6},
    )
    _write_yaml(config_dir / BaseTestDataLoaderConfig.filename, {})
    _write_yaml(config_dir / BaseReaderConfig.filename, {})
    _write_yaml(config_dir / BaseConverterConfig.filename, {})
    _write_yaml(config_dir / BaseExtractorConfig.filename, {})
    _write_yaml(config_dir / BaseEvaluationExporterConfig.filename, {})
    _write_yaml(
        config_dir / BaseEvaluatorConfig.filename,
        {DummyEvaluatorConfig.__name__: {}},
    )

    config = load_evaluation_config(
        test_data_loader_config_cls=BaseTestDataLoaderConfig,
        evaluator_config_classes=[DummyEvaluatorConfig],
        reader_config_cls=BaseReaderConfig,
        converter_config_cls=BaseConverterConfig,
        extractor_config_cls=BaseExtractorConfig,
        evaluation_exporter_config_cls=BaseEvaluationExporterConfig,
        config_dir=config_dir,
    )

    assert isinstance(config, EvaluationPipelineConfig)
    assert config.orchestrator.max_workers == 5
    assert config.orchestrator.max_concurrency == 6
    assert len(config.evaluators) == 1
    assert isinstance(config.evaluators[0], DummyEvaluatorConfig)


def test_load_evaluator_configs_requires_mapping(tmp_path: Path) -> None:
    """Raise when evaluator.yaml is not a mapping."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / BaseEvaluatorConfig.filename).write_text("- not-a-mapping")

    with pytest.raises(
        ValueError, match="Expected evaluator.yaml to contain a mapping"
    ):
        _load_evaluator_configs(config_dir, [DummyEvaluatorConfig])


def test_load_evaluator_configs_missing_yaml_raises(tmp_path: Path) -> None:
    """Raise when evaluator.yaml is missing or empty."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / BaseEvaluatorConfig.filename).write_text("")

    with pytest.raises(ValueError, match="No evaluator configuration found"):
        _load_evaluator_configs(config_dir, [DummyEvaluatorConfig])


def test_load_evaluator_configs_unknown_class_raises(tmp_path: Path) -> None:
    """Raise when evaluator.yaml references an unknown config class."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _write_yaml(
        config_dir / BaseEvaluatorConfig.filename,
        {"UnknownEvaluatorConfig": {}},
    )

    with pytest.raises(ValueError, match="Unknown evaluator config class"):
        _load_evaluator_configs(config_dir, [DummyEvaluatorConfig])


def test_load_evaluator_configs_requires_mapping_per_evaluator(tmp_path: Path) -> None:
    """Raise when an evaluator entry is not a mapping."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _write_yaml(
        config_dir / BaseEvaluatorConfig.filename,
        {DummyEvaluatorConfig.__name__: ["not-a-mapping"]},
    )

    with pytest.raises(ValueError, match="Expected evaluator data"):
        _load_evaluator_configs(config_dir, [DummyEvaluatorConfig])


def test_load_evaluator_configs_allows_none_config(tmp_path: Path) -> None:
    """Allow evaluator entries with null config values."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    _write_yaml(
        config_dir / BaseEvaluatorConfig.filename,
        {DummyEvaluatorConfig.__name__: None},
    )

    evaluators = _load_evaluator_configs(config_dir, [DummyEvaluatorConfig])

    assert len(evaluators) == 1
    assert isinstance(evaluators[0], DummyEvaluatorConfig)
