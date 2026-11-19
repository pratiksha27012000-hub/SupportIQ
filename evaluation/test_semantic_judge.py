
from evaluation.semantic_judge import evaluate_semantic_quality


test_case = {
    "test_id": "JUDGE-001",
    "query": "Can I get an early check-in?",
    "expected_outcome": "answer",
    "required_facts": [
        "Early check-in is not guaranteed",
        "Availability is determined by the property",
        "Any applicable fee must be confirmed"
    ],
    "prohibited_claims": [
        "Early check-in is guaranteed"
    ],
    "expected_citations": [
        "POL-GST-006_CHUNK_002"
    ],
    "ticketing_expectation": None
}


evidence_chunks = [
    {
        "chunk_id": "POL-GST-006_CHUNK_002",
        "document_id": "POL-GST-006",
        "document_name": "Early Check-in & Late Check-out Policy",
        "section": "Policy rules",
        "content": (
            "Early check-in is a request and is not guaranteed. "
            "The property determines availability and approval. "
            "Any applicable fee must be confirmed before the "
            "guest accepts the arrangement."
        )
    }
]


generation_result = {
    "status": "answer",
    "answer": (
        "Early check-in is not guaranteed. The property determines "
        "whether it can be accommodated, and any applicable fee "
        "must be confirmed before you accept."
    ),
    "citations": [
        {
            "chunk_id": "POL-GST-006_CHUNK_002",
            "document_id": "POL-GST-006",
            "document_name": "Early Check-in & Late Check-out Policy",
            "section": "Policy rules"
        }
    ],
    "reason": None
}


print("\nTesting SupportIQ Semantic Judge...")

result = evaluate_semantic_quality(
    test_case=test_case,
    generation_result=generation_result,
    evidence_chunks=evidence_chunks
)

print("\n========== SEMANTIC EVALUATION ==========")

for key, value in result.items():
    print(f"{key}: {value}")

print("\nSemantic Judge test completed!")
