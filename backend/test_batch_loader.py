
from backend.app.document_loader import load_all_documents

# Load all supported documents from the knowledge base
documents = load_all_documents("knowledge_base")

# Display summary
print("\n========== INGESTION SUMMARY ==========")

print("Total documents loaded:", len(documents))

# Count documents by format
pdf_count = sum(1 for doc in documents if doc["file_type"] == ".pdf")
docx_count = sum(1 for doc in documents if doc["file_type"] == ".docx")
txt_count = sum(1 for doc in documents if doc["file_type"] == ".txt")

print("PDF files:", pdf_count)
print("DOCX files:", docx_count)
print("TXT files:", txt_count)

print("=======================================")

from pathlib import Path

print("\n========== TXT FILE AUDIT ==========")

for file_path in Path("knowledge_base").rglob("*.txt"):
    print(file_path)

print("====================================")