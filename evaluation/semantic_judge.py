
import os
import json
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel


# Load environment variables
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


# Structured evaluation output
class SemanticEvaluation(BaseModel):

    factual_correctness: Literal[1, 2, 3, 4, 5]

    completeness: Literal[1, 2, 3, 4, 5]

    groundedness: Literal[1, 2, 3, 4, 5]

    citation_support: Literal[1, 2, 3, 4, 5]

    policy_compliance: Literal[1, 2, 3, 4, 5]

    ticketing_compliance: Literal[1, 2, 3, 4, 5]

    overall_verdict: Literal["pass", "review", "fail"]

    issues: list[str]

    rationale: str

    model_config = {
        "extra": "forbid"
    }


def clean_schema(schema):
    """
    Remove schema title fields to improve
    compatibility with Groq structured output.
    """

    if isinstance(schema, dict):
        schema.pop("title", None)

        for value in schema.values():
            clean_schema(value)

    elif isinstance(schema, list):
        for item in schema:
            clean_schema(item)

    return schema


def evaluate_semantic_quality(
    test_case: dict,
    generation_result: dict,
    evidence_chunks: list
):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is not configured.")

    # Prepare evidence
    evidence = []

    for chunk in evidence_chunks:
        evidence.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "document_name": chunk["document_name"],
            "section": chunk["section"],
            "content": chunk["content"]
        })

    # Prepare generated answer and citations
    evaluation_input = {
        "test_case": test_case,
        "generated_answer": generation_result.get("answer"),
        "generation_status": generation_result.get("status"),
        "generation_reason": generation_result.get("reason"),
        "actual_citations": generation_result.get("citations", []),
        "available_evidence": evidence
    }

    prompt = f"""
You are the independent quality evaluator for SupportIQ,
a hospitality customer support AI assistant.

Evaluate the generated answer using ONLY the supplied
test case and evidence.

Do not invent facts or assume that an action was completed.

EVALUATION DIMENSIONS:

1. factual_correctness:
   Are the statements factually supported by the evidence?

2. completeness:
   Does the answer cover the required facts relevant to
   the guest's question?

3. groundedness:
   Does the answer avoid unsupported claims and assumptions?

4. citation_support:
   This dimension is calculated programmatically.
   Do not independently judge citation support.
   Return a score of 5 for this dimension.

5. policy_compliance:
   Does the answer respect the supplied policies,
   restrictions and prohibited claims?

6. ticketing_compliance:
   Does the answer follow the supplied ticketing expectation?
   If no ticketing expectation is provided, score this dimension
   as 5.

SCORING:
5 = Excellent
4 = Good, with minor omissions
3 = Partially correct; meaningful improvement needed
2 = Major issues
1 = Incorrect or unsafe

VERDICT:
- pass: No material factual, grounding or policy issue.
- review: Some omissions or uncertainty require human review.
- fail: Material unsupported, incorrect or policy-violating claims.

IMPORTANT RULES:

- A correct abstention is acceptable when the expected outcome
  is abstain.
- Do not penalise an abstention for missing answer content
  when abstention is the expected outcome.
- Do not reward a fluent answer if its claims are unsupported.
- Do not assume a ticket has been created merely because the
  assistant offered to create one.
- An offer to capture a guest request is different from claiming
  that the request has already been submitted.
- Do not require every evidence chunk to be cited if it does not
  support a fact needed for the answer.
- Explain material omissions and unsupported claims in issues.
- Use the actual evidence, not general hospitality knowledge.

YOUR RESPONSE MUST INCLUDE EVERY FIELD IN THE
REQUIRED JSON SCHEMA.

MANDATORY FIELDS:
- factual_correctness
- completeness
- groundedness
- citation_support
- policy_compliance
- ticketing_compliance
- overall_verdict
- issues
- rationale

The rationale field is mandatory.
It must contain a non-empty explanation of your evaluation.

Never omit a field, even if its value is not applicable.
For non-applicable ticketing, explain that in the rationale.

Return only valid structured JSON.

INPUT:
{json.dumps(evaluation_input, ensure_ascii=False, indent=2)}
"""

    client = Groq(
        api_key=api_key,
        timeout=30,
        max_retries=0
    )

    schema = clean_schema(
        SemanticEvaluation.model_json_schema()
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
            "type": "json_object"
        },
        temperature=0
    )

    response_text = response.choices[0].message.content

    response_data = json.loads(response_text)

    if "rationale" not in response_data:
        response_data["rationale"] = (
            "The evaluator omitted the rationale field. "
            "This assessment requires manual review."
        )
        response_data["overall_verdict"] = "review"

    validated_result = SemanticEvaluation.model_validate(
        response_data
    )

    return validated_result.model_dump()
