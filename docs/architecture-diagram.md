# Architecture diagram

```mermaid
flowchart TD
    User[Business user / UI] --> API[FastAPI /analysis endpoint]
    API --> Graph[LangGraph Agent]

    Graph --> Understand[understand_question]
    Understand --> Schema[Load database schema]
    Schema --> Select[select_tool]

    Select --> Route{Tool selected?}

    Route -->|sql| SQLGen[generate_sql]
    Route -->|pandas| SQLGen
    Route -->|rag| RAG[retrieve_documents]

    SQLGen --> ExecSQL[execute_sql]
    ExecSQL --> Inspect[inspect_sql_result]
    Inspect --> Validate{Valid and successful?}
    Validate -->|No| Retry[prepare_sql_retry]
    Retry --> SQLGen
    Validate -->|Yes| Insight{Need Pandas follow-up?}

    Insight -->|Yes| PandasGen[generate_pandas_operation]
    PandasGen --> PandasExec[execute_pandas]
    PandasExec --> PandasValidate{Pandas result valid?}
    PandasValidate -->|No| Errors[validation_errors]
    PandasValidate -->|Yes| InsightAssembler[generate_insight]

    RAG --> Docs[Relevant business docs]
    Docs --> InsightAssembler

    Validate -->|Yes and no Pandas follow-up| InsightAssembler
    InsightAssembler --> Answer[Grounded final answer + evidence + caveats]
    Answer --> UI

    subgraph DataLayer[Data and retrieval layer]
        DB[(PostgreSQL / business data)]
        Vector[(ChromaDB / policy documents)]
        LLM[(Gemini API)]
    end

    SQLGen -. uses schema .-> DB
    ExecSQL -. reads from .-> DB
    RAG -. vector search .-> Vector
    Select -. LLM tool routing .-> LLM
    SQLGen -. LLM SQL generation .-> LLM
    PandasGen -. LLM Pandas operation planning .-> LLM
    InsightAssembler -. grounded synthesis .-> LLM
```

## Flow summary

The graph begins with question understanding and route selection. The SQL path is the default path for structured business data. If the result requires more transformation, the agent moves into the Pandas branch. If the question depends on business policy or process documentation, the graph takes the RAG branch. The final insight node synthesizes all evidence into a concise business answer.
