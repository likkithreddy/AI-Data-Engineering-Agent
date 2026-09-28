from app.tools.sql_tool import execute_sql


def test_execute_simple_select():
    result = execute_sql(
        "SELECT id, name FROM products ORDER BY id"
    )

    assert result.success is True
    assert result.row_count == 6
    assert result.columns == ["id", "name"]
    assert len(result.rows) == 6


def test_execute_revenue_query():
    query = """
        SELECT
            p.category,
            SUM(
                oi.quantity
                * oi.unit_price
                * (1 - oi.discount)
            ) AS revenue
        FROM order_items oi
        JOIN orders o
            ON o.id = oi.order_id
        JOIN products p
            ON p.id = oi.product_id
        WHERE o.status = 'completed'
        GROUP BY p.category
        ORDER BY revenue DESC
    """

    result = execute_sql(query)

    assert result.success is True
    assert result.row_count == 3

    assert result.rows[0]["category"] == "Furniture"
    assert float(result.rows[0]["revenue"]) == 4539.67


def test_invalid_sql_is_not_executed():
    result = execute_sql(
        "DROP TABLE products"
    )

    assert result.success is False
    assert result.row_count == 0
    assert "Only SELECT statements are allowed." in result.error

def test_query_result_limit():
    result = execute_sql(
        """
        SELECT id
        FROM generate_series(1, 501) AS numbers(id)
        """
    )

    assert result.success is False
    assert result.row_count == 0
    assert "more than 500 rows" in result.error
    

def test_query_timeout():
    result = execute_sql("SELECT pg_sleep(6)")

    assert result.success is False
    assert result.row_count == 0
    assert "Database execution failed" in result.error