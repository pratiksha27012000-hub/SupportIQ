
from backend.app.rag.retriever import retrieve_relevant_chunks
from backend.app.rag.generator import generate_answer

# 1. Retrieve relevant policy evidence
question = "Can I get my room before the normal check-in time?"

retrieval_result = retrieve_relevant_chunks(
    question=question,
    audience="Guest"
)

# 2. Pass retrieved evidence to the generator
generation_result = generate_answer(
    question=question,
    retrieved_chunks=retrieval_result["retrieved_chunks"]
)

# 3. Display the generated response
print("\n========== GENERATOR TEST ==========")
print("Status:", generation_result["status"])
print("\nAnswer:")
print(generation_result["answer"])

print("\nCitations:")

for citation in generation_result["citations"]:
    print(
        citation["document_id"],
        "|",
        citation["document_name"],
        "|",
        citation["section"],
        "|",
        citation["chunk_id"]
    )

print("\n===================================")
