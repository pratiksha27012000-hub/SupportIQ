
from backend.app.memory.conversation_store import (
    get_conversation_history,
    save_message
)

conversation_id = "TEST-001"

# Save guest message
save_message(
    conversation_id,
    "user",
    "What happens if I make a duplicate payment?"
)

# Save assistant response
save_message(
    conversation_id,
    "assistant",
    "We verify the transaction and payment status."
)

# Save follow-up question
save_message(
    conversation_id,
    "user",
    "What if it is still pending?"
)

# Retrieve conversation history
history = get_conversation_history(conversation_id)

print("\n========== CONVERSATION MEMORY TEST ==========")

for message in history:
    print(f"{message['role']}: {message['content']}")

print("\nTotal messages:", len(history))
