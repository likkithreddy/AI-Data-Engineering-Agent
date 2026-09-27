import pandas as pd

from app.tools.pandas_tool import execute_pandas_operation


def test_group_by_sum():
    dataframe = pd.DataFrame(
        {
            "category": [
                "Furniture",
                "Furniture",
                "Electronics",
            ],
            "revenue": [
                100.0,
                150.0,
                200.0,
            ],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "group_by",
            "group_columns": ["category"],
            "aggregations": {
                "revenue": "sum",
            },
        },
    )

    assert result.success is True
    assert result.row_count == 2

    values = {
        row["category"]: row["revenue"]
        for row in result.rows
    }

    assert values["Furniture"] == 250.0
    assert values["Electronics"] == 200.0


def test_sort_descending():
    dataframe = pd.DataFrame(
        {
            "product": ["A", "B", "C"],
            "revenue": [100.0, 300.0, 200.0],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "sort",
            "column": "revenue",
            "ascending": False,
        },
    )

    assert result.success is True

    assert [
        row["product"]
        for row in result.rows
    ] == ["B", "C", "A"]


def test_describe():
    dataframe = pd.DataFrame(
        {
            "revenue": [
                100.0,
                200.0,
                300.0,
            ],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "describe",
        },
    )

    assert result.success is True
    assert "column" in result.columns
    assert result.row_count == 1


def test_percentage_change():
    dataframe = pd.DataFrame(
        {
            "revenue": [
                100.0,
                125.0,
            ],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "calculate_percentage_change",
            "column": "revenue",
        },
    )

    assert result.success is True
    assert result.row_count == 1

    row = result.rows[0]

    assert row["previous_value"] == 100.0
    assert row["current_value"] == 125.0
    assert row["percentage_change"] == 25.0


def test_detect_missing_values():
    dataframe = pd.DataFrame(
        {
            "revenue": [100.0, None, 300.0],
            "category": ["A", "B", None],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "detect_missing_values",
        },
    )

    assert result.success is True

    missing = {
        row["column"]: row["missing_count"]
        for row in result.rows
    }

    assert missing["revenue"] == 1
    assert missing["category"] == 1


def test_invalid_column_is_rejected():
    dataframe = pd.DataFrame(
        {
            "revenue": [100.0, 200.0],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "sort",
            "column": "not_a_column",
        },
    )

    assert result.success is False
    assert "Columns not found" in result.error


def test_unsupported_operation_is_rejected():
    dataframe = pd.DataFrame(
        {
            "revenue": [100.0, 200.0],
        }
    )

    result = execute_pandas_operation(
        dataframe,
        {
            "operation": "execute_python",
        },
    )

    assert result.success is False
    assert "Unsupported Pandas operation" in result.error