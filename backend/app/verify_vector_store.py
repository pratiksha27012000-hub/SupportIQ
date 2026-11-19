from collections import defaultdict
from backend.app.rag.vector_store import collection

records = collection.get(include=["metadatas"])

status_by_doc = defaultdict(set)
chunks_by_doc = defaultdict(int)

for metadata in records["metadatas"]:
    doc_id = metadata.get("document_id")
    status = metadata.get("status")

    status_by_doc[doc_id].add(status)
    chunks_by_doc[doc_id] += 1

print("\n========== DOCUMENT STATUS VERIFICATION ==========\n")

for doc_id in sorted(status_by_doc):
    print(
        f"{doc_id} | "
        f"Chunks: {chunks_by_doc[doc_id]} | "
        f"Status: {status_by_doc[doc_id]}"
    )

not_approved = [
    doc_id
    for doc_id, statuses in status_by_doc.items()
    if statuses != {"Approved"}
]

print("\n========== FINAL SUMMARY ==========")
print("Unique documents:", len(status_by_doc))
print("Total chunks:", collection.count())
print("Documents not fully approved:", not_approved)
print("All documents approved:", len(not_approved) == 0)