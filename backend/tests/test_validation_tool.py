from app.tools.validation_tool import (
    validate_pandas_operation_result,
    validate_tabular_result,
)


def test_valid_tabular_result():
    result = validate_tabular_result(
        columns=["category", "revenue"],
        rows=[
            {
                "category": "Furniture",
                "revenue": 100.0,
            }
        ],
        row_count=1,
    )

    assert result.valid is True
    assert result.errors == []


def test_row_count_mismatch_is_invalid():
    result = validate_tabular_result(
        columns=["category"],
        rows=[
            {"category": "Furniture"},
        ],
        row_count=2,
    )

    assert result.valid is False
    assert "Row count does not match" in result.errors[0]


def test_missing_values_generate_warning():
    result = validate_tabular_result(
        columns=["category", "revenue"],
        rows=[
            {
                "category": "Furniture",
                "revenue": None,
            }
        ],
        row_count=1,
    )

    assert result.valid is True
    assert any(
        "revenue" in warning
        for warning in result.warnings
    )


def test_pandas_validation_uses_same_rules():
    result = validate_pandas_operation_result(
        columns=["value"],
        rows=[{"value": 100}],
        row_count=1,
    )

    assert result.valid is True