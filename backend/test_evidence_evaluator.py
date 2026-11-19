
from backend.app.rag.evidence_evaluator import (
    EvidenceEvaluation,
    prepare_evidence_input
)
from backend.app.rag.evidence_evaluator import (
    build_evidence_evaluation_prompt
)

from pydantic import ValidationError
from backend.app.rag.evidence_evaluator import (
    validate_evidence_evaluation
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

prepared_input = prepare_evidence_input(
    question="Can I get an early check-in?",
    selected_chunks=sample_chunks
)

print("\n========== PREPARED EVIDENCE INPUT ==========")
print(prepared_input)

print("\nQuestion:", prepared_input["question"])
print("Evidence chunks:", len(prepared_input["evidence"]))
print("Chunk ID:", prepared_input["evidence"][0]["chunk_id"])
print("Document status:", prepared_input["evidence"][0]["status"])

prompt = build_evidence_evaluation_prompt(
    question="Can I get an early check-in?",
    selected_chunks=sample_chunks
)

print("\n========== GENERATED EVALUATION PROMPT ==========")
print(prompt)

print("\nPrompt length:", len(prompt), "characters")


print("\n========== RESPONSE VALIDATION TEST ==========")

valid_response = {
    "classification": "sufficient",
    "evidence_chunk_ids": ["POL-GST-006_CHUNK_002"],
    "supported_facts": [
        "Early check-in depends on property availability.",
        "Property approval is required."
    ],
    "missing_information": [
        "Availability for the guest's specific date."
    ],
    "reason": "The policy supports a general explanation.",
    "draft_evidence_present": True
}

validated_result = validate_evidence_evaluation(valid_response)

print("Valid response:", validated_result.classification)
print("Validation: Passed")


invalid_response = {
    "classification": "maybe",
    "evidence_chunk_ids": [],
    "supported_facts": [],
    "missing_information": [],
    "reason": "Invalid classification",
    "draft_evidence_present": False
}

try:
    validate_evidence_evaluation(invalid_response)
except ValidationError:
    print("Invalid response: Rejected")

print("\n========== PYDANTIC JSON SCHEMA ==========")

schema = EvidenceEvaluation.model_json_schema()

import json
print(json.dumps(schema, indent=2))