
import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Load the embedding model
print("Loading embedding model...")

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# Read enriched chunks
input_file = Path("knowledge_base/processed/enriched_chunks.jsonl")

chunks = []

with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        chunks.append(json.loads(line))

# Tokenize all chunks
texts = [chunk["text"] for chunk in chunks]

encoded = model.tokenizer(
    texts,
    add_special_tokens=True,
    truncation=False
)

token_counts = [
    len(token_ids)
    for token_ids in encoded["input_ids"]
]

# Calculate statistics
print("\n========== TOKEN LENGTH REPORT ==========")
print("Total chunks:", len(chunks))
print("Model maximum sequence length:", model.max_seq_length)
print("Average tokens:", round(sum(token_counts) / len(token_counts), 2))
print("Largest chunk:", max(token_counts))
print("Smallest chunk:", min(token_counts))

exceeding = [
    (chunks[i]["chunk_id"], token_counts[i])
    for i in range(len(chunks))
    if token_counts[i] > model.max_seq_length
]

print("Chunks exceeding model limit:", len(exceeding))

if exceeding:
    print("\nChunks requiring attention:")
    for chunk_id, count in exceeding:
        print(chunk_id, "| Tokens:", count)

print("=========================================")
