from collections.abc import Callable
from inspect import Parameter, signature
from typing import Any

from app.agent.state import AgentState
from app.llm.gemini import select_tool
from app.schemas.insight import InsightResult
from app.schemas.pandas import PandasOperation
from app.schemas.rag import RAGSearchResult
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult
from app.tools.pandas_tool import (
    execute_pandas_operation,
    sql_rows_to_dataframe,
)
from app.tools.schema_tool import get_database_schema
from app.tools.sql_tool import execute_sql
from app.tools.validation_tool import (
    validate_pandas_operation_result,
    validate_tabular_result,
)


SQLGenerator = Callable[..., SQLGenerationResult]

ToolSelector = Callable[
    [str],
    ToolSelectionResult,
]

PandasOperationSelector = Callable[
    [str, list[str], list[dict[str, Any]]],
    PandasOperation,
]

RAGRetriever = Callable[
    [str],
    RAGSearchResult,
]

InsightGenerator = Callable[
    [str, list[str], dict[str, Any], dict[str, Any], list[dict[str, Any]],
     list[str], list[str], str | None],
    InsightResult,
]

MAX_SQL_RETRIES = 2


def understand_question(state: AgentState) -> AgentState:
    question = state.get("question", "").strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    schema_context = get_database_schema()

    return {
        "question": question,
        "schema_context": schema_context,
        "retry_count": 0,
        "observations": [
            "Question received and database schema loaded."
        ],
    }


def create_select_tool_node(
    tool_selector: ToolSelector,
) -> Callable[[AgentState], AgentState]:
    def select_tool_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        selection = tool_selector(question)

        observations = state.get("observations", [])

        return {
            "selected_tools": [selection.selected_tool],
            "observations": [
                *observations,
                (
                    f"Tool selected: {selection.selected_tool}. "
                    f"Reason: {selection.reasoning}"
                ),
            ],
        }

    return select_tool_node


def route_selected_tool(state: AgentState) -> str:
    selected_tools = state.get("selected_tools", [])

    if not selected_tools:
        return "sql"

    selected_tool = selected_tools[0]

    if selected_tool == "pandas":
        return "pandas"

    if selected_tool == "rag":
        return "rag"

    return "sql"


def _call_sql_generator(
    sql_generator: SQLGenerator,
    question: str,
    schema_context: str,
) -> SQLGenerationResult:
    """
    Support both production generators:

        generate_sql(question, schema_context)

    and lightweight test doubles:

        fake_generator(question)
    """

    try:
        parameters = signature(sql_generator).parameters.values()

        positional_parameters = [
            parameter
            for parameter in parameters
            if parameter.kind
            in (
                Parameter.POSITIONAL_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            )
        ]

        accepts_varargs = any(
            parameter.kind == Parameter.VAR_POSITIONAL
            for parameter in parameters
        )

        if accepts_varargs or len(positional_parameters) >= 2:
            return sql_generator(question, schema_context)

        return sql_generator(question)

    except (TypeError, ValueError):
        # Some callable objects do not expose an inspectable signature.
        # Fall back to the simple one-argument contract.
        return sql_generator(question)


def create_generate_sql_node(
    sql_generator: SQLGenerator,
) -> Callable[[AgentState], AgentState]:
    def generate_sql_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()
        schema_context = state.get("schema_context", "")

        if not question:
            raise ValueError("Question cannot be empty.")

        if not schema_context:
            raise ValueError(
                "Schema context is required for SQL generation."
            )

        execution_errors = state.get("execution_errors", [])
        retry_count = state.get("retry_count", 0)

        if execution_errors:
            error_context = "\n".join(
                execution_errors[-3:]
            )

            generation_question = (
                f"{question}\n\n"
                "The previous SQL attempt failed. "
                "Generate a corrected SQL query.\n\n"
                f"Previous execution error:\n"
                f"{error_context}"
            )
        else:
            generation_question = question

        generation = _call_sql_generator(
            sql_generator,
            generation_question,
            schema_context,
        )

        observations = state.get("observations", [])

        if execution_errors:
            observation = (
                f"SQL regenerated after retry {retry_count}."
            )
        else:
            observation = "SQL generated successfully."

        return {
            "generated_sql": generation.sql,
            "reasoning": generation.reasoning,
            "observations": [
                *observations,
                observation,
            ],
        }

    return generate_sql_node


def execute_sql_node(state: AgentState) -> AgentState:
    generated_sql = state.get("generated_sql", "").strip()

    if not generated_sql:
        raise ValueError(
            "Generated SQL is required before execution."
        )

    execution = execute_sql(generated_sql)

    sql_result: dict[str, Any] = {
        "success": execution.success,
        "columns": execution.columns,
        "rows": execution.rows,
        "row_count": execution.row_count,
        "error": execution.error,
    }

    observations = state.get("observations", [])

    if execution.success:
        return {
            "sql_result": sql_result,
            "observations": [
                *observations,
                "SQL executed successfully.",
            ],
        }

    execution_errors = state.get("execution_errors", [])

    error_message = execution.error or "SQL execution failed."

    return {
        "sql_result": sql_result,
        "execution_errors": [
            *execution_errors,
            error_message,
        ],
        "observations": [
            *observations,
            "SQL execution failed.",
        ],
    }


def inspect_sql_result(state: AgentState) -> AgentState:
    sql_result = state.get("sql_result", {})

    validation = validate_tabular_result(
        columns=sql_result.get("columns", []),
        rows=sql_result.get("rows", []),
        row_count=sql_result.get("row_count", 0),
    )

    observations = state.get("observations", [])

    if validation.valid and sql_result.get("success"):
        return {
            "validation_errors": [],
            "observations": [
                *observations,
                (
                    "SQL result validated successfully: "
                    f"{sql_result.get('row_count', 0)} rows."
                ),
            ],
        }

    errors = [
        *state.get("validation_errors", []),
        *validation.errors,
    ]

    if not sql_result.get("success"):
        errors.append(
            "SQL result inspection found an execution failure."
        )

    return {
        "validation_errors": errors,
        "observations": [
            *observations,
            "SQL result inspection found an invalid result.",
        ],
    }


def create_pandas_operation_node(
    operation_selector: PandasOperationSelector,
) -> Callable[[AgentState], AgentState]:
    def pandas_operation_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()
        sql_result = state.get("sql_result", {})

        if not sql_result.get("success"):
            raise ValueError(
                "A successful SQL result is required before Pandas analysis."
            )

        rows = sql_result.get("rows", [])
        columns = sql_result.get("columns", [])

        operation = operation_selector(
            question,
            columns,
            rows,
        )

        return {
            "pandas_operation": operation.model_dump(),
            "observations": [
                *state.get("observations", []),
                (
                    "Pandas operation selected: "
                    f"{operation.operation}."
                ),
            ],
        }

    return pandas_operation_node


def execute_pandas_node(state: AgentState) -> AgentState:
    sql_result = state.get("sql_result", {})
    operation = state.get("pandas_operation", {})

    if not sql_result.get("success"):
        raise ValueError(
            "Successful SQL results are required for Pandas analysis."
        )

    dataframe = sql_rows_to_dataframe(
        sql_result.get("rows", [])
    )

    result = execute_pandas_operation(
        dataframe,
        operation,
    )

    pandas_result: dict[str, Any] = {
        "success": result.success,
        "operation": result.operation,
        "columns": result.columns,
        "rows": result.rows,
        "row_count": result.row_count,
        "error": result.error,
    }

    if not result.success:
        return {
            "pandas_result": pandas_result,
            "execution_errors": [
                *state.get("execution_errors", []),
                result.error or "Pandas execution failed.",
            ],
            "observations": [
                *state.get("observations", []),
                "Pandas execution failed.",
            ],
        }

    validation = validate_pandas_operation_result(
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
    )

    if not validation.valid:
        return {
            "pandas_result": pandas_result,
            "validation_errors": [
                *state.get("validation_errors", []),
                *validation.errors,
            ],
            "observations": [
                *state.get("observations", []),
                "Pandas result validation failed.",
            ],
        }

    return {
        "pandas_result": pandas_result,
        "observations": [
            *state.get("observations", []),
            (
                "Pandas operation executed and validated successfully: "
                f"{result.row_count} rows."
            ),
        ],
    }


def create_rag_node(
    retriever: RAGRetriever,
) -> Callable[[AgentState], AgentState]:
    def rag_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        result = retriever(question)

        documents = [
            {
                "document_id": document.document_id,
                "document": document.document,
                "distance": document.distance,
                "metadata": document.metadata,
            }
            for document in result.documents
        ]

        observations = state.get("observations", [])

        if not documents:
            return {
                "retrieved_documents": [],
                "validation_errors": [
                    *state.get("validation_errors", []),
                    "RAG returned no relevant documents.",
                ],
                "observations": [
                    *observations,
                    "RAG retrieval returned no documents.",
                ],
            }

        return {
            "retrieved_documents": documents,
            "observations": [
                *observations,
                (
                    "RAG retrieval completed successfully: "
                    f"{len(documents)} document(s)."
                ),
            ],
        }

    return rag_node


def create_grounded_insight_node(
    insight_generator: InsightGenerator,
) -> Callable[[AgentState], AgentState]:
    def grounded_insight_node(state: AgentState) -> AgentState:
        question = state.get("question", "").strip()

        if not question:
            raise ValueError("Question cannot be empty.")

        result = insight_generator(
            question,
            state.get("selected_tools", []),
            state.get("sql_result", {}),
            state.get("pandas_result", {}),
            state.get("retrieved_documents", []),
            state.get("observations", []),
            state.get("validation_errors", []),
            (
                "Recognized revenue only includes completed orders. "
                "Revenue = quantity * unit_price * (1 - discount)."
            ),
        )

        return {
            "final_answer": result.answer,
            "evidence": [
                evidence.model_dump()
                for evidence in result.evidence
            ],
            "caveats": result.caveats,
            "observations": [
                *state.get("observations", []),
                "Grounded business insight generated successfully.",
            ],
        }

    return grounded_insight_node


def prepare_sql_retry(state: AgentState) -> AgentState:
    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_SQL_RETRIES:
        return {
            "observations": [
                *state.get("observations", []),
                "Maximum SQL retry limit reached.",
            ],
        }

    return {
        "retry_count": retry_count + 1,
        "observations": [
            *state.get("observations", []),
            f"Preparing SQL retry {retry_count + 1}.",
        ],
    }


def should_retry_sql(state: AgentState) -> str:
    sql_result = state.get("sql_result", {})

    if (
        sql_result.get("success")
        and not state.get("validation_errors")
    ):
        selected_tools = state.get("selected_tools", [])

        if selected_tools and selected_tools[0] == "pandas":
            return "pandas"

        return "end"

    retry_count = state.get("retry_count", 0)

    if retry_count >= MAX_SQL_RETRIES:
        return "end"

    return "retry"