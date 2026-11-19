
from backend.app.document_loader import extract_docx_blocks
from backend.app.chunking import split_docx_blocks_into_section_chunks

file_path = (
    "knowledge_base/SOPs/"
    "SOP-005_Check_in_Issue_Resolution.docx"
)

# 1. Extract structured Word blocks
blocks = extract_docx_blocks(file_path)

# 2. Create section-aware chunks
chunks = split_docx_blocks_into_section_chunks(blocks)

# 3. Display results
print("\n========== DOCX CHUNKING TEST ==========")
print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- CHUNK {index} ---")
    print("Section:", chunk["section"])
    print("Page:", chunk["page_number"])
    print("Text:\n", chunk["text"])

print("\n========================================")
