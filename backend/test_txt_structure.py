
from backend.app.document_loader import extract_txt_blocks
from backend.app.chunking import split_docx_blocks_into_section_chunks

file_path = (
    "knowledge_base/Knowledge_Articles/"
    "KB-001_Guest_Support_FAQs.txt"
)

# 1. Extract structured TXT blocks
blocks = extract_txt_blocks(file_path)

# 2. Reuse our section-aware chunker
chunks = split_docx_blocks_into_section_chunks(blocks)

# 3. Display results
print("\n========== TXT CHUNKING TEST ==========")
print("Total blocks:", len(blocks))
print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- CHUNK {index} ---")
    print("Question:", chunk["section"])
    print("Answer:", chunk["text"])

print("\n======================================")
