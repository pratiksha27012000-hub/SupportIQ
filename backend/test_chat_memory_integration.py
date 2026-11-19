
from unittest.mock import patch

from backend.app.services.chat_service import process_guest_question
from backend.app.memory.conversation_store import (
    get_conversation_history
)


conversation_id = "INTEGRATION-001"

# Mock the RAG pipeline so this test does not call Groq
mock_result = {
    "generation": {
        "answer": "We verify the payment status before classifying it."
    }
}

with patch(
    "backend.app.services.chat_service.run_rag_pipeline",
    return_value=mock_result
):
    response = process_guest_question(
        question="What happens if I make a duplicate payment?",
        conversation_id=conversation_id,
        audience="Guest"
    )

history = get_conversation_history(conversation_id)

print("\n========== CHAT MEMORY INTEGRATION TEST ==========")

print("Conversation ID:", response["conversation_id"])

for message in history:
    print(f"{message['role']}: {message['content']}")

print("\nTotal messages:", len(history))

assert len(history) == 2
assert history[0]["role"] == "user"
assert history[1]["role"] == "assistant"

print("\nTEST PASSED!")
