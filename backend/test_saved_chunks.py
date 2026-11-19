
import json
from pathlib import Path

file_path = Path(
    "knowledge_base/processed/enriched_chunks.jsonl"
)

loaded_chunks = []

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            loaded_chunks.append(json.loads(line))

print("========== SAVED FILE VALIDATION ==========")
print("File exists:", file_path.exists())
print("Records loaded:", len(loaded_chunks))

chunk_ids = [
    chunk["chunk_id"]
    for chunk in loaded_chunks
]

print("Unique IDs:", len(set(chunk_ids)))
print("Duplicate IDs:", len(chunk_ids) - len(set(chunk_ids)))

print("\nFirst chunk preview:")
print(json.dumps(
    loaded_chunks[0],
    indent=2,
    ensure_ascii=False
))

print("===========================================")
