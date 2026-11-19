
from pathlib import Path

from backend.app.document_loader import load_document
from backend.app.metadata_loader import load_document_metadata
from backend.app.chunking import split_document_into_section_chunks


# 1. Load the PDF
file_path = (
    "knowledge_base/Guest_Policies/"
    "POL-GST-006_Early_Check_in_Late_Check_out_Policy.pdf"
)

document = load_document(file_path)


# 2. Load the metadata registry
workbook_path = (
    "knowledge_base/Metadata/"
    "StayEase_Knowledge_Base_Registry_v0.1.xlsx"
)

metadata_registry = load_document_metadata(workbook_path)


# 3. Identify the document
document_id = Path(document["file_name"]).stem.split("_")[0]

metadata = metadata_registry.get(document_id)

if metadata is None:
    raise ValueError(f"Metadata not found for {document_id}")


# 4. Create section chunks
section_headings = [
    "Purpose and scope",
    "Policy rules",
    "Request workflow",
    "Exceptions",
    "Related documents"
]

chunks = split_document_into_section_chunks(
    pages=document["content"],
    section_headings=section_headings
)


# 5. Enrich every chunk with document metadata
enriched_chunks = []

for index, chunk in enumerate(chunks, start=1):

    enriched_chunk = {
        "chunk_id": f"{document_id}_CHUNK_{index:03d}",
        "document_id": document_id,
        "document_name": metadata.get("document_name"),
        "document_type": metadata.get("document_type"),
        "audience": metadata.get("audience"),
        "category": metadata.get("category"),
        "version": metadata.get("version"),
        "status": metadata.get("status"),
        "section": chunk["section"],
        "page_number": chunk["page_number"],
        "text": chunk["text"]
    }

    enriched_chunks.append(enriched_chunk)


# 6. Display results
print("\n========== ENRICHED CHUNKS ==========")
print("Document ID:", document_id)
print("Total enriched chunks:", len(enriched_chunks))

for chunk in enriched_chunks:
    print("\n-----------------------------------")
    for key, value in chunk.items():
        print(f"{key}: {value}")

print("\n===================================")
