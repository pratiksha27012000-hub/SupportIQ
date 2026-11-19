
from backend.app.rag.keyword_retriever import retrieve_keyword_chunks

question = "early check-in availability and additional fee"

results = retrieve_keyword_chunks(
    question=question,
    audience="Guest",
    top_k=5
)

print("\n========== BM25 KEYWORD SEARCH ==========")
print("Question:", question)

for index, chunk in enumerate(results, start=1):
    print(f"\nResult {index}")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document_name"])
    print("Section:", chunk["section"])
    print("BM25 Score:", round(chunk["bm25_score"], 4))
    print("Content:", chunk["content"])

print("\nResults returned:", len(results))
print("========================================")
