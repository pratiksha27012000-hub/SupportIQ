from backend.app.rag.vector_store import ingest_chunks_into_vector_store


if __name__ == "__main__":
    result = ingest_chunks_into_vector_store()

    print("\n========== VECTOR INGESTION SUMMARY ==========")
    print(result)
    print("Vector ingestion completed successfully!")