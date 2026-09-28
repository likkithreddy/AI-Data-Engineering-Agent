from app.llm import gemini
from app.schemas.sql_generation import SQLGenerationResult


class FakeStructuredModel:
    def with_structured_output(self, schema):
        assert schema is SQLGenerationResult
        return self

    def invoke(self, messages):
        system_message = messages[0][1]
        user_message = messages[1][1]

        assert "safe" in system_message.lower()
        assert "database schema" in user_message.lower()

        return SQLGenerationResult(
            sql="""
                SELECT
                    p.category,
                    SUM(
                        oi.quantity
                        * oi.unit_price
                        * (1 - oi.discount)
                    ) AS revenue
                FROM products p
                JOIN order_items oi
                    ON oi.product_id = p.id
                JOIN orders o
                    ON o.id = oi.order_id
                WHERE o.status = 'completed'
                GROUP BY p.category
                ORDER BY revenue DESC
            """,
            reasoning=(
                "Revenue is calculated from completed orders using "
                "quantity, unit price, and discount, then grouped by "
                "product category."
            ),
        )


def test_generate_sql_for_revenue_question(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "get_gemini_model",
        lambda: FakeStructuredModel(),
    )

    result = gemini.generate_sql(
        "Which product category generated the most revenue?"
    )

    assert result.sql
    assert result.reasoning

    sql = result.sql.lower()

    assert "select" in sql
    assert "from" in sql
    assert "completed" in sql
    assert "revenue" in sql


def test_generate_sql_uses_known_schema(monkeypatch):
    monkeypatch.setattr(
        gemini,
        "get_gemini_model",
        lambda: FakeStructuredModel(),
    )

    result = gemini.generate_sql(
        "Show revenue by product category."
    )

    sql = result.sql.lower()

    assert "products" in sql
    assert "order_items" in sql
    assert "orders" in sql