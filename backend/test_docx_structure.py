
from backend.app.document_loader import extract_docx_blocks

file_path = (
    "knowledge_base/SOPs/"
    "SOP-005_Check_in_Issue_Resolution.docx"
)

blocks = extract_docx_blocks(file_path)

print("\n========== STRUCTURED DOCX EXTRACTION ==========")
print("Total blocks:", len(blocks))

for index, block in enumerate(blocks, start=1):
    print(f"\nBLOCK {index}")
    print("Style:", block["style"])
    print("Text:", block["text"])

print("\n================================================")
