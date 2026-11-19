
from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks
from backend.app.rag.reranker import rerank_chunks
from backend.app.rag.context_builder import build_context

question = "Can I get my room before the normal check-in time?"

# 1. Hybrid retrieval
hybrid_result = retrieve_hybrid_chunks(
    question=question,
    audience="Guest",
    top_k=10,
    candidate_k=10
)

# 2. Cross-Encoder reranking
reranked_chunks = rerank_chunks(
    question=question,
    retrieved_chunks=hybrid_result["retrieved_chunks"],
    top_k=5
)

# 3. Build context
context_result = build_context(
    question=question,
    reranked_chunks=reranked_chunks,
    audience="Guest",
    max_chunks=5
)

# 4. Display results
print("\n========== CONTEXT BUILDER TEST ==========\n")

print("Question:", context_result["question"])
print("Audience:", context_result["audience"])
print("Status:", context_result["status"])
print("Chunks selected:", context_result["chunk_count"])

print("\n========== SELECTED SOURCES ==========\n")

for citation in context_result["citations"]:
    print("Chunk ID:", citation["chunk_id"])
    print("Document:", citation["document_name"])
    print("Section:", citation["section"])
    print("Status:", citation["status"])
    print("-" * 50)

print("\n========== FINAL LLM CONTEXT ==========\n")
print(context_result["context"])

print("\n========== TEST COMPLETE ==========")
