
import json
from pathlib import Path

from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks
from backend.app.rag.reranker import rerank_chunks

PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_CASES_FILE = (
    PROJECT_ROOT / "evaluation" / "confidence_test_cases.json"
)

with open(TEST_CASES_FILE, "r", encoding="utf-8") as file:
    test_cases = json.load(file)

print("\n========== CONFIDENCE EVALUATION ==========\n")

for index, test_case in enumerate(test_cases, start=1):

    question = test_case["query"]
    expected_outcome = test_case["expected_outcome"]
    expected_document_id = test_case["expected_document_id"]
    expected_chunk_ids = test_case["expected_relevant_chunk_ids"]

    retrieval_result = retrieve_hybrid_chunks(
        question=question,
        audience="Guest",
        top_k=10,
        candidate_k=10
    )

    reranked_chunks = rerank_chunks(
        question=question,
        retrieved_chunks=retrieval_result["retrieved_chunks"],
        top_k=5
    )

    retrieved_chunk_ids = [
        chunk["chunk_id"] for chunk in reranked_chunks
    ]

    retrieved_document_ids = [
        chunk["document_id"] for chunk in reranked_chunks
    ]

    print(f"\nTest Case: {index}")
    print("Question:", question)
    print("Expected outcome:", expected_outcome)

    print("\nTop 5 candidate scores:")

    for rank, chunk in enumerate(reranked_chunks, start=1):
        print(
            rank,
            chunk["chunk_id"],
            round(chunk["reranker_score"], 4)
        )
        print("Content:", chunk["content"])

    if expected_document_id:
        document_match = (
            expected_document_id in retrieved_document_ids
        )
        print("\nExpected document found:", document_match)

    if expected_chunk_ids:

        matching_chunks = [
            chunk_id for chunk_id in expected_chunk_ids
            if chunk_id in retrieved_chunk_ids
        ]

        print("\nExpected relevant chunks:", expected_chunk_ids)
        print("Retrieved relevant chunks:", matching_chunks)
        print("Relevant evidence found:", len(matching_chunks) > 0)

        if matching_chunks:
            rank = retrieved_chunk_ids.index(matching_chunks[0]) + 1
            print("Relevant evidence rank:", rank)

        expected_evidence_scores = [
            chunk["reranker_score"]
            for chunk in reranked_chunks
            if chunk["chunk_id"] in expected_chunk_ids
        ]

        if expected_evidence_scores:
            print(
                "Best expected evidence score:",
                round(max(expected_evidence_scores), 4)
            )
        else:
            print("Expected evidence score: Not retrieved")

    else:
        print("\nExpected supporting chunks: None")
        print("Retrieved candidate chunks:", len(retrieved_chunk_ids))
        print(
            "Abstention validation:",
            "Requires a separate evidence/confidence decision"
        )

    print("-" * 55)

print("\n========== EVALUATION COMPLETE ==========")
