from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import (
    create_generate_sql_node,
    create_grounded_insight_node,
    create_pandas_operation_node,
    create_rag_node,
    create_select_tool_node,
    execute_pandas_node,
    execute_sql_node,
    inspect_sql_result,
    prepare_sql_retry,
    route_selected_tool,
    understand_question,
)
from app.agent.state import AgentState
from app.llm.gemini import (
    generate_grounded_insight,
    generate_pandas_operation,
    generate_sql,
    select_tool,
)
from app.schemas.insight import InsightResult
from app.schemas.pandas import PandasOperation
from app.schemas.rag import RAGSearchResult
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult
from app.tools.rag_tool import retrieve_business_documents


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
    [
        str,
        list[str],
        dict[str, Any],
        dict[str, Any],
        list[dict[str, Any]],
        list[str],
        list[str],
        str | None,
    ],
    InsightResult,
]


def default_pandas_operation_selector(
    question: str,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> PandasOperation:
    return generate_pandas_operation(
        question=question,
        columns=columns,
        rows=rows,
    )


def default_rag_retriever(
    question: str,
) -> RAGSearchResult:
    return retrieve_business_documents(question)


def default_insight_generator(
    question: str,
    selected_tools: list[str],
    sql_result: dict[str, Any],
    pandas_result: dict[str, Any],
    retrieved_documents: list[dict[str, Any]],
    observations: list[str],
    validation_errors: list[str],
    business_rules: str | None,
) -> InsightResult:
    return generate_grounded_insight(
        question=question,
        selected_tools=selected_tools,
        sql_result=sql_result,
        pandas_result=pandas_result,
        retrieved_documents=retrieved_documents,
        observations=observations,
        validation_errors=validation_errors,
        business_rules=business_rules,
    )


def route_after_sql_inspection(state: AgentState) -> str:
    sql_result = state.get("sql_result", {})
    selected_tools = state.get("selected_tools", [])

    sql_success = sql_result.get("success") is True

    # Pandas uses SQL to retrieve the data first.
    # Once SQL succeeds, route directly into Pandas.
    if sql_success and selected_tools:
        if selected_tools[0] == "pandas":
            return "pandas"

    # Normal SQL path.
    if (
        sql_success
        and not state.get("validation_errors")
    ):
        return "success"

    retry_count = state.get("retry_count", 0)

    if retry_count < 2:
        return "retry"

    return "failed"


def build_agent_graph(
    sql_generator=generate_sql,
    tool_selector=select_tool,
    pandas_operation_selector=default_pandas_operation_selector,
    rag_retriever=default_rag_retriever,
    insight_generator=None,
):
    graph = StateGraph(AgentState)

    graph.add_node(
        "understand_question",
        understand_question,
    )

    graph.add_node(
        "select_tool",
        create_select_tool_node(tool_selector),
    )

    graph.add_node(
        "generate_sql",
        create_generate_sql_node(sql_generator),
    )

    graph.add_node(
        "execute_sql",
        execute_sql_node,
    )

    graph.add_node(
        "inspect_sql_result",
        inspect_sql_result,
    )

    graph.add_node(
        "prepare_sql_retry",
        prepare_sql_retry,
    )

    graph.add_node(
        "generate_pandas_operation",
        create_pandas_operation_node(
            pandas_operation_selector
        ),
    )

    graph.add_node(
        "execute_pandas",
        execute_pandas_node,
    )

    graph.add_node(
        "retrieve_documents",
        create_rag_node(rag_retriever),
    )

    if insight_generator is not None:
        graph.add_node(
            "generate_insight",
            create_grounded_insight_node(
                insight_generator
            ),
        )

    # ---------------------------------------------------------
    # Main flow
    # ---------------------------------------------------------

    graph.add_edge(
        START,
        "understand_question",
    )

    graph.add_edge(
        "understand_question",
        "select_tool",
    )

    graph.add_conditional_edges(
        "select_tool",
        route_selected_tool,
        {
            "sql": "generate_sql",
            "pandas": "generate_sql",
            "rag": "retrieve_documents",
        },
    )

    # ---------------------------------------------------------
    # SQL flow
    # ---------------------------------------------------------

    graph.add_edge(
        "generate_sql",
        "execute_sql",
    )

    graph.add_edge(
        "execute_sql",
        "inspect_sql_result",
    )

    graph.add_conditional_edges(
        "inspect_sql_result",
        route_after_sql_inspection,
        {
            "retry": "prepare_sql_retry",
            "pandas": "generate_pandas_operation",
            "success": (
                "generate_insight"
                if insight_generator is not None
                else END
            ),
            "failed": END,
        },
    )

    graph.add_edge(
        "prepare_sql_retry",
        "generate_sql",
    )

    # ---------------------------------------------------------
    # IMPORTANT: Pandas flow
    # ---------------------------------------------------------

    graph.add_edge(
        "generate_pandas_operation",
        "execute_pandas",
    )

    if insight_generator is not None:
        graph.add_edge(
            "execute_pandas",
            "generate_insight",
        )
    else:
        graph.add_edge(
            "execute_pandas",
            END,
        )

    # ---------------------------------------------------------
    # RAG flow
    # ---------------------------------------------------------

    if insight_generator is not None:
        graph.add_edge(
            "retrieve_documents",
            "generate_insight",
        )

        graph.add_edge(
            "generate_insight",
            END,
        )
    else:
        graph.add_edge(
            "retrieve_documents",
            END,
        )

    return graph.compile()


agent_graph = build_agent_graph(
    insight_generator=default_insight_generator,
)