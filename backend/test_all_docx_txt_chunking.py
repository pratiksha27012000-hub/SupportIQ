
from pathlib import Path

from backend.app.document_loader import (
    extract_docx_blocks,
    extract_txt_blocks
)

from backend.app.chunking import (
    split_docx_blocks_into_section_chunks
)

knowledge_base = Path("knowledge_base")

files = sorted([
    path
    for path in knowledge_base.rglob("*")
    if path.is_file()
    and path.suffix.lower() in {".docx", ".txt"}
    and "metadata" not in [
        part.lower()
        for part in path.relative_to(knowledge_base).parts
    ]
])

total_chunks = 0
failed_documents = []

print("DOCX AND TXT DOCUMENTS FOUND:", len(files))

for file_path in files:

    if file_path.suffix.lower() == ".docx":
        blocks = extract_docx_blocks(str(file_path))
    else:
        blocks = extract_txt_blocks(str(file_path))

    chunks = split_docx_blocks_into_section_chunks(blocks)

    total_chunks += len(chunks)

    if not chunks:
        failed_documents.append(file_path.name)

    print(f"{file_path.name} | Chunks: {len(chunks)}")

print("\n========== CHUNKING SUMMARY ==========")
print("Documents processed:", len(files))
print("Total chunks created:", total_chunks)
print("Documents without chunks:", len(failed_documents))

if failed_documents:
    print("\nDocuments requiring review:")
    for name in failed_documents:
        print("-", name)
else:
    print("All documents produced at least one chunk.")

print("======================================")
