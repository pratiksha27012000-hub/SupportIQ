
import json
from pathlib import Path

from backend.app.rag.vector_store import (
    collection,
    embedding_model
)

# 1. Locate the enriched chunks file
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "enriched_chunks.jsonl"
)

# 2. Load all enriched chunks
chunks = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        chunks.append(json.loads(line))

print("Chunks loaded:", len(chunks))

for chunk in chunks:
    if chunk["chunk_id"] == "POL-GST-005_CHUNK_002":
        print("\n========== METADATA CHECK ==========")
        print("Document ID:", chunk.get("document_id"))
        print("Status:", repr(chunk.get("status")))
        print("Page Number:", repr(chunk.get("page_number")))
        print("Audience:", repr(chunk.get("audience")))
        print("===================================")

        
# 3. Extract text for embedding generation
texts = [chunk["text"] for chunk in chunks]

# 4. Generate embeddings
print("\nGenerating embeddings...")

embeddings = embedding_model.encode(
    texts,
    convert_to_numpy=True,
    show_progress_bar=True
)

print("Embeddings generated:", embeddings.shape)

# 5. Prepare metadata
metadata_fields = [
    "document_id",
    "document_name",
    "document_type",
    "audience",
    "category",
    "subcategory",
    "owning_department",
    "version",
    "status",
    "confidentiality",
    "section",
    "page_number"
]

metadatas = []

for chunk in chunks:
    metadata = {
        field: chunk[field]
        for field in metadata_fields
        if chunk.get(field) is not None
    }
    metadatas.append(metadata)

# 6. Store everything in ChromaDB
collection.upsert(
    ids=[chunk["chunk_id"] for chunk in chunks],
    documents=texts,
    embeddings=embeddings.tolist(),
    metadatas=metadatas
)

# 7. Verify storage
print("\n========== VECTOR STORE SUMMARY ==========")
print("Collection:", collection.name)
print("Chunks processed:", len(chunks))
print("Embedding dimensions:", embeddings.shape[1])
print("Records in ChromaDB:", collection.count())
print("==========================================")
