from typing import Literal

from pydantic import BaseModel, Field


class ToolSelectionResult(BaseModel):
    selected_tool: Literal["sql", "pandas", "rag"] = Field(
        description=(
            "The single best tool for answering the user's question."
        )
    )
    reasoning: str = Field(
        description=(
            "A concise explanation of why this tool is appropriate."
        )
    )