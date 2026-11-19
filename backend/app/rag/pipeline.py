
from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks
from backend.app.rag.reranker import rerank_chunks
from backend.app.rag.context_builder import build_context

from backend.app.rag.evidence_evaluator import (
    evaluate_evidence_with_groq
)

from backend.app.rag.evidence_gate import evaluate_evidence
from backend.app.rag.generator import generate_answer

from backend.app.rag.query_rewriter import (
    rewrite_follow_up_question
)


def run_rag_pipeline(
    question: str,
    audience: str = "Guest",
    conversation_history: list = None
):

    # 1. Query Rewriting
    retrieval_question = question

    rewriting_result = {
        "original_question": question,
        "rewritten_question": question,
        "status": "not_required"
    }

    if conversation_history:
        try:
            retrieval_question = rewrite_follow_up_question(
                question=question,
                conversation_history=conversation_history
            )

            rewriting_result = {
                "original_question": question,
                "rewritten_question": retrieval_question,
                "status": "success"
            }

        except Exception as error:
            rewriting_result = {
                "original_question": question,
                "rewritten_question": question,
                "status": "fallback",
                "reason": str(error)
            }

    # 2. Hybrid Retrieval
    retrieval_result = retrieve_hybrid_chunks(
        question=retrieval_question,
        audience=audience,
        top_k=10,
        candidate_k=10
    )

    # 3. Reranking
    reranked_chunks = rerank_chunks(
        question=retrieval_question,
        retrieved_chunks=retrieval_result["retrieved_chunks"],
        top_k=5
    )

    # 4. Context Building
    context_result = build_context(
        question=retrieval_question,
        reranked_chunks=reranked_chunks,
        audience=audience
    )

    selected_chunks = context_result["selected_chunks"]

    # 5. Evidence Evaluation
    evidence_result = evaluate_evidence_with_groq(
        question=retrieval_question,
        selected_chunks=selected_chunks
    )

    evidence_result = evidence_result.model_dump()

    # 6. Evidence Sufficiency Gate
    evidence_gate_result = evaluate_evidence(
        evidence_classification=evidence_result["classification"],
        constraint_answers_question=evidence_result[
            "constraint_answers_question"
        ]
    )

    # 7. Independent Document Approval Check
    unapproved_chunks = [
        chunk for chunk in selected_chunks
        if chunk.get("status") != "Approved"
    ]

    approval_passed = (
        len(selected_chunks) > 0
        and len(unapproved_chunks) == 0
    )

    approval_result = {
        "approved": approval_passed,
        "unapproved_chunk_ids": [
            chunk["chunk_id"]
            for chunk in unapproved_chunks
        ],
        "status": (
            "approved"
            if approval_passed
            else "blocked"
        ),
        "reason": (
            "All selected evidence documents are approved."
            if approval_passed
            else (
                "No evidence chunks were selected."
                if not selected_chunks
                else "Retrieved evidence contains documents "
                     "that are not Approved."
            )
        )
    }

    # 8. Combined Generation Decision
    generation_allowed = (
        evidence_gate_result["allow_generation"]
        and approval_result["approved"]
    )

    if generation_allowed:

        generation_result = generate_answer(
            question=retrieval_question,
            retrieved_chunks=selected_chunks,
            evidence_assessment=evidence_result
        )

    else:

        if not evidence_gate_result["allow_generation"]:
            block_reason = evidence_gate_result["reason"]
            block_status = evidence_gate_result["decision"]

        else:
            block_reason = approval_result["reason"]
            block_status = "block"

        generation_result = {
            "question": retrieval_question,
            "answer": None,
            "citations": context_result["citations"],
            "status": block_status,
            "reason": block_reason
        }

    # 9. Temporary RAG Diagnostics
    print("\n" + "=" * 60)
    print("SUPPORTIQ RAG DIAGNOSTICS")
    print("=" * 60)

    print("\n1. ORIGINAL QUESTION:")
    print(question)

    print("\n2. REWRITTEN QUESTION:")
    print(retrieval_question)

    print("\n3. HYBRID RETRIEVAL:")
    for chunk in retrieval_result["retrieved_chunks"]:
        print(
            chunk.get("chunk_id"),
            "|",
            chunk.get("document_name")
        )

    print("\n4. RERANKED CHUNKS:")
    for chunk in reranked_chunks:
        print(
            chunk.get("chunk_id"),
            "|",
            chunk.get("document_name")
        )

    print("\n5. SELECTED CONTEXT:")
    for chunk in selected_chunks:
        print(
            chunk.get("chunk_id"),
            "|",
            chunk.get("document_name"),
            "| Status:",
            chunk.get("status")
        )

    print("\n6. EVIDENCE ASSESSMENT:")
    print(evidence_result)

    print("\n7. EVIDENCE GATE:")
    print(evidence_gate_result)

    print("\n8. APPROVAL ASSESSMENT:")
    print(approval_result)

    print("\n9. GENERATION DECISION:")
    print(generation_allowed)

    print("\n10. GENERATION RESULT:")
    print(generation_result)

    print("=" * 60 + "\n")

    # 10. Return Complete Pipeline Result
    return {
        "question": question,

        "rewriting": rewriting_result,

        "audience": audience,

        "retrieval": retrieval_result,

        "reranking": {
            "reranked_chunks": reranked_chunks,
            "status": "success"
        },

        "context": context_result,

        "evidence_assessment": evidence_result,

        "evidence_gate": evidence_gate_result,

        "approval_assessment": approval_result,

        "generation_control": {
            "allowed": generation_allowed,
            "status": (
                "allowed"
                if generation_allowed
                else "blocked"
            )
        },

        "generation": generation_result
    }
