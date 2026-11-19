
import json
from getpass import getpass
from groq import Groq

from backend.app.rag.evidence_evaluator import (
    EvidenceEvaluation,
    build_evidence_evaluation_prompt
)

# 1. Securely collect API key
api_key = getpass("Paste your Groq API key: ")

client = Groq(
    api_key=api_key,
    timeout=30,
    max_retries=0
)

# 2. Generate Pydantic JSON schema
schema = EvidenceEvaluation.model_json_schema()

# Remove descriptive title fields from nested schema
def clean_schema(value):
    if isinstance(value, dict):
        return {
            key: clean_schema(item)
            for key, item in value.items()
            if key != "title"
        }
    if isinstance(value, list):
        return [clean_schema(item) for item in value]
    return value

schema = clean_schema(schema)

# 3. Prepare test evidence
sample_chunks = [
    {
        "chunk_id": "POL-GST-006_CHUNK_002",
        "document_id": "POL-GST-006",
        "document_name": "Early Check-in & Late Check-out Policy",
        "section": "Policy rules",
        "audience": "Guest",
        "status": "Draft",
        "content": (
            "Early check-in is subject to property availability "
            "and approval. It is not guaranteed."
        )
    }
]

prompt = build_evidence_evaluation_prompt(
    question="What is the early check-in policy?",
    selected_chunks=sample_chunks
)

# 4. Call Groq with strict JSON schema
print("\nTesting Groq Structured Outputs...")

try:
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

    result = response.choices[0].message.content

    print("\n========== GROQ RESPONSE ==========")
    print(result)

    # 5. Validate with Pydantic
    parsed_result = json.loads(result)

    validated = EvidenceEvaluation.model_validate(
        parsed_result
    )

    print("\n========== VALIDATION ==========")
    print("Classification:", validated.classification)
    print("Evidence IDs:", validated.evidence_chunk_ids)
    print("Draft evidence:", validated.draft_evidence_present)
    print("Pydantic validation: SUCCESS")

except Exception as error:
    print("\nError:", str(error))
    print("Structured output test: FAILED")
