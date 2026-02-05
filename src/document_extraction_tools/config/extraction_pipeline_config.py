"""Master Extraction Pipeline Configuration."""

from pydantic import BaseModel, Field

from document_extraction_tools.config.base_converter_config import BaseConverterConfig
from document_extraction_tools.config.base_extraction_exporter_config import (
    BaseExtractionExporterConfig,
)
from document_extraction_tools.config.base_extractor_config import BaseExtractorConfig
from document_extraction_tools.config.base_file_lister_config import (
    BaseFileListerConfig,
)
from document_extraction_tools.config.base_reader_config import BaseReaderConfig
from document_extraction_tools.config.extraction_orchestrator_config import (
    ExtractionOrchestratorConfig,
)


class ExtractionPipelineConfig(BaseModel):
    """Master container for extraction pipeline component configurations.

    This class aggregates the configurations for all pipeline components.
    """

    orchestrator: ExtractionOrchestratorConfig = Field(
        ..., description="Configuration for orchestrating extraction execution."
    )

    file_lister: BaseFileListerConfig = Field(
        ..., description="Configuration for file discovery."
    )

    reader: BaseReaderConfig = Field(
        ..., description="Configuration for reading raw document bytes."
    )

    converter: BaseConverterConfig = Field(
        ..., description="Configuration for converting raw bytes into documents."
    )

    extractor: BaseExtractorConfig = Field(
        ..., description="Configuration for extracting structured data."
    )

    exporter: BaseExtractionExporterConfig = Field(
        ..., description="Configuration for exporting extracted data."
    )
