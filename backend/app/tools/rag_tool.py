from math import isfinite

from app.rag.vectorstore import search_documents
from app.schemas.rag import RAGSearchResult, RetrievedDocument


MAX_RAG_DISTANCE = 1.20


def retrieve_business_documents(
    query: str,
    top_k: int = 5,
) -> RAGSearchResult:
    query = query.strip()

    if not query:
        raise ValueError("Query cannot be empty.")

    documents = search_documents(
        query=query,
        top_k=top_k,
    )

    relevant_documents = []

    for document in documents:
        distance = document.get("distance")

        if distance is None:
            continue

        try:
            distance_value = float(distance)
        except (TypeError, ValueError):
            continue

        if not isfinite(distance_value):
            continue

        if distance_value > MAX_RAG_DISTANCE:
            continue

        relevant_documents.append(
            RetrievedDocument(
                document_id=document["document_id"],
                document=document["document"],
                distance=distance_value,
                metadata=document["metadata"],
            )
        )

    return RAGSearchResult(
        query=query,
        documents=relevant_documents,
    )