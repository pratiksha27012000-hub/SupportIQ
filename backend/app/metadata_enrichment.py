
from pathlib import Path


def enrich_chunks_with_metadata(
    document,
    chunks,
    metadata_registry
):
    """
    Attach authoritative Excel metadata to document chunks.
    Works with PDF, DOCX and TXT chunks.
    """

    # Identify document using its filename
    document_id = (
        Path(document["file_name"]).stem.split("_")[0]
    )

    # Retrieve metadata from Excel registry
    metadata = metadata_registry.get(document_id)

    if metadata is None:
        raise ValueError(
            f"Metadata not found for document: {document_id}"
        )

    enriched_chunks = []

    for index, chunk in enumerate(chunks, start=1):

        enriched_chunk = {
            "chunk_id": f"{document_id}_CHUNK_{index:03d}",
            "document_id": document_id,
            "document_name": metadata.get("document_name"),
            "document_type": metadata.get("document_type"),
            "audience": metadata.get("audience"),
            "category": metadata.get("category"),
            "subcategory": metadata.get("subcategory"),
            "owning_department": metadata.get("owning_department"),
            "version": metadata.get("version"),
            "status": metadata.get("status"),
            "confidentiality": metadata.get("confidentiality"),
            "section": chunk["section"],
            "page_number": chunk.get("page_number"),
            "text": chunk["text"]
        }

        enriched_chunks.append(enriched_chunk)

    return enriched_chunks
