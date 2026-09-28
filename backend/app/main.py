import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.analysis import router as analysis_router
from app.api.routes.health import router as health_router


logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
)


app = FastAPI(
    title="AI Data Engineering Agent",
    description=(
        "Autonomous business data analysis using LangGraph, "
        "PostgreSQL, Pandas, RAG, and Gemini."
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=(
        r"https?://"
        r"(localhost|"
        r"127\.0\.0\.1|"
        r"0\.0\.0\.0|"
        r"192\.168\.\d+\.\d+|"
        r"10\.\d+\.\d+\.\d+|"
        r"172\.(1[6-9]|2\d|3[0-1])\.\d+\.\d+)"
        r":\d+"
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    health_router,
)

app.include_router(
    analysis_router,
)