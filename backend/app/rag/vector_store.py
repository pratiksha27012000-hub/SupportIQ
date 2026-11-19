
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

# 1. Define paths
PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "enriched_chunks.jsonl"
)

CHROMA_PATH = (
    PROJECT_ROOT
    / "backend"
    / "storage"
    / "chroma_db"
)

# 2. Load embedding model
embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

# 3. Create persistent ChromaDB client
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

# 4. Create collection
collection = client.get_or_create_collection(
    name="supportiq_knowledge_base",
    metadata={"hnsw:space": "cosine"}
)

print("Vector store initialized!")
print("Collection:", collection.name)


import json


def ingest_chunks_into_vector_store():
    """Load enriched chunks, generate embeddings and upsert into ChromaDB."""

    if not CHUNKS_FILE.exists():
        raise FileNotFoundError(
            f"Enriched chunks file not found: {CHUNKS_FILE}"
        )

    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    if not chunks:
        raise ValueError("No enriched chunks found.")

    print("Chunks loaded:", len(chunks))

    # Extract text
    texts = [chunk["text"] for chunk in chunks]

    # Generate embeddings
    print("\nGenerating embeddings...")

    embeddings = embedding_model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True
    )

    # Prepare metadata
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

    # Upsert into ChromaDB
    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in chunks],
        documents=texts,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    print("\n========== VECTOR STORE SUMMARY ==========")
    print("Collection:", collection.name)
    print("Chunks processed:", len(chunks))
    print("Embedding dimensions:", embeddings.shape[1])
    print("Records in ChromaDB:", collection.count())
    print("==========================================")

    return {
        "chunks_processed": len(chunks),
        "embedding_dimensions": embeddings.shape[1],
        "collection_count": collection.count()
    }
