"""Configuration for the local file lister."""

from pydantic import Field

from document_extraction_tools.config.base_file_lister_config import (
    BaseFileListerConfig,
)


class LocalFileListerConfig(BaseFileListerConfig):
    """Configuration for local file listing."""

    source_dir: str = Field(..., description="Directory to scan for input files.")
    extensions: list[str] = Field(
        default_factory=lambda: [".pdf"],
        description="File extensions to include.",
    )
