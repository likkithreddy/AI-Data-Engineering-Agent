from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    schema_context: str

    selected_tools: list[str]

    generated_sql: str
    reasoning: str

    sql_result: dict[str, Any]

    pandas_operation: dict[str, Any]
    pandas_result: dict[str, Any]

    retrieved_documents: list[dict[str, Any]]

    observations: list[str]
    validation_errors: list[str]
    execution_errors: list[str]

    retry_count: int

    final_answer: str
    evidence: list[dict[str, Any]]
    caveats: list[str]