"""Gemini extractor implementation using image data for the example pipeline."""

import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

from document_extraction_tools.base.extractor.extractor import BaseExtractor
from document_extraction_tools.examples.simple_lease_extraction.config.extractor_config import (
    ExtractorConfig,
)
from document_extraction_tools.types.document import Document, ImageData


class GeminiImageExtractor(BaseExtractor):
    """Extracts lease data from images using the Gemini API."""

    def __init__(self, config: ExtractorConfig) -> None:
        """Initialize the extractor and client."""
        super().__init__(config)

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Set GEMINI_API_KEY in the environment.")

        self.client = genai.Client(api_key=api_key)
        self.model_name = config.model_name

    async def extract(self, document: Document, schema: type[BaseModel]) -> BaseModel:
        """Run extraction against the Gemini API."""
        contents = []

        # 1. Add Text Prompt
        contents.append("Extract data from this lease document.")

        # 2. Add Images
        for page in document.pages:
            if isinstance(page.data, ImageData):
                contents.append(
                    types.Part.from_bytes(
                        data=page.data.content, mime_type="image/jpeg"
                    )
                )

        # 3. Call Gemini API
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
            ),
        )

        return response.parsed
