
from pathlib import Path

from backend.app.document_loader import extract_pdf_blocks
from backend.app.chunking import split_pdf_blocks_into_section_chunks

pdf_folder = Path("knowledge_base")

pdf_files = sorted(pdf_folder.rglob("*.pdf"))

total_chunks = 0
failed_documents = []

print("PDF DOCUMENTS FOUND:", len(pdf_files))

for file_path in pdf_files:
    blocks = extract_pdf_blocks(str(file_path))
    chunks = split_pdf_blocks_into_section_chunks(blocks)

    total_chunks += len(chunks)

    if not chunks:
        failed_documents.append(file_path.name)

    print(
        f"{file_path.name} | "
        f"Chunks: {len(chunks)}"
    )

print("\n========== PDF CHUNKING SUMMARY ==========")
print("Documents processed:", len(pdf_files))
print("Total chunks created:", total_chunks)
print("Documents without chunks:", len(failed_documents))

if failed_documents:
    print("\nDocuments requiring review:")
    for name in failed_documents:
        print("-", name)
else:
    print("All PDFs produced at least one chunk.")

print("==========================================")
