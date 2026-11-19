
from backend.app.document_loader import load_document
from backend.app.chunking import split_document_into_section_chunks

file_path = (
    "knowledge_base/Guest_Policies/"
    "POL-GST-006_Early_Check_in_Late_Check_out_Policy.pdf"
)

document = load_document(file_path)

section_headings = [
    "Purpose and scope",
    "Policy rules",
    "Request workflow",
    "Exceptions",
    "Related documents"
]

chunks = split_document_into_section_chunks(
    pages=document["content"],
    section_headings=section_headings
)

print("\n========== SECTION CHUNKING TEST ==========")
print("Total chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- CHUNK {index} ---")
    print("Section:", chunk["section"])
    print("Page:", chunk["page_number"])
    print("Text:", chunk["text"])

print("\n===========================================")
