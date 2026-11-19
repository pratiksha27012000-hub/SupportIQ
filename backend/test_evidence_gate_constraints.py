
from backend.app.rag.evidence_gate import evaluate_evidence


result = evaluate_evidence(
    evidence_classification="constraint_only",
    constraint_answers_question=True
)

print("\n========== CONSTRAINT ANSWERABILITY TEST ==========")
print("Classification:", result["classification"])
print("Decision:", result["decision"])
print("Allow generation:", result["allow_generation"])
print("Human assistance:", result["offer_human_assistance"])
print("Reason:", result["reason"])
