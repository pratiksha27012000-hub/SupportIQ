from backend.app.document_loader import load_document

file_path = (
    "knowledge_base/Guest_Policies/"
    "POL-GST-006_Early_Check_in_Late_Check_out_Policy.pdf"
)

result = load_document(file_path)

print("FILE NAME:", result["file_name"])
print("FILE TYPE:", result["file_type"])

print("\nEXTRACTED CONTENT:\n")

for page in result["content"]:
    print(f"\n--- PAGE {page['page_number']} ---")
    print(page["text"])
