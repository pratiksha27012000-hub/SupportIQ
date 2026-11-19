
from backend.app.services.chat_service import process_guest_question
from backend.app.memory.conversation_store import (
    get_conversation_history
)


conversation_id = "LIVE-CONTEXT-001"

print("\n========== LIVE CONTEXTUAL RAG TEST ==========")

# FIRST QUESTION
print("\n--- TURN 1: ORIGINAL QUESTION ---")

first_response = process_guest_question(
    question="What happens if I make a duplicate payment?",
    conversation_id=conversation_id,
    audience="Guest"
)

print("Original question:", first_response["question"])

print(
    "Rewriting status:",
    first_response["rag_result"]["rewriting"]["status"]
)

print(
    "Retrieved chunks:",
    len(first_response["rag_result"]["retrieval"]["retrieved_chunks"])
)

print(
    "Production approval:",
    first_response["rag_result"]["approval_assessment"]["status"]
)


# SECOND QUESTION
print("\n--- TURN 2: CONTEXTUAL FOLLOW-UP ---")

second_response = process_guest_question(
    question="What if it is still pending?",
    conversation_id=conversation_id,
    audience="Guest"
)

rag_result = second_response["rag_result"]

print("Original question:", second_response["question"])

print(
    "Rewritten question:",
    rag_result["rewriting"]["rewritten_question"]
)

print(
    "Rewriting status:",
    rag_result["rewriting"]["status"]
)

print("\nRetrieved documents:")

for chunk in rag_result["retrieval"]["retrieved_chunks"][:5]:
    print(
        chunk["document_id"],
        "|",
        chunk["document_name"]
    )

print("\nEvidence classification:")
print(
    rag_result["evidence_assessment"]["classification"]
)

print("\nSupported facts:")
print(
    rag_result["evidence_assessment"]["supported_facts"]
)

print("\nMissing information:")
print(
    rag_result["evidence_assessment"]["missing_information"]
)

print("\nEvaluator reasoning:")
print(
    rag_result["evidence_assessment"]["reason"]
)

print("\nSelected evidence:")
for chunk in rag_result["context"]["selected_chunks"]:
    print("\nDocument:", chunk["document_id"])
    print("Section:", chunk["section"])
    print("Content:", chunk["content"])

print("\nConstraint answers question:")
print(
    rag_result["evidence_assessment"][
        "constraint_answers_question"
    ]
)

print("\nEvidence gate:")
print(rag_result["evidence_gate"])

print("\nProduction approval:")
print(rag_result["approval_assessment"])

print("\nGeneration control:")
print(rag_result["generation_control"])

print("\nGeneration status:")
print(rag_result["generation"]["status"])

print("\nConversation messages saved:")
history = get_conversation_history(conversation_id)

for message in history:
    print(f'{message["role"]}: {message["content"]}')

print("\nTotal messages:", len(history))

print("\n========== TEST COMPLETED ==========")
