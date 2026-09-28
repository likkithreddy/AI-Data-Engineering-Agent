from app.agent.graph import build_agent_graph
from app.schemas.insight import EvidenceItem, InsightResult
from app.schemas.pandas import PandasOperation
from app.schemas.rag import RAGSearchResult, RetrievedDocument
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult


def fake_sql_generator(
    question: str,
    schema_context: str,
) -> SQLGenerationResult:
    return SQLGenerationResult(
        sql="""
            SELECT
                p.category,
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount)
                ) AS revenue
            FROM products p
            JOIN order_items oi
                ON oi.product_id = p.id
            JOIN orders o
                ON o.id = oi.order_id
            WHERE o.status = 'completed'
            GROUP BY p.category
            ORDER BY revenue DESC
        """,
        reasoning="Calculate completed-order revenue by category.",
    )


def fake_sql_tool_selector(
    question: str,
) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="sql",
        reasoning="The question requires structured business data.",
    )


def fake_pandas_tool_selector(
    question: str,
) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="pandas",
        reasoning="The question requires dataframe analysis.",
    )


def fake_pandas_operation_selector(
    question: str,
    columns: list[str],
    rows: list[dict],
) -> PandasOperation:
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
                document="Customers may request a refund within 30 days.",
                distance=0.1,
                metadata={"source": "refund_policy.txt"},
            )
        ],
    )


def fake_insight_generator(
    question,
    selected_tools,
    sql_result,
    pandas_result,
    retrieved_documents,
    observations,
    validation_errors,
    business_rules,
) -> InsightResult:
    if sql_result and sql_result.get("rows"):
        return InsightResult(
            answer="Furniture generated the highest recognized revenue.",
            evidence=[
                EvidenceItem(
                    source_type="sql",
                    source="Completed-order revenue query",
                    details=(
                        "The validated SQL result contains Furniture "
                        "as the highest-revenue category."
                    ),
                )
            ],
            caveats=[],
        )

    if retrieved_documents:
        return InsightResult(
            answer="Customers may request refunds within 30 days.",
            evidence=[
                EvidenceItem(
                    source_type="rag",
                    source="refund_policy.txt",
                    details=(
                        "The retrieved refund policy states that "
                        "customers may request a refund within 30 days."
                    ),
                )
            ],
            caveats=[],
        )

    return InsightResult(
        answer="No sufficient evidence was available.",
        evidence=[],
        caveats=["The available evidence was insufficient."],
    )


def test_sql_path_generates_grounded_insight():
    graph = build_agent_graph(
        tool_selector=fake_sql_tool_selector,
        sql_generator=fake_sql_generator,
        insight_generator=fake_insight_generator,
    )

    result = graph.invoke(
        {
            "question": "Which category generated the most revenue?"
        }
    )

    assert result["final_answer"]
    assert result["evidence"]
    assert result["evidence"][0]["source_type"] == "sql"


def test_pandas_path_generates_grounded_insight():
    graph = build_agent_graph(
        tool_selector=fake_pandas_tool_selector,
        sql_generator=fake_sql_generator,
        pandas_operation_selector=fake_pandas_operation_selector,
        insight_generator=fake_insight_generator,
    )

    result = graph.invoke(
        {
            "question": "Sort categories by revenue."
        }
    )

    assert result["pandas_result"]["success"] is True
    assert result["final_answer"]
    assert result["evidence"]


def test_rag_path_generates_grounded_insight():
    graph = build_agent_graph(
        tool_selector=lambda question: ToolSelectionResult(
            selected_tool="rag",
            reasoning="The question requires business policy documentation.",
        ),
        rag_retriever=fake_rag_retriever,
        insight_generator=fake_insight_generator,
    )

    result = graph.invoke(
        {
            "question": "What is the refund policy?"
        }
    )

    assert result["retrieved_documents"]
    assert result["final_answer"]
    assert result["evidence"][0]["source_type"] == "rag"