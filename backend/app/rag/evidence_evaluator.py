
from typing import Literal
from pydantic import BaseModel, Field
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq


class EvidenceEvaluation(BaseModel):

    classification: Literal[
        "sufficient",
        "partial",
        "constraint_only",
        "insufficient"
    ]

    constraint_answers_question: bool = Field(
        description=(
            "True only when a policy restriction itself directly "
            "answers the guest's actual question. False otherwise."
        )
    )

    evidence_chunk_ids: list[str]

    supported_facts: list[str]

    missing_information: list[str]

    reason: str

    draft_evidence_present: bool

    model_config = {
        "extra": "forbid"
    }


def prepare_evidence_input(
    question: str,
    selected_chunks: list
):
    evidence_items = []

    for chunk in selected_chunks:
        evidence_items.append({
            "chunk_id": chunk.get("chunk_id"),
            "document_id": chunk.get("document_id"),
            "document_name": chunk.get("document_name"),
            "section": chunk.get("section"),
            "audience": chunk.get("audience"),
            "status": chunk.get("status"),
            "content": chunk.get("content")
        })

    return {
        "question": question,
        "evidence": evidence_items
    }


def build_evidence_evaluation_prompt(
    question: str,
    selected_chunks: list
):
    prepared_input = prepare_evidence_input(
        question=question,
        selected_chunks=selected_chunks
    )

    return f"""
You are the Evidence Evaluator for SupportIQ,
a hospitality AI assistant.

Your responsibility is to assess exactly what the
supplied evidence allows SupportIQ to tell the guest.

IMPORTANT PRINCIPLE:

Do not treat a question as entirely unanswerable merely
because some requested information is missing.

SupportIQ should answer supported parts of a question,
clearly identify missing information, and offer human
assistance for the unsupported parts.

EVALUATION RULES:

1. Use only the supplied evidence.
2. Never invent facts, policy details, timelines,
   eligibility conditions, or outcomes.
3. Distinguish direct evidence from loosely related text.
4. Identify every material part of the guest's question.
5. Assess each part independently.
6. Include only directly supported information in supported_facts.
7. Record unanswered material parts in missing_information.
8. Do not assume that general troubleshooting guidance
   establishes a specific policy outcome.
9. Assess semantic evidence sufficiency independently
   of document approval status.
10. A Draft document may contain semantically relevant
    information, but it is not approved for production use.
11. Set draft_evidence_present to true whenever any
    supplied evidence document has Draft status.
12. Production approval is evaluated separately.

CLASSIFICATION:

- sufficient:
  All material parts of the guest's question are
  directly supported by the supplied evidence.

- partial:
  At least one meaningful part of the question is
  supported, but one or more material details or
  requested outcomes remain unsupported or unknown.

- constraint_only:
  Evidence contains a relevant policy restriction,
  but does not otherwise establish the requested
  information or outcome.

- insufficient:
  The supplied evidence does not meaningfully support
  answering any part of the question.

PARTIAL ANSWER RULES:

1. Use partial when some useful information can safely
   be provided, even if the complete question cannot
   be answered.

2. Put every supported answerable fact in supported_facts.

3. Put every material unanswered detail in
   missing_information.

4. Do not turn missing information into assumptions.

5. If the guest asks multiple questions, assess each
   requested outcome separately.

6. A general instruction to contact support does not
   prove refund eligibility, refund approval, or a
   processing timeline.

7. If the evidence supports an investigation process
   but not its eventual outcome, classify as partial
   when useful supported guidance can be provided.

8. If no meaningful answer can be given, use
   insufficient rather than partial.

CONSTRAINT ANSWERABILITY RULES:

1. Evaluate constraint_answers_question separately.
2. Set it to true ONLY when the policy restriction
   itself directly answers the guest's actual question.
3. Example:
   Guest asks: "Can you guarantee a complimentary upgrade?"
   Evidence says upgrades require authorised approval
   and cannot be guaranteed.
   Classification: constraint_only.
   constraint_answers_question: true.

4. Example:
   Guest asks: "Am I eligible for a refund?"
   Evidence says payment status must be verified but
   does not establish refund eligibility.
   Classification: constraint_only if no other useful
   answerable information exists.
   constraint_answers_question: false.

5. For sufficient, partial and insufficient,
   constraint_answers_question must be false.

EVIDENCE ID RULES:

1. evidence_chunk_ids must contain only IDs supplied
   in the retrieved evidence.
2. Include only chunks that directly support the
   assessment.
3. Never invent or modify chunk IDs.

OUTPUT REQUIREMENTS:

Return:
- classification
- constraint_answers_question
- evidence_chunk_ids
- supported_facts
- missing_information
- reason
- draft_evidence_present

Return only information supported by the supplied evidence.

GUEST QUESTION AND RETRIEVED EVIDENCE:

{json.dumps(prepared_input, indent=2)}
"""


def validate_evidence_evaluation(
    response: dict,
    selected_chunks: list
):
    validated_result = EvidenceEvaluation.model_validate(response)

    valid_chunk_ids = {
        chunk.get("chunk_id")
        for chunk in selected_chunks
        if chunk.get("chunk_id")
    }

    returned_chunk_ids = validated_result.evidence_chunk_ids

    invalid_ids = set(returned_chunk_ids) - valid_chunk_ids

    if invalid_ids:
        raise ValueError(
            f"Evidence evaluator returned unknown chunk IDs: "
            f"{sorted(invalid_ids)}"
        )

    if len(returned_chunk_ids) != len(set(returned_chunk_ids)):
        raise ValueError(
            "Evidence evaluator returned duplicate chunk IDs."
        )

    if (
        validated_result.classification
        in {"sufficient", "partial", "constraint_only"}
        and not returned_chunk_ids
    ):
        raise ValueError(
            "Evidence classification requires supporting chunk IDs."
        )

    if (
        validated_result.classification == "partial"
        and (
            not validated_result.supported_facts
            or not validated_result.missing_information
        )
    ):
        raise ValueError(
            "Partial classification requires both supported facts "
            "and missing information."
        )

    if (
        validated_result.classification == "insufficient"
        and validated_result.supported_facts
    ):
        raise ValueError(
            "Insufficient classification cannot contain supported facts."
        )

    return validated_result


# Load environment variables from project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

load_dotenv(PROJECT_ROOT / ".env")


def evaluate_evidence_with_groq(
    question: str,
    selected_chunks: list
):
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found in environment."
        )

    client = Groq(
        api_key=api_key,
        timeout=30,
        max_retries=0
    )

    prompt = build_evidence_evaluation_prompt(
        question=question,
        selected_chunks=selected_chunks
    )

    schema = EvidenceEvaluation.model_json_schema()

    def clean_schema(value):
        if isinstance(value, dict):
            return {
                key: clean_schema(item)
                for key, item in value.items()
                if key != "title"
            }

        if isinstance(value, list):
            return [
                clean_schema(item)
                for item in value
            ]

        return value

    schema = clean_schema(schema)

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
                "name": "evidence_evaluation",
                "strict": True,
                "schema": schema
            }
        },
        temperature=0
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError(
            "Evidence evaluator returned an empty response."
        )

    response_data = json.loads(response_text)

    validated_result = validate_evidence_evaluation(
        response=response_data,
        selected_chunks=selected_chunks
    )

    return validated_result
