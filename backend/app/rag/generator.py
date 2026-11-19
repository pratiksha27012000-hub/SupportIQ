
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


def generate_answer(
    question: str,
    retrieved_chunks: list,
    evidence_assessment=None
):

    # 1. Check whether evidence exists
    if not retrieved_chunks:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "abstain",
            "reason": "No evidence was provided."
        }

    # 2. Check API configuration
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "generation_error",
            "reason": "Groq API key is not configured."
        }

    # 3. Read the evidence assessment
    if evidence_assessment is None:
        assessment = {}
    elif hasattr(evidence_assessment, "model_dump"):
        assessment = evidence_assessment.model_dump()
    elif isinstance(evidence_assessment, dict):
        assessment = evidence_assessment
    else:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "generation_error",
            "reason": "Invalid evidence assessment format."
        }

    classification = assessment.get("classification")

    supported_facts = assessment.get("supported_facts", [])
    missing_information = assessment.get("missing_information", [])
    evidence_chunk_ids = assessment.get("evidence_chunk_ids", [])

    if classification not in {
        "sufficient",
        "partial",
        "constraint_only"
    }:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "abstain",
            "reason": "Evidence assessment does not permit generation."
        }

    # 4. Validate assessment evidence IDs against supplied chunks
    available_chunks = {
        chunk["chunk_id"]: chunk
        for chunk in retrieved_chunks
        if chunk.get("chunk_id")
    }

    invalid_ids = set(evidence_chunk_ids) - set(available_chunks)

    if invalid_ids:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "generation_error",
            "reason": "Evidence assessment contains invalid chunk references."
        }

    if not evidence_chunk_ids or not supported_facts:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "abstain",
            "reason": "No validated supporting facts are available."
        }

    # 5. Prepare only evidence identified by the evaluator
    evidence = []

    for chunk_id in evidence_chunk_ids:
        chunk = available_chunks[chunk_id]

        evidence.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk.get("document_id"),
            "document_name": chunk.get("document_name"),
            "section": chunk.get("section"),
            "content": chunk.get("content")
        })

    # 6. Prepare generation instructions
    if classification == "partial":
        response_instruction = """
This is a PARTIAL answer.

You MUST:
1. Answer the parts supported by supported_facts.
2. Clearly explain which requested information cannot
   currently be confirmed.
3. Use missing_information to identify what remains unknown.
4. Do not guess or fill information gaps.
5. Offer human assistance for the unresolved parts.
6. Do not claim that a ticket has already been created.
"""
    elif classification == "constraint_only":
        response_instruction = """
This answer is based on a policy constraint.

You MUST:
1. Explain the supported policy restriction clearly.
2. Do not imply that an outcome beyond the restriction
   has been confirmed.
3. Offer human assistance where further investigation
   is needed.
"""
    else:
        response_instruction = """
All material parts of the question are supported.

Provide a complete answer using only the supported facts.
"""

    prompt = f"""
You are SupportIQ, a hospitality customer support assistant.

Your task is to answer the guest using only the
evidence and assessment supplied below.

STRICT RULES:

1. Use only information supported by the supplied evidence.
2. Treat supported_facts as the facts approved for use
   by the evidence evaluator.
3. Do not invent policies, fees, timelines, eligibility,
   availability, exceptions or outcomes.
4. Do not replace missing information with general
   hospitality knowledge.
5. Clearly distinguish confirmed information from
   information that cannot be confirmed.
6. Do not promise refunds, upgrades, bookings,
   compensation or completed transactions.
7. Do not claim that an agent or department has been
   contacted or assigned.
8. Do not claim that a support ticket has already
   been created.
9. Do not expose internal document IDs or technical
   assessment details to the guest.
10. Use polite, natural and concise language.
11. If information is missing, explain the limitation
    honestly.
12. When appropriate, offer to create a support request
    for human investigation. Do not claim it is created.
13. Do not introduce operational steps that are not
    supported by the supplied evidence.
14. Do not include unsupported information merely
    to make the response sound more complete.

RESPONSE INSTRUCTIONS:

{response_instruction}

EVIDENCE ASSESSMENT:

{json.dumps({
    "classification": classification,
    "supported_facts": supported_facts,
    "missing_information": missing_information
}, ensure_ascii=False, indent=2)}

AVAILABLE EVIDENCE:

{json.dumps(evidence, ensure_ascii=False, indent=2)}

GUEST QUESTION:

{question}

Return:
- answer: the guest-facing response.
- used_chunk_ids: IDs of evidence chunks actually used.

Return only valid structured output.
"""

    # 7. Call Groq
    try:
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
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "supportiq_answer",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string"
                            },
                            "used_chunk_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": [
                            "answer",
                            "used_chunk_ids"
                        ],
                        "additionalProperties": False
                    }
                }
            },
            temperature=0
        )

        response_text = response.choices[0].message.content

        if not response_text:
            raise ValueError("Groq returned an empty response.")

        result = json.loads(response_text)

        answer = result["answer"].strip()
        used_chunk_ids = result["used_chunk_ids"]

        # 8. Validate citations against available evidence
        valid_chunk_ids = list(dict.fromkeys(
            chunk_id
            for chunk_id in used_chunk_ids
            if chunk_id in available_chunks
            and chunk_id in evidence_chunk_ids
        ))

        if not answer or not valid_chunk_ids:
            return {
                "question": question,
                "answer": None,
                "citations": [],
                "status": "abstain",
                "reason": (
                    "The generated answer did not contain "
                    "valid supporting evidence references."
                )
            }

        # 9. Build citations from our own evidence records
        citations = []

        for chunk_id in valid_chunk_ids:
            chunk = available_chunks[chunk_id]

            citations.append({
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk.get("document_id"),
                "document_name": chunk.get("document_name"),
                "section": chunk.get("section")
            })

        # 10. Return the correct generation status
        generation_status = (
            "partial_answer"
            if classification == "partial"
            else "answer"
        )

        return {
            "question": question,
            "answer": answer,
            "citations": citations,
            "status": generation_status,
            "reason": None
        }

    except Exception as error:
        return {
            "question": question,
            "answer": None,
            "citations": [],
            "status": "generation_error",
            "reason": str(error)
        }
