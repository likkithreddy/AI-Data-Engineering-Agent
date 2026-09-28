from pathlib import Path

from app.rag.vectorstore import add_documents


def load_documents(
    documents_directory: str | Path,
) -> tuple[list[str], list[str], list[dict[str, str]]]:
    directory = Path(documents_directory)

    if not directory.exists():
        raise FileNotFoundError(
            f"Document directory does not exist: {directory}"
        )

    documents: list[str] = []
    document_ids: list[str] = []
    metadatas: list[dict[str, str]] = []

    for path in sorted(directory.glob("**/*.txt")):
        content = path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            continue

        documents.append(content)
        document_ids.append(path.stem)
        metadatas.append(
            {
                "source": path.name,
            }
        )

    return documents, document_ids, metadatas


def ingest_documents(
    documents_directory: str | Path,
) -> int:
    documents, document_ids, metadatas = load_documents(
        documents_directory
    )

    add_documents(
        documents=documents,
        document_ids=document_ids,
        metadatas=metadatas,
    )

    return len(documents)