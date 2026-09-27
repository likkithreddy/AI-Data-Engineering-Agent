from sqlalchemy import inspect

from app.db.engine import engine


def get_database_schema() -> str:
    """Return a human-readable description of the database schema."""

    inspector = inspect(engine)

    lines: list[str] = []

    table_names = inspector.get_table_names()

    for table_name in table_names:
        lines.append(f"Table: {table_name}")
        lines.append("Columns:")

        columns = inspector.get_columns(table_name)

        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            nullable = column["nullable"]

            lines.append(
                f"- {column_name}: {column_type} "
                f"(nullable={nullable})"
            )

        foreign_keys = inspector.get_foreign_keys(table_name)

        if foreign_keys:
            lines.append("Foreign Keys:")

            for foreign_key in foreign_keys:
                constrained_columns = foreign_key["constrained_columns"]
                referred_table = foreign_key["referred_table"]
                referred_columns = foreign_key["referred_columns"]

                lines.append(
                    f"- {constrained_columns} -> "
                    f"{referred_table}.{referred_columns}"
                )

        lines.append("")

    return "\n".join(lines)