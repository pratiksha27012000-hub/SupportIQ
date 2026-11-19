
from sentence_transformers import CrossEncoder

# Load the reranking model
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_chunks(
    question: str,
    retrieved_chunks: list,
    top_k: int = 5
):
    if not retrieved_chunks:
        return []

    # Create query-chunk pairs
    pairs = [
        (question, chunk["content"])
        for chunk in retrieved_chunks
    ]

    # Score each query-chunk pair
    scores = reranker_model.predict(pairs)

    # Attach scores to chunks
    reranked_chunks = []

    for chunk, score in zip(retrieved_chunks, scores):
        reranked_chunks.append({
            **chunk,
            "reranker_score": float(score)
        })

    # Sort by reranker score
    reranked_chunks.sort(
        key=lambda chunk: chunk["reranker_score"],
        reverse=True
    )

    return reranked_chunks[:top_k]
