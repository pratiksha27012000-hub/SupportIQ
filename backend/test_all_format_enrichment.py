
from backend.app.document_loader import (
    load_document,
    extract_docx_blocks,
    extract_txt_blocks
)

from backend.app.metadata_loader import load_document_metadata

from backend.app.chunking import (
    split_document_into_section_chunks,
    split_docx_blocks_into_section_chunks
)

from backend.app.metadata_enrichment import enrich_chunks_with_metadata


# 1. Load Excel metadata registry
workbook_path = (
    "knowledge_base/Metadata/"
    "StayEase_Knowledge_Base_Registry_v0.1.xlsx"
)

metadata_registry = load_document_metadata(workbook_path)


# 2. Define our three test documents
test_files = [
    {
        "format": "PDF",
        "path": (
            "knowledge_base/Guest_Policies/"
            "POL-GST-006_Early_Check_in_Late_Check_out_Policy.pdf"
        )
    },
    {
        "format": "DOCX",
        "path": (
            "knowledge_base/SOPs/"
            "SOP-005_Check_in_Issue_Resolution.docx"
        )
    },
    {
        "format": "TXT",
        "path": (
            "knowledge_base/Knowledge_Articles/"
            "KB-001_Guest_Support_FAQs.txt"
        )
    }
]


# 3. Process each format
all_enriched_chunks = []

for item in test_files:

    file_path = item["path"]
    file_format = item["format"]

    print(f"\nProcessing {file_format}: {file_path}")

    if file_format == "PDF":
        document = load_document(file_path)

        chunks = split_document_into_section_chunks(
            pages=document["content"],
            section_headings=[
                "Purpose and scope",
                "Policy rules",
                "Request workflow",
                "Exceptions",
                "Related documents"
            ]
        )

    elif file_format == "DOCX":
        document = {
            "file_name": file_path.split("/")[-1]
        }

        blocks = extract_docx_blocks(file_path)

        chunks = split_docx_blocks_into_section_chunks(blocks)

    else:
        document = {
            "file_name": file_path.split("/")[-1]
        }

        blocks = extract_txt_blocks(file_path)

        chunks = split_docx_blocks_into_section_chunks(blocks)


    # 4. Apply common metadata enrichment
    enriched_chunks = enrich_chunks_with_metadata(
        document=document,
        chunks=chunks,
        metadata_registry=metadata_registry
    )

    all_enriched_chunks.extend(enriched_chunks)

    print("Document ID:", enriched_chunks[0]["document_id"])
    print("Chunks created:", len(enriched_chunks))
    print("Audience:", enriched_chunks[0]["audience"])
    print("Category:", enriched_chunks[0]["category"])
    print("Status:", enriched_chunks[0]["status"])


# 5. Final summary
print("\n========== ENRICHMENT SUMMARY ==========")
print("Documents processed:", len(test_files))
print("Total enriched chunks:", len(all_enriched_chunks))

for chunk in all_enriched_chunks:
    print(
        chunk["chunk_id"],
        "|",
        chunk["document_id"],
        "|",
        chunk["section"]
    )

print("\n========================================")
