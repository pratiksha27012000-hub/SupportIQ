
import json
from pathlib import Path

from backend.app.rag.generator import generate_answer


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "enriched_chunks.jsonl"
)

test_cases = [
    {
        "question": "What happens if I make a duplicate payment?",
        "chunk_ids": [
            "SOP-004_CHUNK_001",
            "SOP-004_CHUNK_002",
            "POL-GST-004_CHUNK_001"
        ]
    },
    {
        "question": "Can you arrange airport pickup for me?",
        "chunk_ids": [
            "KB-001_CHUNK_002",
            "KB-001_CHUNK_005"
        ]
    },
    {
        "question": "Can you guarantee me a complimentary room upgrade?",
        "chunk_ids": [
            "POL-GST-008_CHUNK_004"
        ]
    }
]


# Load all enriched chunks
all_chunks = {}

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        chunk = json.loads(line)
        chunk["content"] = chunk["text"]
        all_chunks[chunk["chunk_id"]] = chunk


for index, test_case in enumerate(test_cases, start=1):

    question = test_case["question"]

    selected_chunks = [
        all_chunks[chunk_id]
        for chunk_id in test_case["chunk_ids"]
        if chunk_id in all_chunks
    ]

    print("\n" + "=" * 65)
    print(f"TEST CASE {index}")
    print("=" * 65)

    print("Question:", question)
    print("Evidence chunks:", len(selected_chunks))

    if not selected_chunks:
        print("ERROR: No matching evidence chunks found.")
        continue

    result = generate_answer(
        question=question,
        retrieved_chunks=selected_chunks
    )

    print("\nStatus:", result["status"])
    print("Answer:", result["answer"])
    print("Reason:", result["reason"])

    print("\nCITATIONS:")

    for citation in result["citations"]:
        print(
            citation["chunk_id"],
            "|",
            citation["document_name"],
            "|",
            citation["section"]
        )

print("\n" + "=" * 65)
print("ALL GENERATOR TESTS COMPLETED")
print("=" * 65)
