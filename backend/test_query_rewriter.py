
from backend.app.rag.query_rewriter import (
    rewrite_follow_up_question
)


conversation_history = [
    {
        "role": "user",
        "content": "What happens if I make a duplicate payment?"
    },
    {
        "role": "assistant",
        "content": (
            "We verify the transaction and payment status "
            "before classifying it."
        )
    }
]

follow_up_question = "What if it is still pending?"

rewritten_question = rewrite_follow_up_question(
    question=follow_up_question,
    conversation_history=conversation_history
)

print("\n========== QUERY REWRITING TEST ==========")
print("Original question:", follow_up_question)
print("Rewritten question:", rewritten_question)
print("==========================================")
