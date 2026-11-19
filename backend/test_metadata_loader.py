
from backend.app.metadata_loader import load_document_metadata

workbook_path = (
    "knowledge_base/Metadata/"
    "StayEase_Knowledge_Base_Registry_v0.1.xlsx"
)

metadata = load_document_metadata(workbook_path)

print("\n========== METADATA LOADER TEST ==========")

print("Total metadata records:", len(metadata))

print("\nSample record: POL-GST-006")

sample = metadata.get("POL-GST-006")

if sample:
    for key, value in sample.items():
        print(f"{key}: {value}")
else:
    print("Document metadata not found!")

print("\n==========================================")
