
from backend.app.ingestion_pipeline import ingest_knowledge_base

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

output_folder = __import__("pathlib").Path(
    "knowledge_base/processed"
)
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "enriched_chunks.jsonl"

import json

with open(output_file, "w", encoding="utf-8") as file:
    for chunk in chunks:
        file.write(json.dumps(chunk, ensure_ascii=False) + "\n")

print("Saved enriched chunks:", output_file)
print("Saved records:", len(chunks))
