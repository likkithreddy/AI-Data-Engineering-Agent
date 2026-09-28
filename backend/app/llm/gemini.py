from typing import Any

from langchain_google_genai import ChatGoogleGenerativeAI

from app.agent.prompts import (
    GROUNDED_INSIGHT_SYSTEM_PROMPT,
    PANDAS_OPERATION_SYSTEM_PROMPT,
    SQL_GENERATION_SYSTEM_PROMPT,
    TOOL_SELECTION_SYSTEM_PROMPT,
)
from app.core.config import settings
from app.schemas.insight import InsightResult
from app.schemas.pandas import PandasOperation
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult
from app.tools.schema_tool import get_database_schema


def get_gemini_model() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key,
        temperature=0,
        max_retries=2,
    )


def select_tool(question: str) -> ToolSelectionResult:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    model = get_gemini_model().with_structured_output(
        ToolSelectionResult
    )

    messages = [
        ("system", TOOL_SELECTION_SYSTEM_PROMPT),
        (
            "human",
            f"""
User question:

{question}
""",
        ),
    ]

    result = model.invoke(messages)

    if not isinstance(result, ToolSelectionResult):
        raise TypeError(
            "Gemini returned an unexpected tool-selection output type."
        )

    return result


def generate_sql(
    question: str,
    schema_context: str | None = None,
) -> SQLGenerationResult:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if schema_context is None:
        schema_context = get_database_schema()

    model = get_gemini_model().with_structured_output(
        SQLGenerationResult
    )

    user_prompt = f"""
Database schema:

{schema_context}

Business rules:

- Recognized revenue only includes completed orders.
- Revenue = quantity * unit_price * (1 - discount).

User question:

{question}
"""

    messages = [
        ("system", SQL_GENERATION_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    result = model.invoke(messages)

    if not isinstance(result, SQLGenerationResult):
        raise TypeError(
            "Gemini returned an unexpected structured output type."
        )

    return result


def generate_pandas_operation(
    question: str,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> PandasOperation:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if not columns:
        raise ValueError("Columns cannot be empty.")

    model = get_gemini_model().with_structured_output(
        PandasOperation
    )

    sample_rows = rows[:10]

    user_prompt = f"""
Available columns:

{columns}

Sample rows:

{sample_rows}

User question:

{question}
"""

    messages = [
        ("system", PANDAS_OPERATION_SYSTEM_PROMPT),
        ("human", user_prompt),
    ]

    result = model.invoke(messages)

    if not isinstance(result, PandasOperation):
        raise TypeError(
            "Gemini returned an unexpected Pandas operation output type."
        )

    return result


def generate_grounded_insight(
    question: str,
    selected_tools: list[str],
    sql_result: dict[str, Any] | None = None,
    pandas_result: dict[str, Any] | None = None,
    retrieved_documents: list[dict[str, Any]] | None = None,
    observations: list[str] | None = None,
    validation_errors: list[str] | None = None,
    business_rules: str | None = None,
) -> InsightResult:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    sql_result = sql_result or {}
    pandas_result = pandas_result or {}
    retrieved_documents = retrieved_documents or []
    observations = observations or []
    validation_errors = validation_errors or []

    evidence_context = f"""
User question:

{question}

Selected tools:

{selected_tools}

SQL evidence:

{sql_result}

Pandas evidence:

{pandas_result}

Retrieved business documents:

{retrieved_documents}

Agent observations:

{observations}

Validation issues:

{validation_errors}

Business rules:

{business_rules or "No additional business rules supplied."}
"""

    model = get_gemini_model().with_structured_output(
        InsightResult
    )

    messages = [
        ("system", GROUNDED_INSIGHT_SYSTEM_PROMPT),
        ("human", evidence_context),
    ]

    result = model.invoke(messages)

    if not isinstance(result, InsightResult):
        raise TypeError(
            "Gemini returned an unexpected grounded insight output type."
        )

    return result