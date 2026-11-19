
from backend.app.rag.pipeline import run_rag_pipeline

from backend.app.memory.conversation_store import (
    get_conversation_history,
    save_message
)


def process_guest_question(
    question: str,
    conversation_id: str,
    audience: str
):
    # 1. Retrieve previous conversation history
    history = [
        message.copy()
        for message in get_conversation_history(conversation_id)
    ]

    # 2. Save the latest guest question
    save_message(
        conversation_id=conversation_id,
        role="user",
        content=question
    )

    # 3. Process question with conversation context
    rag_result = run_rag_pipeline(
        question=question,
        audience=audience,
        conversation_history=history
    )

    # 4. Extract generated answer
    generation = rag_result.get("generation", {})
    answer = generation.get("answer")

    # 5. Save assistant response
    if answer:
        save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer
        )

    # 6. Retrieve updated history
    updated_history = get_conversation_history(conversation_id)

    return {
        "conversation_id": conversation_id,
        "question": question,
        "audience": audience,
        "conversation_history": updated_history,
        "rag_result": rag_result
    }
