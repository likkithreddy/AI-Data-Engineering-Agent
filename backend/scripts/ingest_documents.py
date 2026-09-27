from pathlib import Path

from app.rag.ingest import ingest_documents


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]

    documents_directory = (
        project_root / "data" / "documents"
    )

    count = ingest_documents(
        documents_directory
    )

    print(
        f"Successfully ingested {count} document(s)."
    )


if __name__ == "__main__":
    main()