from backend.app.rag.evidence_evaluator import (
    evaluate_evidence_with_groq
)

sample_chunks = [
    {
        "chunk_id": "POL-GST-006_CHUNK_002",
        "document_id": "POL-GST-006",
        "document_name": "Early Check-in & Late Check-out Policy",
        "section": "Policy rules",
        "audience": "Guest",
        "status": "Draft",
        "content": (
            "Early check-in is subject to property availability "
            "and approval. It is not guaranteed."
        )
    }
]

question = "What is the early check-in policy?"

print("\nTesting SupportIQ Evidence Evaluator...")

result = evaluate_evidence_with_groq(
    question=question,
    selected_chunks=sample_chunks
)

print("\n========== EVIDENCE ASSESSMENT ==========")
print("Classification:", result.classification)
print("Evidence IDs:", result.evidence_chunk_ids)
print("Supported facts:", result.supported_facts)
print("Missing information:", result.missing_information)
print("Reason:", result.reason)
print("Draft evidence:", result.draft_evidence_present)