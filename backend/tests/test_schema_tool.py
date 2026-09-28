from app.tools.schema_tool import get_database_schema


def test_database_schema_contains_expected_tables():
    schema = get_database_schema()

    assert "customers" in schema
    assert "products" in schema
    assert "orders" in schema
    assert "order_items" in schema


def test_database_schema_contains_relationships():
    schema = get_database_schema()

    assert "customers" in schema
    assert "orders" in schema
    assert "products" in schema