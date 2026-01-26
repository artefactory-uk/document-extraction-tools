"""Field comparison helper used by example evaluators."""

import os
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class LlmJudgeResult(BaseModel):
    """Structured response for equality judgment."""

    is_equal: bool = Field(..., description="Whether the values are equivalent.")


def get_llm_judge_client() -> genai.Client:
    """Initialize and return a Gemini LLM client."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Set GEMINI_API_KEY in the environment.")
    return genai.Client(api_key=api_key)


def invoke_llm_as_a_judge(
    true_value: Any,  # noqa: ANN401
    pred_value: Any,  # noqa: ANN401
    client: genai.Client,
    model_name: str,
    prompt_template: str,
) -> bool:
    """Return True when two field values should be considered equal."""
    prompt = prompt_template.format(
        true_value=true_value,
        pred_value=pred_value,
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LlmJudgeResult,
        ),
    )

    return response.parsed.is_equal
