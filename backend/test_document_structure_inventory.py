
from pathlib import Path
import pymupdf

from backend.app.document_loader import (
    extract_docx_blocks,
    extract_txt_blocks
)

KNOWLEDGE_BASE = Path("knowledge_base")

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def inspect_pdf(file_path):
    document = pymupdf.open(file_path)

    heading_candidates = []

    for page_number, page in enumerate(document, start=1):
        page_data = page.get_text("dict")

        for block in page_data["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                spans = line["spans"]

                if not spans:
                    continue

                line_text = " ".join(
                    span["text"].strip()
                    for span in spans
                    if span["text"].strip()
                )

                if not line_text:
                    continue

                is_bold = any(
                    "bold" in span["font"].lower()
                    for span in spans
                )

                large_font = any(
                    span["size"] >= 12
                    for span in spans
                )

                if (is_bold or large_font) and len(line_text) < 120:
                    heading_candidates.append(
                        f"Page {page_number}: {line_text}"
                    )

    page_count = len(document)
    document.close()

    return page_count, heading_candidates


def inspect_documents():
    files = [
        path
        for path in KNOWLEDGE_BASE.rglob("*")
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
        and "metadata" not in [
            part.lower()
            for part in path.relative_to(KNOWLEDGE_BASE).parts
        ]
    ]

    print(f"Total documents found: {len(files)}")

    for file_path in sorted(files):
        extension = file_path.suffix.lower()

        print("\n" + "=" * 65)
        print("FILE:", file_path.name)
        print("FORMAT:", extension.upper())

        if extension == ".pdf":
            pages, headings = inspect_pdf(file_path)
            print("PAGES:", pages)
            print("HEADING CANDIDATES:")

            if headings:
                for heading in headings:
                    print(" -", heading)
            else:
                print(" - No heading candidates detected")

        elif extension == ".docx":
            blocks = extract_docx_blocks(str(file_path))

            headings = [
                block["text"]
                for block in blocks
                if block["style"].startswith("Heading")
                or block["style"] == "Title"
            ]

            print("TOTAL BLOCKS:", len(blocks))
            print("HEADINGS:")

            for heading in headings:
                print(" -", heading)

        elif extension == ".txt":
            blocks = extract_txt_blocks(str(file_path))

            headings = [
                block["text"]
                for block in blocks
                if block["style"].startswith("Heading")
            ]

            print("TOTAL BLOCKS:", len(blocks))
            print("HEADINGS:")

            for heading in headings:
                print(" -", heading)


if __name__ == "__main__":
    inspect_documents()
