"""Local file lister implementation for the example pipeline."""

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
        if not self.source_dir.exists():
            raise FileNotFoundError(
                f"Source directory {self.source_dir} does not exist."
            )

        files: list[PathIdentifier] = []
        for ext in self.extensions:
            pattern = f"**/*{ext}"
            files.extend(
                PathIdentifier(path=path)
                for path in self.source_dir.glob(pattern, case_sensitive=False)
            )
        return files
