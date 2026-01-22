"""Local test data loader for evaluations."""

import json
from pathlib import Path

from document_extraction_tools.base.test_data_loader.base_test_data_loader import (
    BaseTestDataLoader,
)
from document_extraction_tools.examples.simple_lease_extraction.config.test_data_loader_config import (
    TestDataLoaderConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.test_example import TestExample


class LocalTestDataLoader(BaseTestDataLoader[SimpleLeaseDetails]):
    """Loads evaluation examples from a JSON file."""

    def __init__(self, config: TestDataLoaderConfig) -> None:
        """Initialize with a local test data loader configuration.

        Args:
            config (TestDataLoaderConfig): Configuration for the local test data loader.
        """
        super().__init__(config)
        self.config = config

    def load_test_data(
        self, path_identifier: PathIdentifier
    ) -> list[TestExample[SimpleLeaseDetails]]:
        """Load test examples from a JSON file.

        Assumes the JSON file is an array of objects, each containing 'inputs' and 'expectations' fields.

        Args:
            path_identifier (PathIdentifier): Path to the JSON file containing test data.
        """
        input_path = Path(path_identifier.path)
        if not input_path.exists():
            raise FileNotFoundError(f"Test data not found: {input_path}")

        payload = json.loads(input_path.read_text())
        if not isinstance(payload, list):
            raise ValueError("Test data must be a JSON array.")

        examples: list[TestExample[SimpleLeaseDetails]] = []
        for entry in payload:
            if not isinstance(entry, dict):
                raise ValueError("Each test data entry must be an object.")

            inputs = entry.get("inputs") or {}
            expectations = entry.get("expectations")
            if expectations is None:
                raise ValueError("Missing expectations in test data entry.")

            doc_path = inputs.get("input_pdf_path")
            if doc_path is None:
                raise ValueError("Missing inputs.input_pdf_path in test data entry.")

            resolved_path = Path(doc_path)
            id = resolved_path.stem

            examples.append(
                TestExample(
                    id=id,
                    path_identifier=PathIdentifier(path=resolved_path),
                    true=SimpleLeaseDetails.model_validate(expectations),
                )
            )

        return examples
