
from backend.app.rag.pipeline import run_rag_pipeline

question = "Can I get my room before the normal check-in time?"

result = run_rag_pipeline(
    question=question,
    audience="Guest"
)

print("\n========== SUPPORTIQ FULL RAG PIPELINE ==========\n")

print("QUESTION:", result["question"])
print("AUDIENCE:", result["audience"])

print("\n========== HYBRID RETRIEVAL ==========")

for rank, chunk in enumerate(
    result["retrieval"]["retrieved_chunks"], start=1
):
    print(
        rank,
        chunk["chunk_id"],
        "RRF:", round(chunk["rrf_score"], 5)
    )

print("\n========== CROSS-ENCODER RERANKING ==========")

for rank, chunk in enumerate(
    result["reranking"]["reranked_chunks"], start=1
):
    print(
        rank,
        chunk["chunk_id"],
        "Score:", round(chunk["reranker_score"], 4)
    )

print("\n========== EVIDENCE ASSESSMENT ==========")

evidence = result["evidence_assessment"]

print("Classification:", evidence["classification"])
print("Reason:", evidence["reason"])
print("Draft Evidence:", evidence["draft_evidence_present"])

print("\n========== DOCUMENT APPROVAL ASSESSMENT ==========")

approval = result["approval_assessment"]

print("Approval Status:", approval["status"])
print("Approved:", approval["approved"])
print("Unapproved Chunks:", approval["unapproved_chunk_ids"])

print("\n========== EVIDENCE GATE ==========")

gate = result["evidence_gate"]

print("Decision:", gate["decision"])
print("Allow Generation:", gate["allow_generation"])
print("Reason:", gate["reason"])

print("\n========== GENERATION ==========")

generation = result["generation"]

print("Status:", generation["status"])
print("Answer:", generation["answer"])

print("\nCITATIONS:")

for citation in generation["citations"]:
    print(
        citation["document_id"],
        "|",
        citation["document_name"],
        "|",
        citation["section"]
    )

print("\n========== PIPELINE COMPLETE ==========")
