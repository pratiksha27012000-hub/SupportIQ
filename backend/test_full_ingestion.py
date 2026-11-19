
from backend.app.ingestion_pipeline import ingest_knowledge_base
import json
from pathlib import Path

chunks, failures = ingest_knowledge_base(
    knowledge_base_path="knowledge_base",
    metadata_workbook_path=(
        "knowledge_base/Metadata/"
        "StayEase_Knowledge_Base_Registry_v0.1.xlsx"
    )
)

print("\n========== FINAL VALIDATION ==========")

print("Total chunks:", len(chunks))
print("Failed documents:", len(failures))

# Check unique chunk IDs
chunk_ids = [chunk["chunk_id"] for chunk in chunks]

print("Unique chunk IDs:", len(set(chunk_ids)))
print("Duplicate chunk IDs:", len(chunk_ids) - len(set(chunk_ids)))

# Check required metadata
required_fields = [
    "chunk_id",
    "document_id",
    "document_name",
    "audience",
    "category",
    "section",
    "text"
]

invalid_chunks = [
    chunk["chunk_id"]
    for chunk in chunks
    if any(
        chunk.get(field) is None or chunk.get(field) == ""
        for field in required_fields
    )
]

print("Chunks with missing required fields:", len(invalid_chunks))

print("======================================")


# Save enriched chunks
output_folder = Path("knowledge_base/processed")
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "enriched_chunks.jsonl"

with open(output_file, "w", encoding="utf-8") as file:
    for chunk in chunks:
        file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print("\nSaved enriched chunks to:", output_file)
print("Saved records:", len(chunks))