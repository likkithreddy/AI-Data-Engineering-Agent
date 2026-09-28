from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source_type: str = Field(
        description="Type of evidence: sql, pandas, or rag."
    )
    source: str = Field(
        description="Human-readable description of the evidence source."
    )
    details: str = Field(
        description="Specific evidence supporting the answer."
    )


class InsightResult(BaseModel):
    answer: str = Field(
        description="A concise business answer grounded only in supplied evidence."
    )
    evidence: list[EvidenceItem] = Field(
        default_factory=list,
        description="Evidence supporting the answer."
    )
    caveats: list[str] = Field(
        default_factory=list,
        description="Important limitations or caveats."
    )