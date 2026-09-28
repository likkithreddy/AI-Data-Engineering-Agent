from app.agent.state import AgentState


def test_agent_state_accepts_initial_question():
    state: AgentState = {
        "question": "Which category generated the most revenue?"
    }

    assert state["question"] == (
        "Which category generated the most revenue?"
    )


def test_agent_state_supports_analysis_fields():
    state: AgentState = {
        "question": "Which category generated the most revenue?",
        "schema_context": "Table: products",
        "selected_tools": ["sql"],
        "generated_sql": "SELECT 1",
        "retry_count": 0,
        "observations": [],
        "validation_errors": [],
        "execution_errors": [],
        "evidence": [],
    }

    assert state["selected_tools"] == ["sql"]
    assert state["retry_count"] == 0
    assert state["generated_sql"] == "SELECT 1"
    