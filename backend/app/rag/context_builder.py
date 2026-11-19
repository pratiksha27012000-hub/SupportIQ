
def build_context(
    question: str,
    reranked_chunks: list,
    audience: str = "Guest",
    max_chunks: int = 5
):
    selected_chunks = []
    seen_chunk_ids = set()

    # 1. Select relevant chunks and remove duplicates
    for chunk in reranked_chunks:
        chunk_id = chunk["chunk_id"]

        if chunk_id in seen_chunk_ids:
            continue

        # 2. Enforce audience-level filtering
        if chunk.get("audience") != audience:
            continue

        seen_chunk_ids.add(chunk_id)
        selected_chunks.append(chunk)

        if len(selected_chunks) >= max_chunks:
            break

    # 3. Build structured context with source information
    context_parts = []
    citations = []

    for index, chunk in enumerate(selected_chunks, start=1):
        source = (
            f"[Source {index}]\n"
            f"Document ID: {chunk.get('document_id')}\n"
            f"Document: {chunk.get('document_name')}\n"
            f"Section: {chunk.get('section')}\n"
            f"Page: {chunk.get('page_number')}\n"
            f"Audience: {chunk.get('audience')}\n"
            f"Document Status: {chunk.get('status')}\n"
            f"Content:\n{chunk.get('content')}"
        )

        context_parts.append(source)

        citations.append({
            "chunk_id": chunk.get("chunk_id"),
            "document_id": chunk.get("document_id"),
            "document_name": chunk.get("document_name"),
            "section": chunk.get("section"),
            "page_number": chunk.get("page_number"),
            "status": chunk.get("status")
        })

    # 4. Combine selected sources
    context = "\n\n".join(context_parts)

    return {
        "question": question,
        "audience": audience,
        "context": context,
        "selected_chunks": selected_chunks,
        "citations": citations,
        "chunk_count": len(selected_chunks),
        "status": "success" if selected_chunks else "no_context"
    }
