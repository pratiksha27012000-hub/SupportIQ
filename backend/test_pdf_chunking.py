
from pathlib import Path

from backend.app.document_loader import extract_pdf_blocks
from backend.app.chunking import split_pdf_blocks_into_section_chunks

pdf_files = [
    Path("knowledge_base/Guest_Policies/POL-GST-001_Guest_Booking_Reservation_Policy.pdf"),
    Path("knowledge_base/Hotel_Partner_Policies/POL-HTL-005_Commission_Settlement_Policy.pdf")
]

for file_path in pdf_files:
    print("\n" + "=" * 65)
    print("DOCUMENT:", file_path.name)

    blocks = extract_pdf_blocks(str(file_path))

    chunks = split_pdf_blocks_into_section_chunks(blocks)

    print("CHUNKS CREATED:", len(chunks))

    for chunk in chunks:
        print("\nSECTION:", chunk["section"])
        print("PAGE:", chunk["page_number"])
        print("CONTENT:", chunk["text"][:250])
