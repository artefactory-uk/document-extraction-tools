"""Configuration Loader."""

import logging
from pathlib import Path
from typing import Any

import yaml

from document_extraction_tools.config.pipeline_config import PipelineConfig

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
    config_dir: str = "config", mapping_file: str = "config_file_mapping.yaml"
) -> PipelineConfig:
    """Loads configuration based on a mapping file.

    It first reads the mapping file to determine which YAML file corresponds
    to which pipeline component. Then it loads those files.

    Args:
        config_dir: Directory containing the configs.
        mapping_file: The YAML file that maps component keys to filenames.

    Returns:
        PipelineConfig: The fully validated configuration.

    Raises:
        FileNotFoundError: If the config directory or mapping file is missing.
    """
    base_dir = Path(config_dir)
    if not base_dir.exists():
        raise FileNotFoundError(f"Config directory not found: {base_dir.absolute()}")

    mapping_path = base_dir / mapping_file
    if not mapping_path.exists():
        raise FileNotFoundError(
            f"Mapping file '{mapping_file}' not found in {base_dir.absolute()}. "
            "This file is required to map components to their config files."
        )

    file_mapping = _load_yaml(mapping_path)
    loaded_data = {}

    for field, filename in file_mapping.items():
        file_path = base_dir / filename
        loaded_data[field] = _load_yaml(file_path)

    return PipelineConfig(**loaded_data)
