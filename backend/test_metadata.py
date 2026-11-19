
from openpyxl import load_workbook
from pathlib import Path

workbook_path = Path(
    "knowledge_base/Metadata/StayEase_Knowledge_Base_Registry_v0.1.xlsx"
)

knowledge_base_path = Path("knowledge_base")

workbook = load_workbook(
    workbook_path,
    read_only=True,
    data_only=True
)

sheet = workbook["Document_Master"]

headers = next(
    sheet.iter_rows(min_row=1, max_row=1, values_only=True)
)

# Read registry records
registry = {}

for row in sheet.iter_rows(min_row=2, values_only=True):
    record = dict(zip(headers, row))
    document_id = record.get("document_id")

    if document_id:
        registry[str(document_id).strip()] = record

# Find actual knowledge-base files
supported_extensions = {".pdf", ".docx", ".txt"}

files = [
    path for path in knowledge_base_path.rglob("*")
    if path.is_file()
    and path.suffix.lower() in supported_extensions
    and "metadata" not in [
        part.lower()
        for part in path.relative_to(knowledge_base_path).parts
    ]
]

print("\n========== METADATA MATCHING AUDIT ==========")

matched = []
unmatched = []

for file_path in files:
    document_id = file_path.stem.split("_")[0]

    if document_id in registry:
        matched.append(document_id)
        print(f"MATCHED: {file_path.name} -> {document_id}")
    else:
        unmatched.append(file_path.name)
        print(f"UNMATCHED: {file_path.name}")

print("\n========== AUDIT SUMMARY ==========")
print("Physical files:", len(files))
print("Registry records:", len(registry))
print("Matched files:", len(matched))
print("Unmatched files:", len(unmatched))
print("===================================")

workbook.close()
