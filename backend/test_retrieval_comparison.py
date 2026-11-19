
from backend.app.rag.retriever import retrieve_relevant_chunks
from backend.app.rag.keyword_retriever import retrieve_keyword_chunks
from backend.app.rag.hybrid_retriever import retrieve_hybrid_chunks

question = "early check-in availability and additional fee"
audience = "Guest"
top_k = 5

# 1. Dense retrieval
dense_results = retrieve_relevant_chunks(
    question, audience, top_k
)["retrieved_chunks"]

# 2. BM25 keyword retrieval
keyword_results = retrieve_keyword_chunks(
    question, audience, top_k
)

# 3. Hybrid retrieval
hybrid_results = retrieve_hybrid_chunks(
    question, audience, top_k
)["retrieved_chunks"]


def display_results(title, results):
    print(f"\n========== {title} ==========")

    for rank, chunk in enumerate(results, start=1):
        print(
            f"{rank}. {chunk['chunk_id']} | "
            f"{chunk['document_name']} | "
            f"{chunk['section']}"
        )


display_results("DENSE RETRIEVAL", dense_results)
display_results("BM25 KEYWORD RETRIEVAL", keyword_results)
display_results("HYBRID RETRIEVAL (RRF)", hybrid_results)
