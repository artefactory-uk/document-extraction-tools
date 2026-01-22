"""Master Extraction Pipeline Configuration."""

from pydantic import BaseModel

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

    orchestrator: ExtractionOrchestratorConfig
    file_lister: BaseFileListerConfig
    reader: BaseReaderConfig
    converter: BaseConverterConfig
    extractor: BaseExtractorConfig
    exporter: BaseExtractionExporterConfig
