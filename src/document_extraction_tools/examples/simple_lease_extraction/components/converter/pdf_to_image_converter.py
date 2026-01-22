"""PDF-to-image converter implementation for the example pipeline."""

import io
from pathlib import Path

from pdf2image import convert_from_bytes  # type: ignore

from document_extraction_tools.base.converter.base_converter import BaseConverter
from document_extraction_tools.examples.simple_lease_extraction.config.pdf_to_image_converter_config import (
    PDFToImageConverterConfig,
)
from document_extraction_tools.types.document import Document, ImageData, Page
from document_extraction_tools.types.document_bytes import DocumentBytes


class PDFToImageConverter(BaseConverter):
    """Converts PDF bytes into image pages."""

    def __init__(self, config: PDFToImageConverterConfig) -> None:
        """Initialize converter with example config."""
        super().__init__(config)
        self.dpi = config.dpi
        self.image_format = config.format

    def convert(self, document_bytes: DocumentBytes) -> Document:
        """Convert raw PDF bytes into a Document with image pages."""
        pil_images = convert_from_bytes(
            document_bytes.file_bytes, dpi=self.dpi, fmt=self.image_format
        )

        pages = []
        for i, img in enumerate(pil_images):
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format=self.image_format.upper())

            pages.append(
                Page(
                    page_number=i + 1,
                    data=ImageData(
                        content=img_byte_arr.getvalue(),
                    ),
                )
            )

        file_path = Path(document_bytes.path_identifier.path)

        return Document(
            id=file_path.stem,
            content_type="image",
            path_identifier=document_bytes.path_identifier,
            pages=pages,
        )
