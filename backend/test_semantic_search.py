
from backend.app.rag.vector_store import collection, embedding_model

# 1. Ask a question that uses different wording
query = "Can I get my room before the normal check-in time?"

# 2. Convert the question into an embedding
query_embedding = embedding_model.encode(query).tolist()

# 3. Search ChromaDB for the 5 closest chunks
results = collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where={"audience": "Guest"},
    include=["documents", "metadatas", "distances"]
)

# 4. Display the results
print("\n========== SEMANTIC SEARCH RESULTS ==========")
print("Question:", query)

for index, (chunk_id, document, metadata, distance) in enumerate(
    zip(
        results["ids"][0],
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ),
    start=1
):
    print(f"\nResult {index}")
    print("Chunk ID:", chunk_id)
    print("Section:", metadata.get("section"))
    print("Category:", metadata.get("category"))
    print("Distance:", round(distance, 4))
    print("Content:", document)

print("\n=============================================")
