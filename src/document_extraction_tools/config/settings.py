"""Base Configuration Schemas.

These models define the configuration parameters strictly required by the
Abstract Base Classes in the library. Implementations should subclass these
models to add their specific parameters.
"""

from pydantic import BaseModel, Field

from document_extraction_tools.types.path_identifier import PathIdentifier


class BaseOrchestratorConfig(BaseModel):
    """Configuration for the Pipeline Orchestrator."""

    max_workers: int = Field(
        default=4, description="Number of processes to use for CPU-bound tasks."
    )
    max_concurrency: int = Field(
        default=10, description="Maximum number of concurrent I/O requests."
    )


class BaseExporterConfig(BaseModel):
    """Configuration for the Exporter."""

    destination: PathIdentifier = Field(
        ..., description="The root destination for exports."
    )


class BaseFileListerConfig(BaseModel):
    """Base config for File Listers."""

    pass


class BaseReaderConfig(BaseModel):
    """Base config for Readers."""

    pass


class BaseConverterConfig(BaseModel):
    """Base config for Converters."""

    pass


class BaseExtractorConfig(BaseModel):
    """Base config for Extractors."""

    pass


class PipelineConfig(BaseModel):
    """Master container for component configurations."""

    orchestrator: BaseOrchestratorConfig
    file_lister: BaseFileListerConfig
    reader: BaseReaderConfig
    converter: BaseConverterConfig
    extractor: BaseExtractorConfig
    exporter: BaseExporterConfig
