from backend.app.rag.vector_store import client, collection

print("ChromaDB connection successful!")
print("Collection name:", collection.name)
print("Existing records:", collection.count())