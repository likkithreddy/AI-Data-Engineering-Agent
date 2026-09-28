from pydantic import BaseModel


class RetrievedDocument(BaseModel):
    document_id: str
    document: str
    distance: float | None = None
    metadata: dict[str, str] = {}


class RAGSearchResult(BaseModel):
    query: str
    documents: list[RetrievedDocument]