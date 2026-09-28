from app.schemas.pandas import PandasOperation


def test_pandas_operation_schema_accepts_group_by():
    operation = PandasOperation(
        operation="group_by",
        group_columns=["category"],
        aggregations={"revenue": "sum"},
    )

    assert operation.operation == "group_by"
    assert operation.group_columns == ["category"]
    assert operation.aggregations == {"revenue": "sum"}


def test_pandas_operation_schema_accepts_sort():
    operation = PandasOperation(
        operation="sort",
        column="revenue",
        ascending=False,
    )

    assert operation.operation == "sort"
    assert operation.column == "revenue"
    assert operation.ascending is False