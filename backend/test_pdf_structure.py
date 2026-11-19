
from backend.app.document_loader import load_document

file_path = (
    "knowledge_base/Guest_Policies/"
    "POL-GST-006_Early_Check_in_Late_Check_out_Policy.pdf"
)

document = load_document(file_path)

pages = document["content"]

print("\n========== PDF STRUCTURE ==========")
print("Document:", document["file_name"])
print("Total pages:", len(pages))

for page in pages:
    print(f"\n{'=' * 45}")
    print("PAGE:", page["page_number"])
    print("CHARACTERS:", len(page["text"]))
    print("\nEXTRACTED TEXT:")
    print(page["text"])

print("\n===================================")
