
from datetime import datetime, timezone


# Temporary in-memory storage
conversation_memory = {}


def get_conversation_history(conversation_id: str):
    """
    Retrieves previous messages for a conversation.
    """

    return conversation_memory.get(conversation_id, [])


def save_message(
    conversation_id: str,
    role: str,
    content: str
):
    """
    Saves a guest or assistant message.
    """

    if conversation_id not in conversation_memory:
        conversation_memory[conversation_id] = []

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    conversation_memory[conversation_id].append(message)

    return message
