
from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks

question = "early check-in availability and additional fee"

results = retrieve_hybrid_chunks(
    question=question,
    audience="Guest",
    top_k=5,
    candidate_k=10
)

print("\n========== HYBRID RETRIEVAL RESULTS ==========\n")

for rank, chunk in enumerate(results["retrieved_chunks"], start=1):
    print(f"Rank: {rank}")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document_name"])
    print("Section:", chunk["section"])
    print("RRF Score:", round(chunk["rrf_score"], 5))
    print("Dense Rank:", chunk.get("dense_rank", "Not retrieved"))
    print("Keyword Rank:", chunk.get("keyword_rank", "Not retrieved"))
    print("-" * 60)

print("Total results:", len(results["retrieved_chunks"]))
print("Status:", results["status"])
