import pytest

from app.tools.sql_tool import validate_sql


def test_valid_select():
    result = validate_sql(
        "SELECT id, name FROM products"
    )

    assert result.valid is True
    assert result.error is None


def test_valid_select_with_join():
    result = validate_sql(
        """
        SELECT
            p.category,
            SUM(oi.quantity * oi.unit_price) AS revenue
        FROM order_items oi
        JOIN products p
            ON p.id = oi.product_id
        GROUP BY p.category
        """
    )

    assert result.valid is True


@pytest.mark.parametrize(
    "query",
    [
        "DELETE FROM products",
        "UPDATE products SET cost = 0",
        "INSERT INTO products VALUES (1, 'test')",
        "DROP TABLE products",
        "ALTER TABLE products ADD COLUMN test TEXT",
        "TRUNCATE TABLE products",
        "CREATE TABLE malicious (id INT)",
    ],
)
def test_write_operations_are_rejected(query):
    result = validate_sql(query)

    assert result.valid is False


def test_multiple_statements_are_rejected():
    result = validate_sql(
        "SELECT * FROM products; DROP TABLE products;"
    )

    assert result.valid is False


def test_empty_query_is_rejected():
    result = validate_sql("")

    assert result.valid is False