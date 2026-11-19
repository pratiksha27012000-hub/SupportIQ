
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def rewrite_follow_up_question(
    question: str,
    conversation_history: list
):
    """
    Converts a contextual follow-up into a standalone question.
    """

    # No history means no rewriting is needed
    if not conversation_history:
        return question

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("Groq API key is not configured.")

    # Prepare recent conversation history
    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation_history[-6:]
    )

    prompt = f"""
You are a query rewriting assistant for SupportIQ.

Your task is to convert the latest guest question
into a standalone question using conversation history.

RULES:
1. Preserve the guest's original intent.
2. Resolve references such as it, they, that and this.
3. Do not answer the question.
4. Do not add new facts or assumptions.
5. If the question is already standalone, return it unchanged.
6. Return only the rewritten question.

CONVERSATION HISTORY:
{history_text}

LATEST QUESTION:
{question}
"""

    client = Groq(
        api_key=api_key,
        timeout=30,
        max_retries=0
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    rewritten_question = (
        response.choices[0].message.content.strip()
    )

    return rewritten_question
