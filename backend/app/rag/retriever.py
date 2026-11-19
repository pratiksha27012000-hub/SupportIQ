
from backend.app.core.config import ALLOWED_DOCUMENT_STATUSES
from backend.app.rag.vector_store import (
    collection,
    embedding_model
)


def retrieve_relevant_chunks(
    question: str,
    audience: str = "Guest",
    top_k: int = 5
):
    # 1. Convert the guest's question into an embedding
    query_embedding = embedding_model.encode(
        question
    ).tolist()

    # 2. Search ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={
            "$and": [
                {"audience": audience},
                {"status": {"$in": ALLOWED_DOCUMENT_STATUSES}}
            ]
        },
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    # 3. Structure the retrieved results
    retrieved_chunks = []

    for index in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][index]
        distance = results["distances"][0][index]

        retrieved_chunks.append({
            "chunk_id": results["ids"][0][index],
            "document_id": metadata.get("document_id"),
            "document_name": metadata.get("document_name"),
            "section": metadata.get("section"),
            "category": metadata.get("category"),
            "content": results["documents"][0][index],
            "distance": distance,
            "similarity": 1 - distance,
            "status": metadata.get("status"),
            "page_number": metadata.get("page_number"),
            "audience": metadata.get("audience")
        })

    return {
        "question": question,
        "audience": audience,
        "retrieved_chunks": retrieved_chunks,
        "status": "success"
    }
