from app.schemas.rag import RAGSearchResult, RetrievedDocument


def test_rag_result_contains_documents():
    result = RAGSearchResult(
        query="What is our refund policy?",
        documents=[
            RetrievedDocument(
                document_id="refund_policy",
                document="Customers may request a refund within 30 days.",
                distance=0.12,
                metadata={
                    "source": "refund_policy.txt",
                },
            )
        ],
    )

    assert result.query == "What is our refund policy?"
    assert len(result.documents) == 1
    assert (
        result.documents[0].document_id
        == "refund_policy"
    )
    assert (
        result.documents[0].metadata["source"]
        == "refund_policy.txt"
    )


def test_empty_rag_result_is_valid():
    result = RAGSearchResult(
        query="unknown question",
        documents=[],
    )

    assert result.documents == []