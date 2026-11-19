
import json
import re
from pathlib import Path
from backend.app.core.config import ALLOWED_DOCUMENT_STATUSES
from rank_bm25 import BM25Okapi


# 1. Locate the enriched chunks
PROJECT_ROOT = Path(__file__).resolve().parents[3]

CHUNKS_FILE = (
    PROJECT_ROOT
    / "knowledge_base"
    / "processed"
    / "enriched_chunks.jsonl"
)


# 2. Load all chunks
all_chunks = []

with open(CHUNKS_FILE, "r", encoding="utf-8") as file:
    for line in file:
        all_chunks.append(json.loads(line))


# 3. Tokenization function
def tokenize(text: str):
    return re.findall(r"\b\w+\b", text.lower())


# 4. Build the keyword retriever
def retrieve_keyword_chunks(
    question: str,
    audience: str = "Guest",
    top_k: int = 5
):
    # Filter documents by audience
    filtered_chunks = [
        chunk for chunk in all_chunks
        if (
            chunk.get("audience") == audience
            and chunk.get("status") in ALLOWED_DOCUMENT_STATUSES
        )
    ]

    if not filtered_chunks:
        return []

    # Tokenize document content
    tokenized_corpus = [
        tokenize(chunk["text"])
        for chunk in filtered_chunks
    ]

    # Build BM25 index
    bm25 = BM25Okapi(tokenized_corpus)

    # Tokenize guest question
    tokenized_query = tokenize(question)

    # Calculate keyword relevance scores
    scores = bm25.get_scores(tokenized_query)

    # Rank results by score
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    # Return top results
    results = []

    for index in ranked_indices[:top_k]:
        if scores[index] <= 0:
            continue

        chunk = filtered_chunks[index]

        results.append({
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk["document_id"],
            "document_name": chunk["document_name"],
            "section": chunk["section"],
            "audience": chunk.get("audience"),
            "status": chunk.get("status"),
            "page_number": chunk.get("page_number"),
            "content": chunk["text"],
            "bm25_score": float(scores[index])
        })

    return results
