from pydantic import BaseModel, Field


class SQLGenerationResult(BaseModel):
    sql: str = Field(
        description="A single PostgreSQL SELECT statement that answers the user's question."
    )
    reasoning: str = Field(
        description="A concise explanation of why this SQL answers the question."
    )