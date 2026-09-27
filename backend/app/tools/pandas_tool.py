from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import pandas as pd


PandasOperationName = Literal[
    "group_by",
    "aggregate",
    "sort",
    "describe",
    "calculate_percentage_change",
    "detect_missing_values",
]


@dataclass
class PandasExecutionResult:
    success: bool
    operation: str
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    error: str | None = None


MAX_RESULT_ROWS = 500


def sql_rows_to_dataframe(
    rows: list[dict[str, Any]],
) -> pd.DataFrame:
    return pd.DataFrame(rows)


def _validate_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> None:
    missing_columns = [
        column
        for column in columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Columns not found in dataframe: {missing_columns}"
        )


def _execute_group_by(
    dataframe: pd.DataFrame,
    operation: dict[str, Any],
) -> pd.DataFrame:
    group_columns = operation.get("group_columns", [])
    aggregations = operation.get("aggregations", {})

    if not group_columns:
        raise ValueError(
            "group_columns is required for group_by."
        )

    if not aggregations:
        raise ValueError(
            "aggregations is required for group_by."
        )

    _validate_columns(dataframe, group_columns)
    _validate_columns(
        dataframe,
        list(aggregations.keys()),
    )

    allowed_aggregations = {
        "sum",
        "mean",
        "min",
        "max",
        "count",
    }

    for aggregation in aggregations.values():
        if aggregation not in allowed_aggregations:
            raise ValueError(
                f"Unsupported aggregation: {aggregation}"
            )

    return (
        dataframe
        .groupby(group_columns, dropna=False)
        .agg(aggregations)
        .reset_index()
    )


def _execute_aggregate(
    dataframe: pd.DataFrame,
    operation: dict[str, Any],
) -> pd.DataFrame:
    aggregations = operation.get("aggregations", {})

    if not aggregations:
        raise ValueError(
            "aggregations is required for aggregate."
        )

    _validate_columns(
        dataframe,
        list(aggregations.keys()),
    )

    allowed_aggregations = {
        "sum",
        "mean",
        "min",
        "max",
        "count",
    }

    for aggregation in aggregations.values():
        if aggregation not in allowed_aggregations:
            raise ValueError(
                f"Unsupported aggregation: {aggregation}"
            )

    return dataframe.agg(aggregations).to_frame().T


def _execute_sort(
    dataframe: pd.DataFrame,
    operation: dict[str, Any],
) -> pd.DataFrame:
    column = operation.get("column")
    ascending = operation.get("ascending", False)

    if not column:
        raise ValueError("column is required for sort.")

    _validate_columns(dataframe, [column])

    if not isinstance(ascending, bool):
        raise ValueError("ascending must be a boolean.")

    return dataframe.sort_values(
        by=column,
        ascending=ascending,
    )


def _execute_describe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    return (
        dataframe
        .describe(include="all")
        .transpose()
        .reset_index(names="column")
    )


def _execute_percentage_change(
    dataframe: pd.DataFrame,
    operation: dict[str, Any],
) -> pd.DataFrame:
    column = operation.get("column")

    if not column:
        raise ValueError(
            "column is required for calculate_percentage_change."
        )

    _validate_columns(dataframe, [column])

    values = pd.to_numeric(
        dataframe[column],
        errors="coerce",
    )

    if len(values) < 2:
        raise ValueError(
            "calculate_percentage_change requires at least "
            "two rows."
        )

    result_rows: list[dict[str, Any]] = []

    for position in range(1, len(values)):
        previous_value = values.iloc[position - 1]
        current_value = values.iloc[position]

        if pd.isna(previous_value) or pd.isna(current_value):
            raise ValueError(
                "Percentage change cannot be calculated "
                "from null values."
            )

        if previous_value == 0:
            raise ValueError(
                "Percentage change cannot use zero as the baseline."
            )

        percentage_change = (
            (current_value - previous_value)
            / previous_value
            * 100
        )

        result_rows.append(
            {
                "previous_value": float(previous_value),
                "current_value": float(current_value),
                "percentage_change": float(percentage_change),
            }
        )

    return pd.DataFrame(
        result_rows,
        columns=[
            "previous_value",
            "current_value",
            "percentage_change",
        ],
    )


def _execute_missing_values(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "column": dataframe.columns,
            "missing_count": dataframe.isna().sum().values,
            "missing_percentage": (
                dataframe.isna().mean().values * 100
            ),
        }
    )


def _clean_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    result = dataframe.copy()

    result = result.replace(
        {
            pd.NA: None,
            float("inf"): None,
            float("-inf"): None,
        }
    )

    return result.where(
        pd.notna(result),
        None,
    )


def execute_pandas_operation(
    dataframe: pd.DataFrame,
    operation: dict[str, Any],
) -> PandasExecutionResult:
    operation_name = operation.get("operation")

    if not operation_name:
        return PandasExecutionResult(
            success=False,
            operation="unknown",
            columns=[],
            rows=[],
            row_count=0,
            error="operation is required.",
        )

    try:
        if operation_name == "group_by":
            result = _execute_group_by(
                dataframe,
                operation,
            )

        elif operation_name == "aggregate":
            result = _execute_aggregate(
                dataframe,
                operation,
            )

        elif operation_name == "sort":
            result = _execute_sort(
                dataframe,
                operation,
            )

        elif operation_name == "describe":
            result = _execute_describe(
                dataframe,
            )

        elif operation_name == "calculate_percentage_change":
            result = _execute_percentage_change(
                dataframe,
                operation,
            )

        elif operation_name == "detect_missing_values":
            result = _execute_missing_values(
                dataframe,
            )

        else:
            raise ValueError(
                f"Unsupported Pandas operation: {operation_name}"
            )

        if len(result) > MAX_RESULT_ROWS:
            raise ValueError(
                f"Pandas operation returned more than "
                f"{MAX_RESULT_ROWS} rows."
            )

        result = _clean_dataframe(result)

        rows = result.to_dict(
            orient="records"
        )

        return PandasExecutionResult(
            success=True,
            operation=operation_name,
            columns=list(result.columns),
            rows=rows,
            row_count=len(rows),
        )

    except (ValueError, KeyError, TypeError) as exc:
        return PandasExecutionResult(
            success=False,
            operation=operation_name,
            columns=[],
            rows=[],
            row_count=0,
            error=str(exc),
        )