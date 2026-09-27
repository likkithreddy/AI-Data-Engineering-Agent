from typing import Literal

from pydantic import BaseModel, Field


PandasOperationName = Literal[
    "group_by",
    "aggregate",
    "sort",
    "describe",
    "calculate_percentage_change",
    "detect_missing_values",
]


class PandasOperation(BaseModel):
    operation: PandasOperationName

    group_columns: list[str] = Field(default_factory=list)

    aggregations: dict[
        str,
        Literal[
            "sum",
            "mean",
            "min",
            "max",
            "count",
        ],
    ] = Field(default_factory=dict)

    column: str | None = None

    ascending: bool = False