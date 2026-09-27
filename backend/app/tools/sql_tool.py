from dataclasses import dataclass
from typing import Any

import pandas as pd
import sqlglot
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.engine import engine
from sqlglot import exp


@dataclass
class SQLValidationResult:
    valid: bool
    query: str
    error: str | None = None


@dataclass
class SQLExecutionResult:
    success: bool
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    error: str | None = None

MAX_RESULT_ROWS = 500
ALLOWED_ROOT_EXPRESSIONS = (
    exp.Select,
    
)


def validate_sql(query: str) -> SQLValidationResult:
    """Validate SQL before it is allowed to execute."""

    query = query.strip()

    if not query:
        return SQLValidationResult(
            valid=False,
            query=query,
            error="SQL query cannot be empty.",
        )

    try:
        statements = sqlglot.parse(
            query,
            read="postgres",
        )
    except sqlglot.errors.ParseError as exc:
        return SQLValidationResult(
            valid=False,
            query=query,
            error=f"SQL parsing failed: {exc}",
        )

    if len(statements) != 1:
        return SQLValidationResult(
            valid=False,
            query=query,
            error="Only one SQL statement is allowed.",
        )

    statement = statements[0]

    if not isinstance(statement, ALLOWED_ROOT_EXPRESSIONS):
        return SQLValidationResult(
            valid=False,
            query=query,
            error="Only SELECT statements are allowed.",
        )

    return SQLValidationResult(
        valid=True,
        query=query,
    )


def execute_sql(query: str) -> SQLExecutionResult:
    """Validate and execute a read-only SQL query."""
    validation = validate_sql(query)

    if not validation.valid:
        return SQLExecutionResult(
            success=False,
            columns=[],
            rows=[],
            row_count=0,
            error=validation.error,
        )

    try:
        with engine.connect() as connection:
            connection.execute(text("SET LOCAL statement_timeout = 5000"))

            result = connection.execute(text(validation.query))

            rows = result.mappings().fetchmany(MAX_RESULT_ROWS + 1)
            columns = list(result.keys())

        if len(rows) > MAX_RESULT_ROWS:
            return SQLExecutionResult(
                success=False,
                columns=columns,
                rows=[],
                row_count=0,
                error=(
                    f"Query returned more than {MAX_RESULT_ROWS} rows. "
                    "Please narrow the query."
                ),
            )

        dataframe = pd.DataFrame(rows, columns=columns)

        return SQLExecutionResult(
            success=True,
            columns=columns,
            rows=dataframe.to_dict(orient="records"),
            row_count=len(dataframe),
        )

    except SQLAlchemyError as exc:
        return SQLExecutionResult(
            success=False,
            columns=[],
            rows=[],
            row_count=0,
            error=f"Database execution failed: {exc}",
        )