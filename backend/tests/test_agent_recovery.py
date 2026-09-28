from app.agent.graph import build_agent_graph
from app.schemas.insight import InsightResult
from app.schemas.sql_generation import SQLGenerationResult
from app.schemas.tool_selection import ToolSelectionResult


def fake_tool_selector(question: str) -> ToolSelectionResult:
    return ToolSelectionResult(
        selected_tool="sql",
        reasoning="The question requires structured database analysis.",
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
        answer="The recovered SQL query executed successfully.",
        evidence=[
            {
                "source_type": "sql",
                "source": "Recovered SQL execution",
                "details": "The retry produced a successful SQL result.",
            }
        ],
        caveats=[],
    )


def test_agent_recovers_after_sql_execution_failure():
    attempts = []

    def fake_sql_generator(
        question: str,
        schema_context: str,
    ) -> SQLGenerationResult:
        attempts.append(question)

        if len(attempts) == 1:
            return SQLGenerationResult(
                sql="SELECT * FROM table_that_does_not_exist",
                reasoning="Intentional failing SQL for retry testing.",
            )

        return SQLGenerationResult(
            sql="SELECT 1 AS recovery_check",
            reasoning="Corrected SQL after the previous execution failure.",
        )

    graph = build_agent_graph(
        sql_generator=fake_sql_generator,
        tool_selector=fake_tool_selector,
        insight_generator=fake_insight_generator,
    )

    result = graph.invoke(
        {
            "question": "Test SQL recovery behavior.",
        }
    )

    assert len(attempts) == 2

    assert result["retry_count"] == 1

    assert result["generated_sql"] == "SELECT 1 AS recovery_check"

    assert result["sql_result"]["success"] is True

    assert result["sql_result"]["row_count"] == 1

    assert result["sql_result"]["rows"] == [
        {"recovery_check": 1}
    ]

    assert (
        result["final_answer"]
        == "The recovered SQL query executed successfully."
    )

    assert any(
        "retry" in observation.lower()
        for observation in result.get("observations", [])
    )


def test_agent_stops_after_maximum_sql_retries():
    attempts = []

    def always_failing_sql_generator(
        question: str,
        schema_context: str,
    ) -> SQLGenerationResult:
        attempts.append(question)

        return SQLGenerationResult(
            sql="SELECT * FROM table_that_does_not_exist",
            reasoning="Intentional failing SQL for retry-limit testing.",
        )

    graph = build_agent_graph(
        sql_generator=always_failing_sql_generator,
        tool_selector=fake_tool_selector,
        insight_generator=fake_insight_generator,
    )

    result = graph.invoke(
        {
            "question": "Test SQL retry limit.",
        }
    )

    # Initial attempt + two retries.
    assert len(attempts) == 3

    # The graph stops after the configured maximum retry count.
    assert result["retry_count"] == 2

    # The final SQL execution still failed.
    assert result["sql_result"]["success"] is False

    # No grounded insight should be generated after exhausting retries.
    assert "final_answer" not in result

    # The execution failure should be preserved for diagnostics.
    assert result["execution_errors"]

    assert any(
        "retry" in observation.lower()
        for observation in result.get("observations", [])
    )