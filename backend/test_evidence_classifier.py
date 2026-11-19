
from backend.app.rag.evidence_classifier import (
    classify_evidence,
    assess_evidence_status
)

# Test 1: No evidence
result_1 = classify_evidence(
    question="Can you arrange airport pickup?",
    selected_chunks=[]
)

print("\nTEST 1: No Evidence")
print(result_1)


# Test 2: Wrong audience
result_2 = classify_evidence(
    question="Can I get early check-in?",
    selected_chunks=[
        {
            "chunk_id": "POL-HTL-001_CHUNK_001",
            "audience": "Hotel Partner",
            "status": "Draft"
        }
    ]
)

print("\nTEST 2: Wrong Audience")
print(result_2)


# Test 3: Guest Draft evidence
result_3 = classify_evidence(
    question="Can I get early check-in?",
    selected_chunks=[
        {
            "chunk_id": "POL-GST-006_CHUNK_002",
            "audience": "Guest",
            "status": "Draft"
        }
    ]
)

print("\nTEST 3: Guest Draft Evidence")
print(result_3)


print("\n========== EVIDENCE ASSESSMENT TESTS ==========")

test_cases = [
    {
        "name": "No annotation",
        "chunks": [
            {"chunk_id": "C1"}
        ],
        "expected": "unassessed"
    },
    {
        "name": "Sufficient evidence",
        "chunks": [
            {"chunk_id": "C1", "evidence_type": "sufficient"}
        ],
        "expected": "sufficient"
    },
    {
        "name": "Constraint only",
        "chunks": [
            {"chunk_id": "C2", "evidence_type": "constraint_only"}
        ],
        "expected": "constraint_only"
    },
    {
        "name": "Insufficient evidence",
        "chunks": [
            {"chunk_id": "C3", "evidence_type": "insufficient"}
        ],
        "expected": "insufficient"
    }
]

for test in test_cases:
    result = assess_evidence_status(test["chunks"])

    print("\nTest:", test["name"])
    print("Expected:", test["expected"])
    print("Actual:", result)
    print("Passed:", result == test["expected"])


print("\n========== INTEGRATED CLASSIFIER TESTS ==========")

integrated_cases = [
    {
        "name": "Sufficient evidence",
        "chunks": [
            {
                "chunk_id": "POL-GST-006_CHUNK_002",
                "audience": "Guest",
                "status": "Draft",
                "evidence_type": "sufficient"
            }
        ],
        "expected": "sufficient"
    },
    {
        "name": "Constraint-only evidence",
        "chunks": [
            {
                "chunk_id": "POL-GST-008_CHUNK_004",
                "audience": "Guest",
                "status": "Draft",
                "evidence_type": "constraint_only"
            }
        ],
        "expected": "constraint_only"
    },
    {
        "name": "Insufficient evidence",
        "chunks": [
            {
                "chunk_id": "KB-001_CHUNK_002",
                "audience": "Guest",
                "status": "Draft",
                "evidence_type": "insufficient"
            }
        ],
        "expected": "insufficient"
    },
    {
        "name": "Unassessed evidence",
        "chunks": [
            {
                "chunk_id": "POL-GST-006_CHUNK_002",
                "audience": "Guest",
                "status": "Draft"
            }
        ],
        "expected": "unassessed"
    }
]

for test in integrated_cases:
    result = classify_evidence(
        question="Can I get early check-in?",
        selected_chunks=test["chunks"]
    )

    passed = result["classification"] == test["expected"]

    print("\nTest:", test["name"])
    print("Expected:", test["expected"])
    print("Actual:", result["classification"])
    print("Passed:", passed)
    print("Draft evidence:", result["draft_evidence_present"])
