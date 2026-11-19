
from pathlib import Path

from backend.app.document_loader import (
    extract_pdf_blocks,
    extract_docx_blocks,
    extract_txt_blocks
)

from backend.app.chunking import (
    split_pdf_blocks_into_section_chunks,
    split_docx_blocks_into_section_chunks
)

from backend.app.metadata_loader import load_document_metadata

from backend.app.metadata_enrichment import enrich_chunks_with_metadata


def ingest_knowledge_base(
    knowledge_base_path: str,
    metadata_workbook_path: str
):
    knowledge_base = Path(knowledge_base_path)

    metadata_registry = load_document_metadata(
        metadata_workbook_path
    )

    all_enriched_chunks = []
    failed_documents = []

    supported_extensions = {".pdf", ".docx", ".txt"}

    files = sorted([
        path for path in knowledge_base.rglob("*")
        if path.is_file()
        and path.suffix.lower() in supported_extensions
        and "metadata" not in [
            part.lower()
            for part in path.relative_to(knowledge_base).parts
        ]
    ])

    print("Documents discovered:", len(files))

    for file_path in files:
        try:
            extension = file_path.suffix.lower()

            if extension == ".pdf":
                blocks = extract_pdf_blocks(str(file_path))
                chunks = split_pdf_blocks_into_section_chunks(blocks)

            elif extension == ".docx":
                blocks = extract_docx_blocks(str(file_path))
                chunks = split_docx_blocks_into_section_chunks(blocks)

            elif extension == ".txt":
                blocks = extract_txt_blocks(str(file_path))
                chunks = split_docx_blocks_into_section_chunks(blocks)

            document = {
                "file_name": file_path.name,
                "file_path": str(file_path),
                "file_type": extension
            }

            enriched_chunks = enrich_chunks_with_metadata(
                document,
                chunks,
                metadata_registry
            )

            all_enriched_chunks.extend(enriched_chunks)

            print(
                f"Processed: {file_path.name} | "
                f"Chunks: {len(enriched_chunks)}"
            )

        except Exception as error:
            failed_documents.append({
                "file": file_path.name,
                "error": str(error)
            })

            print(f"FAILED: {file_path.name} | {error}")

    print("\n========== INGESTION SUMMARY ==========")
    print("Documents discovered:", len(files))
    print("Documents successfully processed:", len(files) - len(failed_documents))
    print("Documents failed:", len(failed_documents))
    print("Total enriched chunks:", len(all_enriched_chunks))
    print("=======================================")

    return all_enriched_chunks, failed_documents
