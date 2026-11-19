
from backend.app.rag.retriever import retrieve_relevant_chunks

result = retrieve_relevant_chunks(
    question="Can I get my room before the normal check-in time?",
    audience="Guest"
)

print("\n========== RETRIEVER TEST ==========")
print("Status:", result["status"])
print("Question:", result["question"])

for index, chunk in enumerate(
    result["retrieved_chunks"],
    start=1
):
    print(f"\nResult {index}")
    print("Chunk ID:", chunk["chunk_id"])
    print("Document:", chunk["document_name"])
    print("Section:", chunk["section"])
    print("Similarity:", round(chunk["similarity"], 4))
    print("Content:", chunk["content"])

print("\n===================================")
