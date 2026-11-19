
import json
from pathlib import Path

file_path = Path(
    "knowledge_base/processed/enriched_chunks.jsonl"
)

chunks = []

with open(file_path, "r", encoding="utf-8") as file:
    for line in file:
        if line.strip():
            chunks.append(json.loads(line))

# Measure approximate size using word count
for chunk in chunks:
    chunk["word_count"] = len(chunk["text"].split())

word_counts = [chunk["word_count"] for chunk in chunks]

print("========== CHUNK SIZE REPORT ==========")
print("Total chunks:", len(chunks))
print("Average words:", round(sum(word_counts) / len(word_counts), 2))
print("Largest chunk:", max(word_counts))
print("Smallest chunk:", min(word_counts))

print("\nTop 10 largest chunks:")

largest_chunks = sorted(
    chunks,
    key=lambda item: item["word_count"],
    reverse=True
)[:10]

for chunk in largest_chunks:
    print(
        chunk["chunk_id"],
        "| Section:", chunk["section"],
        "| Words:", chunk["word_count"]
    )

print("=======================================")
