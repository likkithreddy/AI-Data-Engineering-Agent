from app.agent.graph import (
    build_agent_graph,
    default_pandas_operation_selector,
    default_rag_retriever,
)
from app.llm.gemini import (
    generate_grounded_insight,
    generate_sql,
    select_tool,
)
from app.schemas.api import AnalysisResponse


def analyze_question(
    question: str,
    graph=None,
    sql_generator=generate_sql,
    tool_selector=select_tool,
    pandas_operation_selector=default_pandas_operation_selector,
    rag_retriever=default_rag_retriever,
    insight_generator=generate_grounded_insight,
) -> AnalysisResponse:
    question = question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    if graph is None:
        active_graph = build_agent_graph(
            sql_generator=sql_generator,
            tool_selector=tool_selector,
            pandas_operation_selector=pandas_operation_selector,
            rag_retriever=rag_retriever,
            insight_generator=insight_generator,
        )
    else:
        active_graph = graph

    result = active_graph.invoke(
        {
            "question": question,
        }
    )

    return AnalysisResponse(
        question=question,
        answer=result.get(
            "final_answer",
            "No grounded answer was generated.",
        ),
        request_id=None,
        execution_time_ms=None,
        retry_count=result.get(
            "retry_count",
            0,
        ),
        reasoning=result.get(
            "reasoning",
            "",
        ),
        selected_tools=result.get(
            "selected_tools",
            [],
        ),
        evidence=result.get(
            "evidence",
            [],
        ),
        caveats=result.get(
            "caveats",
            [],
        ),
        generated_sql=result.get(
            "generated_sql",
        ),
        execution=result.get(
            "sql_result",
        ),
        sql_result=result.get(
            "sql_result",
        ),
        pandas_operation=result.get(
            "pandas_operation",
        ),
        pandas_result=result.get(
            "pandas_result",
        ),
        retrieved_documents=result.get(
            "retrieved_documents",
            [],
        ),
        observations=result.get(
            "observations",
            [],
        ),
        validation_errors=result.get(
            "validation_errors",
            [],
        ),
    )


class AnalysisService:
    def __init__(
        self,
        graph=None,
        sql_generator=generate_sql,
        tool_selector=select_tool,
        pandas_operation_selector=default_pandas_operation_selector,
        rag_retriever=default_rag_retriever,
        insight_generator=generate_grounded_insight,
    ):
        self.graph = graph
        self.sql_generator = sql_generator
        self.tool_selector = tool_selector
        self.pandas_operation_selector = pandas_operation_selector
        self.rag_retriever = rag_retriever
        self.insight_generator = insight_generator

    def analyze(
        self,
        question: str,
    ) -> AnalysisResponse:
        return analyze_question(
            question=question,
            graph=self.graph,
            sql_generator=self.sql_generator,
            tool_selector=self.tool_selector,
            pandas_operation_selector=(
                self.pandas_operation_selector
            ),
            rag_retriever=self.rag_retriever,
            insight_generator=self.insight_generator,
        )