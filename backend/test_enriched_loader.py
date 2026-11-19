
from backend.app.document_loader import load_documents_with_metadata

documents = load_documents_with_metadata(
    folder_path="knowledge_base",
    workbook_path=(
        "knowledge_base/Metadata/"
        "StayEase_Knowledge_Base_Registry_v0.1.xlsx"
    )
)

print("\n========== ENRICHED DOCUMENT TEST ==========")

print("Total enriched documents:", len(documents))

# Inspect one document
sample = next(
    (
        doc for doc in documents
        if doc["document_id"] == "POL-GST-006"
    ),
    None
)

if sample:
    print("\nDOCUMENT ID:", sample["document_id"])
    print("FILE NAME:", sample["file_name"])
    print("FILE TYPE:", sample["file_type"])

    print("\nMETADATA:")
    for key, value in sample["metadata"].items():
        print(f"{key}: {value}")

    print("\nCONTENT PREVIEW:")
    content = sample["content"]

    if isinstance(content, list):
        print(content[0]["text"][:500])
    else:
        print(content[:500])

else:
    print("POL-GST-006 not found!")

print("\n============================================")
