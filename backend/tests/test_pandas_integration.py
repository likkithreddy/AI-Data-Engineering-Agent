import pandas as pd

from app.tools.pandas_tool import (
    execute_pandas_operation,
    sql_rows_to_dataframe,
)
from app.tools.validation_tool import (
    validate_pandas_operation_result,
)


def test_sql_rows_convert_to_dataframe():
    rows = [
        {
            "category": "Furniture",
            "revenue": 4539.67,
        },
        {
            "category": "Electronics",
            "revenue": 3710.10,
        },
    ]

    dataframe = sql_rows_to_dataframe(rows)

    assert isinstance(dataframe, pd.DataFrame)
    assert list(dataframe.columns) == [
        "category",
        "revenue",
    ]
    assert len(dataframe) == 2


def test_sql_result_can_flow_through_pandas():
    rows = [
        {
            "category": "Furniture",
            "revenue": 4539.67,
        },
        {
            "category": "Electronics",
            "revenue": 3710.10,
        },
        {
            "category": "Office Supplies",
            "revenue": 240.00,
        },
    ]

    dataframe = sql_rows_to_dataframe(rows)

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "sort",
            "column": "revenue",
            "ascending": False,
        },
    )

    assert result.success is True

    validation = validate_pandas_operation_result(
        columns=result.columns,
        rows=result.rows,
        row_count=result.row_count,
    )

    assert validation.valid is True
    assert result.rows[0]["category"] == "Furniture"