
from unittest.mock import patch

from backend.app.services.chat_service import process_guest_question
from backend.app.memory.conversation_store import (
    get_conversation_history
)


conversation_id = "CONTEXT-TEST-001"

mock_result = {
    "generation": {
        "answer": "We verify the payment status before classifying it."
    }
}

# First guest question
with patch(
    "backend.app.services.chat_service.run_rag_pipeline",
    return_value=mock_result
) as mock_pipeline:

    first_response = process_guest_question(
        question="What happens if I make a duplicate payment?",
        conversation_id=conversation_id,
        audience="Guest"
    )

    # Second guest question
    second_response = process_guest_question(
        question="What if it is still pending?",
        conversation_id=conversation_id,
        audience="Guest"
    )

    # Inspect what was passed to the RAG pipeline
    second_call = mock_pipeline.call_args_list[1]

    print("\n========== CONTEXTUAL CHAT TEST ==========")

    print("Second question:", second_call.kwargs["question"])

    print("\nConversation history passed to RAG:")
    for message in second_call.kwargs["conversation_history"]:
        print(f"{message['role']}: {message['content']}")

    print("\nMessages saved:")
    history = get_conversation_history(conversation_id)

    for message in history:
        print(f"{message['role']}: {message['content']}")

    print("\nTotal saved messages:", len(history))

    assert len(history) == 4
    assert len(second_call.kwargs["conversation_history"]) == 2

    print("\nTEST PASSED!")
