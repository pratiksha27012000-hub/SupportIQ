
from backend.app.rag.retriever import retrieve_relevant_chunks
from backend.app.rag.keyword_retriever import retrieve_keyword_chunks


def retrieve_hybrid_chunks(
    question: str,
    audience: str = "Guest",
    top_k: int = 5,
    candidate_k: int = 10,
    rrf_k: int = 60
):
    # 1. Retrieve candidates using semantic search
    dense_result = retrieve_relevant_chunks(
        question=question,
        audience=audience,
        top_k=candidate_k
    )

    dense_chunks = dense_result["retrieved_chunks"]

    # 2. Retrieve candidates using keyword search
    keyword_chunks = retrieve_keyword_chunks(
        question=question,
        audience=audience,
        top_k=candidate_k
    )

    # 3. Combine results using Reciprocal Rank Fusion
    combined = {}

    for rank, chunk in enumerate(dense_chunks, start=1):
        chunk_id = chunk["chunk_id"]

        combined[chunk_id] = {
            **chunk,
            "dense_rank": rank,
            "rrf_score": 1 / (rrf_k + rank)
        }

    for rank, chunk in enumerate(keyword_chunks, start=1):
        chunk_id = chunk["chunk_id"]

        if chunk_id in combined:
            combined[chunk_id]["keyword_rank"] = rank
            combined[chunk_id]["bm25_score"] = chunk["bm25_score"]
            combined[chunk_id]["rrf_score"] += 1 / (rrf_k + rank)

        else:
            combined[chunk_id] = {
                **chunk,
                "keyword_rank": rank,
                "rrf_score": 1 / (rrf_k + rank)
            }

    # 4. Sort by combined RRF score
    ranked_chunks = sorted(
        combined.values(),
        key=lambda chunk: chunk["rrf_score"],
        reverse=True
    )

    return {
        "question": question,
        "audience": audience,
        "retrieved_chunks": ranked_chunks[:top_k],
        "status": "success"
    }
