from typing import Any

from pydantic import BaseModel, Field

from app.tools.sql_tool import SQLExecutionResult


class AnalysisRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )


class AnalysisResponse(BaseModel):
    question: str

    answer: str

    reasoning: str = ""

    selected_tools: list[str] = Field(
        default_factory=list
    )

    evidence: list[dict[str, Any]] = Field(
        default_factory=list
    )

    caveats: list[str] = Field(
        default_factory=list
    )

    generated_sql: str | None = None

    execution: SQLExecutionResult | None = None

    sql_result: dict[str, Any] | None = None

    pandas_operation: dict[str, Any] | None = None

    pandas_result: dict[str, Any] | None = None

    retrieved_documents: list[dict[str, Any]] = Field(
        default_factory=list
    )

    observations: list[str] = Field(
        default_factory=list
    )

    validation_errors: list[str] = Field(
        default_factory=list
    )