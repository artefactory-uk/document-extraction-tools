"""Local file lister implementation for the example pipeline."""

import os
from pathlib import Path

from document_extraction_tools.base.file_lister.file_lister import BaseFileLister
from document_extraction_tools.examples.simple_lease_extraction.config.file_lister_config import (
    FileListerConfig,
)
from document_extraction_tools.types.path_identifier import PathIdentifier


class LocalFileLister(BaseFileLister):
    """Lists files from a local directory based on configured extensions."""

    def __init__(self, config: FileListerConfig) -> None:
        """Initialize the lister with example config."""
        super().__init__(config)
        self.source_dir = Path(config.source_dir)
        self.extensions = [ext.lower() for ext in config.extensions]

    def list_files(self) -> list[PathIdentifier]:
        """Return PathIdentifier entries for matching files."""
        files: list[PathIdentifier] = []
        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"Source directory {self.source_dir} does not exist."
            )

        for root, _, filenames in os.walk(self.source_dir):
            for name in filenames:
                if any(name.lower().endswith(ext) for ext in self.extensions):
                    full_path = Path(root) / name
                    files.append(PathIdentifier(path=str(full_path)))
        return files
