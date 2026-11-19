
import json
from pathlib import Path

from backend.app.rag.generator import generate_answer
from evaluation.semantic_judge import evaluate_semantic_quality


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_CASES_FILE = (
    PROJECT_ROOT / "evaluation" / "generation_test_cases.json"
)

CHUNKS_FILE = (
    PROJECT_ROOT / "knowledge_base" / "processed" / "enriched_chunks.jsonl"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "evaluation" / "generation_evaluation_results.json"
)


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_chunks():
    chunks = []

    with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                chunks.append(json.loads(line))

    return {
        chunk["chunk_id"]: chunk
        for chunk in chunks
    }


def prepare_evidence(chunk_ids, chunk_registry):
    evidence = []

    for chunk_id in chunk_ids:
        chunk = chunk_registry.get(chunk_id)

        if chunk is None:
            raise ValueError(
                f"Evidence chunk not found: {chunk_id}"
            )

        evidence.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "document_name": chunk["document_name"],
            "section": chunk["section"],
            "content": chunk["text"]
        })

    return evidence


def calculate_citation_score(
    missing_expected_citations,
    unexpected_citations
):
    """
    Citation scoring is deterministic.
    It does not require an LLM call.
    """

    if unexpected_citations:
        return 1

    if missing_expected_citations:
        return 3

    return 5


def evaluate_test_case(test_case, chunk_registry):

    # 1. Prepare evidence
    evidence = prepare_evidence(
        test_case["evidence_chunk_ids"],
        chunk_registry
    )

    # 2. Generate guest answer
    generation_result = generate_answer(
        question=test_case["query"],
        retrieved_chunks=evidence
    )

    answer = generation_result.get("answer") or ""

    actual_outcome = generation_result.get("status")
    expected_outcome = test_case["expected_outcome"]

    # 3. Validate expected outcome
    outcome_match = actual_outcome == expected_outcome

    # 4. Validate citations
    actual_citations = {
        item["chunk_id"]
        for item in generation_result.get("citations", [])
    }

    expected_citations = set(
        test_case.get("expected_citations", [])
    )

    supplied_evidence_ids = set(
        test_case["evidence_chunk_ids"]
    )

    missing_expected_citations = sorted(
        expected_citations - actual_citations
    )

    unexpected_citations = sorted(
        actual_citations - supplied_evidence_ids
    )

    citation_coverage = (
        len(expected_citations & actual_citations)
        / len(expected_citations)
        if expected_citations
        else 1.0
    )

    # 5. Check prohibited exact phrases
    prohibited_phrases_found = [
        phrase
        for phrase in test_case.get("prohibited_claims", [])
        if phrase.lower() in answer.lower()
    ]

    # 6. Calculate citation score using Python
    citation_score = calculate_citation_score(
        missing_expected_citations,
        unexpected_citations
    )

    # 7. Run semantic evaluation
    semantic_result = evaluate_semantic_quality(
        test_case=test_case,
        generation_result=generation_result,
        evidence_chunks=evidence
    )

    # Override LLM citation score with deterministic score
    semantic_result["citation_support"] = citation_score

    # 8. Return evaluation
    return {
        "test_id": test_case["test_id"],
        "query": test_case["query"],

        "expected_outcome": expected_outcome,
        "actual_outcome": actual_outcome,
        "outcome_match": outcome_match,

        "citations_valid": len(unexpected_citations) == 0,
        "expected_citation_coverage": round(
            citation_coverage, 2
        ),

        "citation_support_score": citation_score,
        "missing_expected_citations": missing_expected_citations,
        "unexpected_citations": unexpected_citations,

        "prohibited_exact_phrases_found": prohibited_phrases_found,

        "answer": answer,
        "reason": generation_result.get("reason"),

        "semantic_evaluation": semantic_result,

        "manual_review_status": "Pending"
    }


def main():

    test_cases = load_json(TEST_CASES_FILE)
    chunk_registry = load_chunks()

    results = []

    print("\n========== SUPPORTIQ GENERATION EVALUATION ==========")
    print("Test cases:", len(test_cases))
    print("Available evidence chunks:", len(chunk_registry))

    for test_case in test_cases:

        print("\nRunning:", test_case["test_id"])

        try:
            result = evaluate_test_case(
                test_case,
                chunk_registry
            )

            results.append(result)

            print("Expected outcome:", result["expected_outcome"])
            print("Actual outcome:", result["actual_outcome"])
            print("Outcome match:", result["outcome_match"])

            print("Citations valid:", result["citations_valid"])

            print(
                "Citation coverage:",
                result["expected_citation_coverage"]
            )

            print(
                "Citation support score:",
                result["citation_support_score"]
            )

            print("\nSemantic evaluation:")

            semantic = result["semantic_evaluation"]

            for dimension in [
                "factual_correctness",
                "completeness",
                "groundedness",
                "citation_support",
                "policy_compliance",
                "ticketing_compliance"
            ]:
                print(
                    f"{dimension}: {semantic[dimension]}/5"
                )

            print("Semantic verdict:", semantic["overall_verdict"])
            print("Semantic issues:", semantic["issues"])
            print("Answer:", result["answer"])

        except Exception as error:

            print("EVALUATION FAILED:", str(error))

            results.append({
                "test_id": test_case["test_id"],
                "query": test_case["query"],
                "evaluation_status": "error",
                "error": str(error)
            })

    # 9. Calculate summary
    successful_results = [
        result
        for result in results
        if result.get("evaluation_status") != "error"
    ]

    total = len(test_cases)
    successful_count = len(successful_results)

    outcome_matches = sum(
        result.get("outcome_match", False)
        for result in successful_results
    )

    valid_citations = sum(
        result.get("citations_valid", False)
        for result in successful_results
    )

    semantic_passes = sum(
        result.get("semantic_evaluation", {}).get(
            "overall_verdict"
        ) == "pass"
        for result in successful_results
    )

    summary = {
        "total_tests": total,
        "successful_evaluations": successful_count,
        "failed_evaluations": total - successful_count,

        "outcome_matches": outcome_matches,
        "valid_citations": valid_citations,
        "semantic_passes": semantic_passes,

        "outcome_match_rate": round(
            outcome_matches / successful_count, 2
        ) if successful_count else 0,

        "valid_citation_rate": round(
            valid_citations / successful_count, 2
        ) if successful_count else 0,

        "semantic_pass_rate": round(
            semantic_passes / successful_count, 2
        ) if successful_count else 0,

        "manual_review_required": True,
        "results": results
    }

    # 10. Save results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            summary,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n========== FINAL EVALUATION SUMMARY ==========")

    print("Total tests:", total)
    print("Successful evaluations:", successful_count)
    print("Failed evaluations:", total - successful_count)

    print("Outcome match rate:", summary["outcome_match_rate"])
    print("Valid citation rate:", summary["valid_citation_rate"])
    print("Semantic pass rate:", summary["semantic_pass_rate"])

    print("Manual review required: Yes")
    print("Results saved to:", OUTPUT_FILE)

    print("===============================================")


if __name__ == "__main__":
    main()
