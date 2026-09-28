from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]


def validate_tabular_result(
    columns: list[str],
    rows: list[dict[str, Any]],
    row_count: int,
    max_rows: int = 500,
) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    if row_count < 0:
        errors.append("Row count cannot be negative.")

    if row_count != len(rows):
        errors.append(
            "Row count does not match the number of returned rows."
        )

    if row_count > max_rows:
        errors.append(
            f"Result contains more than {max_rows} rows."
        )

    if not columns and rows:
        errors.append(
            "Rows were returned without column metadata."
        )

    expected_columns = set(columns)

    for index, row in enumerate(rows):
        row_columns = set(row.keys())

        if row_columns != expected_columns:
            errors.append(
                f"Row {index} columns do not match result columns."
            )

    if row_count == 0:
        warnings.append("Result contains no rows.")

    null_counts = {
        column: sum(
            row.get(column) is None
            for row in rows
        )
        for column in columns
    }

    for column, null_count in null_counts.items():
        if null_count > 0:
            warnings.append(
                f"Column '{column}' contains "
                f"{null_count} null value(s)."
            )

    return ValidationResult(
        valid=not errors,
        errors=errors,
        warnings=warnings,
    )


def validate_pandas_operation_result(
    columns: list[str],
    rows: list[dict[str, Any]],
    row_count: int,
) -> ValidationResult:
    return validate_tabular_result(
        columns=columns,
        rows=rows,
        row_count=row_count,
    )