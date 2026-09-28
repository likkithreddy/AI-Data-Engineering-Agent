# AI Data Engineering Agent

An end-to-end business intelligence assistant that turns natural-language questions into grounded, evidence-backed answers using SQL, Pandas analysis, and document retrieval.

The backend is built with FastAPI and LangGraph, and it uses Google Gemini for tool routing, SQL generation, and insight synthesis. The application reads from a PostgreSQL database, performs follow-up dataframe analysis when needed, and consults business policy documents in a Chroma vector store before answering.

## What the project does

This project helps business users ask questions like:

- "What is our recognized revenue by product category?"
- "Which customers have the highest lifetime value?"
- "What is the refund policy for delayed returns?"
- "Which orders are still pending, and how much revenue is at risk?"

Instead of manually writing SQL or hunting through policy docs, the agent chooses the best tool for the job:

- SQL for structured database questions
- Pandas for post-query aggregation and transformations
- RAG for policy and process documents
- Gemini-generated grounding to explain the answer with evidence and caveats

## Architecture

The system is organized into four major components:

1. Frontend UI
   - A Vite + React application that sends questions to the backend API.
2. FastAPI backend
   - Exposes the `/analysis` endpoint.
   - Orchestrates the agent run and returns structured evidence.
3. LangGraph agent
   - Routes the user question to the right tool.
   - Executes SQL and/or Pandas operations.
   - Retrieves relevant policy documents when the answer depends on business rules.
   - Produces a grounded final answer.
4. Data and retrieval layer
   - PostgreSQL stores transactional business data.
   - ChromaDB stores business documentation for semantic retrieval.
   - Google Gemini supplies model reasoning and structured output generation.

## Core workflow

The agent follows this lifecycle:

1. Receive a question from the UI or API.
2. Load the database schema and identify the best tool.
3. Generate a safe SQL query.
4. Execute the query against PostgreSQL.
5. Validate the result.
6. If additional analysis is required, generate a Pandas operation and analyze the result.
7. If the question depends on policy or business documentation, retrieve matching documents.
8. Generate a grounded business insight with evidence and caveats.

## Features

- Natural-language business question answering
- Tool selection with LangGraph routing
- Safe SQL generation using schema-aware prompts
- Result validation and SQL retry logic
- Pandas-based downstream analysis for grouped or derived metrics
- Document retrieval for business policy questions
- Structured evidence output with answer, SQL, results, and caveats
- FastAPI API and React front end
- Database seeding scripts and document ingestion scripts

## Project structure

```text
.
├── README.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── llm/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tools/
│   │   └── main.py
│   ├── scripts/
│   ├── requirements.txt
│   ├── .env.example
│   └── .venv/
├── data/
│   └── documents/
├── docker/
├── docs/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── scripts/
```

## Setup

### 1. Create the environment file

Copy the example environment file:

```bash
cp backend/.env.example backend/.env
```

Then update the values in `backend/.env`:

- `DATABASE_URL` for your PostgreSQL instance
- `GEMINI_API_KEY` from your Google AI project
- `GEMINI_MODEL` if you want to override the default

### 2. Install backend dependencies

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Prepare the database

```bash
cd backend
python scripts/init_database.py
python scripts/seed_database.py
```

### 4. Ingest business documents for RAG

```bash
cd backend
python scripts/ingest_documents.py
```

### 5. Start the backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API is available at:

- http://localhost:8000/docs
- http://localhost:8000/health

### 6. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

## Example API requests

### Structured SQL question

```bash
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the recognized revenue by product category for completed orders?"
  }'
```

### Follow-up Pandas question

```bash
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which customer segment has the highest average order value?"
  }'
```

### Policy / documentation question

```bash
curl -X POST http://localhost:8000/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the refund policy for delayed returns?"
  }'
```

## Example queries the agent handles well

- "What is total recognized revenue for completed orders?"
- "Which products sold the most units last quarter?"
- "Show me the top 5 customers by revenue."
- "Which countries have the highest average order size?"
- "What are the business rules around refunds and revenue recognition?"
- "Which orders are pending and still require action?"

## Notes

- The agent intentionally prefers safe, read-only SQL.
- Validation ensures generated SQL and Pandas outputs are structurally reasonable.
- The final answer is grounded in the evidence from the database, analysis, and retrieved documents instead of generic model output alone.
- The project is designed for business-data analysis use cases where both structured and policy-based evidence matter.

## Useful commands

```bash
# backend tests
cd backend
pytest

# optional linting
ruff check app
```
