
from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks
from backend.app.rag.reranker import rerank_chunks

questions = [
    "Can I get an early check-in?",
    "Can you arrange airport pickup for me?",
    "What is the refund timeline?",
    "Can I cancel my reservation?",
    "Do you provide airport transfers?",
    "Can I get a complimentary room upgrade?"
]

for question in questions:

    print("\n" + "=" * 65)
    print("QUESTION:", question)
    print("=" * 65)

    # Step 1: Retrieve candidate chunks
    hybrid_result = retrieve_hybrid_chunks(
        question=question,
        audience="Guest",
        top_k=10,
        candidate_k=10
    )

    retrieved_chunks = hybrid_result["retrieved_chunks"]

    # Step 2: Rerank candidates
    reranked_chunks = rerank_chunks(
        question=question,
        retrieved_chunks=retrieved_chunks,
        top_k=5
    )

    # Step 3: Display results
    for rank, chunk in enumerate(reranked_chunks, start=1):
        print(f"\nRank: {rank}")
        print("Chunk ID:", chunk["chunk_id"])
        print("Document:", chunk["document_name"])
        print("Section:", chunk["section"])
        print("Reranker Score:", round(chunk["reranker_score"], 4))

    print("\nTotal reranked chunks:", len(reranked_chunks))
