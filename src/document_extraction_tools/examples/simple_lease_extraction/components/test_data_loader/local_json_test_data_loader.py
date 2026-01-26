"""Local test data loader for evaluations."""

import json
from pathlib import Path

import mlflow

from document_extraction_tools.base.test_data_loader.base_test_data_loader import (
    BaseTestDataLoader,
)
from document_extraction_tools.examples.simple_lease_extraction.config.local_json_test_data_loader_config import (
    LocalJSONTestDataLoaderConfig,
)
from document_extraction_tools.examples.simple_lease_extraction.schema.schema import (
    SimpleLeaseDetails,
)
from document_extraction_tools.types.path_identifier import PathIdentifier
from document_extraction_tools.types.test_example import TestExample


class LocalJSONTestDataLoader(BaseTestDataLoader[SimpleLeaseDetails]):
    """Loads evaluation examples from a JSON file."""

    def __init__(self, config: LocalJSONTestDataLoaderConfig) -> None:
        """Initialize with a local test data loader configuration."""
        super().__init__(config)
        self.config = config

    @mlflow.trace(name="load_test_data", span_type="RETRIEVER")
    def load_test_data(
        self, path_identifier: PathIdentifier
    ) -> list[TestExample[SimpleLeaseDetails]]:
        """Load test examples from a JSON file."""
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
            example_id = resolved_path.stem

            examples.append(
                TestExample(
                    id=example_id,
                    path_identifier=PathIdentifier(path=resolved_path),
                    true=SimpleLeaseDetails.model_validate(expectations),
                )
            )

        return examples
