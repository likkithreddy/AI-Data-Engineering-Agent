from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb

from app.core.config import settings
from app.rag.embeddings import embed_query, embed_texts


def get_chroma_client() -> chromadb.PersistentClient:
    path = Path(settings.chroma_path)

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return chromadb.PersistentClient(
        path=str(path),
    )


def get_collection():
    client = get_chroma_client()

    return client.get_or_create_collection(
        name=settings.chroma_collection_name,
    )


def add_documents(
    documents: list[str],
    document_ids: list[str],
    metadatas: list[dict[str, Any]] | None = None,
) -> None:
    if len(documents) != len(document_ids):
        raise ValueError(
            "documents and document_ids must have the same length."
        )

    if not documents:
        return

    collection = get_collection()

    embeddings = embed_texts(documents)

    collection.upsert(
        ids=document_ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def search_documents(
    query: str,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not query.strip():
        raise ValueError("Query cannot be empty.")

    if top_k < 1:
        raise ValueError("top_k must be at least 1.")

    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[embed_query(query)],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances",
        ],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    ids = results.get("ids", [[]])[0]

    return [
        {
            "document_id": ids[index],
            "document": documents[index],
            "metadata": metadatas[index] or {},
            "distance": distances[index],
        }
        for index in range(len(documents))
    ]