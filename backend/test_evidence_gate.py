
from backend.app.rag.evidence_gate import evaluate_evidence


test_cases = [
    ("sufficient", False),
    ("partial", False),
    ("constraint_only", True),
    ("constraint_only", False),
    ("insufficient", False),
    ("unassessed", False)
]


for classification, constraint_answerable in test_cases:

    result = evaluate_evidence(
        evidence_classification=classification,
        constraint_answers_question=constraint_answerable
    )

    print("\nClassification:", classification)
    print("Decision:", result["decision"])
    print("Allow generation:", result["allow_generation"])
    print("Offer human assistance:", result["offer_human_assistance"])
    print("Reason:", result["reason"])
