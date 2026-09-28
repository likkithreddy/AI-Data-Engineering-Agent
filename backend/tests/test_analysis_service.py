from app.schemas.insight import InsightResult
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult
from app.services.analysis_service import analyze_question


def fake_tool_selector(question: str) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="sql",
        reasoning="The question asks for a structured revenue calculation.",
    )


def fake_revenue_generator(question: str) -> SQLGenerationResult:
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


def fake_insight_generator(
    question: str,
    selected_tools: list[str],
    sql_result: dict,
    pandas_result: dict,
    retrieved_documents: list[dict],
    observations: list[str],
    validation_errors: list[str],
    business_rules: str | None,
) -> InsightResult:
    return InsightResult(
        answer=(
            "Furniture generated the most recognized revenue, "
            "with revenue of 4539.67."
        ),
        evidence=[
            {
                "source_type": "sql",
                "source": "Revenue by product category query",
                "details": (
                    "Furniture: 4539.67; "
                    "Electronics: 3710.10; "
                    "Office Supplies: 240.00."
                ),
            }
        ],
        caveats=[],
    )


def test_analyze_question_without_gemini():
    result = analyze_question(
        "Which product category generated the most revenue?",
        sql_generator=fake_revenue_generator,
        tool_selector=fake_tool_selector,
        insight_generator=fake_insight_generator,
    )

    assert result.question == (
        "Which product category generated the most revenue?"
    )

    assert result.generated_sql
    assert result.reasoning

    assert result.execution.success is True
    assert result.execution.row_count == 3

    categories = {
        row["category"]: float(row["revenue"])
        for row in result.execution.rows
    }

    assert categories["Furniture"] == 4539.67
    assert categories["Electronics"] == 3710.10
    assert categories["Office Supplies"] == 240.00


def test_analyze_rejects_empty_question():
    try:
        analyze_question("")
    except ValueError as exc:
        assert str(exc) == "Question cannot be empty."
    else:
        raise AssertionError("Expected ValueError for empty question.")