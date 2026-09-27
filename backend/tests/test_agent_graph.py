from app.agent.graph import build_agent_graph
from app.schemas.pandas import PandasOperation
from app.schemas.rag import RAGSearchResult, RetrievedDocument
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult


def fake_sql_tool_selector(
    question: str,
) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="sql",
        reasoning="The question asks for structured business data.",
    )


def fake_pandas_tool_selector(
    question: str,
) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="pandas",
        reasoning="The question requires dataframe analysis.",
    )


def fake_rag_tool_selector(
    question: str,
) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="rag",
        reasoning="The question requires business documentation.",
    )


def fake_sql_generator(
    question: str,
    schema_context: str,
) -> SQLGenerationResult:
    assert schema_context

    return SQLGenerationResult(
        sql="""
            SELECT
                p.category,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount)
                ) AS revenue
            FROM order_items oi
            JOIN orders o
                ON o.id = oi.order_id
            JOIN products p
                ON p.id = oi.product_id
            WHERE o.status = 'completed'
            GROUP BY p.category
            ORDER BY revenue DESC
        """,
        reasoning="Calculate recognized revenue by product category.",
    )


def fake_pandas_operation_selector(
    question: str,
    columns: list[str],
    rows: list[dict],
) -> PandasOperation:
    assert "category" in columns
    assert "revenue" in columns
    assert rows

    return PandasOperation(
        operation="sort",
        column="revenue",
        ascending=False,
    )


def fake_rag_retriever(
    question: str,
) -> RAGSearchResult:
    return RAGSearchResult(
        query=question,
        documents=[
            RetrievedDocument(
                document_id="refund_policy",
                document=(
                    "Customers may request a refund within "
                    "30 days of purchase."
                ),
                distance=0.12,
                metadata={
                    "source": "refund_policy.txt",
                },
            )
        ],
    )


def retry_aware_sql_generator(
    question: str,
    schema_context: str,
) -> SQLGenerationResult:
    if "previous SQL attempt failed" in question:
        return SQLGenerationResult(
            sql="""
                SELECT
                    p.category,
                    SUM(
                        oi.quantity
                        * oi.unit_price
                        * (1 - oi.discount)
                    ) AS revenue
                FROM order_items oi
                JOIN orders o
                    ON o.id = oi.order_id
                JOIN products p
                    ON p.id = oi.product_id
                WHERE o.status = 'completed'
                GROUP BY p.category
                ORDER BY revenue DESC
            """,
            reasoning="Correct the failed SQL query.",
        )

    return SQLGenerationResult(
        sql="SELECT invalid_column FROM products",
        reasoning="Intentional failure for recovery testing.",
    )


def always_invalid_sql_generator(
    question: str,
    schema_context: str,
) -> SQLGenerationResult:
    return SQLGenerationResult(
        sql="SELECT invalid_column FROM products",
        reasoning="Intentional failure for retry testing.",
    )


def test_sql_agent_path():
    graph = build_agent_graph(
        tool_selector=fake_sql_tool_selector,
        sql_generator=fake_sql_generator,
    )

    result = graph.invoke(
        {
            "question": "Which product category generated the most revenue?"
        }
    )

    assert result["selected_tools"] == ["sql"]
    assert result["sql_result"]["success"] is True
    assert result["sql_result"]["row_count"] == 3

    categories = {
        row["category"]: float(row["revenue"])
        for row in result["sql_result"]["rows"]
    }

    assert categories["Furniture"] == 4539.67
    assert categories["Electronics"] == 3710.10
    assert categories["Office Supplies"] == 240.00


def test_pandas_agent_path():
    graph = build_agent_graph(
        tool_selector=fake_pandas_tool_selector,
        sql_generator=fake_sql_generator,
        pandas_operation_selector=fake_pandas_operation_selector,
    )

    result = graph.invoke(
        {
            "question": (
                "Sort the product categories by revenue."
            )
        }
    )

    assert result["selected_tools"] == ["pandas"]
    assert result["sql_result"]["success"] is True
    assert result["pandas_result"]["success"] is True

    assert result["pandas_result"]["rows"][0]["category"] == (
        "Furniture"
    )

    assert float(
    result["pandas_result"]["rows"][0]["revenue"]
    ) == 4539.67


def test_rag_agent_path():
    graph = build_agent_graph(
        tool_selector=fake_rag_tool_selector,
        sql_generator=fake_sql_generator,
        rag_retriever=fake_rag_retriever,
    )

    result = graph.invoke(
        {
            "question": "What is our refund policy?"
        }
    )

    assert result["selected_tools"] == ["rag"]

    documents = result["retrieved_documents"]

    assert len(documents) == 1
    assert documents[0]["document_id"] == "refund_policy"


def test_agent_recovers_from_failed_sql():
    graph = build_agent_graph(
        tool_selector=fake_sql_tool_selector,
        sql_generator=retry_aware_sql_generator,
    )

    result = graph.invoke(
        {
            "question": "Which product category generated the most revenue?"
        }
    )

    assert result["sql_result"]["success"] is True
    assert result["retry_count"] == 1


def test_agent_stops_after_maximum_retries():
    graph = build_agent_graph(
        tool_selector=fake_sql_tool_selector,
        sql_generator=always_invalid_sql_generator,
    )

    result = graph.invoke(
        {
            "question": "Which product category generated the most revenue?"
        }
    )

    assert result["sql_result"]["success"] is False
    assert result["retry_count"] == 2
    assert len(result["execution_errors"]) == 3


def test_agent_rejects_empty_question():
    graph = build_agent_graph(
        tool_selector=fake_sql_tool_selector,
        sql_generator=fake_sql_generator,
    )

    try:
        graph.invoke({"question": ""})
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty."
    else:
        raise AssertionError("Expected ValueError.")