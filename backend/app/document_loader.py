import pymupdf  # PyMuPDF
import os
from backend.app.metadata_loader import load_document_metadata
from docx import Document
from pathlib import Path


def extract_text_from_pdf(file_path: str):
    """
    Extracts text from every page of a PDF document.
    """

    extracted_pages = []

    # Open the PDF document
    document = pymupdf.open(file_path)

    # Read each page
    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        extracted_pages.append({
            "page_number": page_number,
            "text": text.strip()
        })

    document.close()

    return extracted_pages





def extract_text_from_docx(file_path: str):
    """
    Extracts text from a Word document.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def extract_docx_blocks(file_path: str):
    document = Document(file_path)

    blocks = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()

        if not text:
            continue

        blocks.append({
            "text": text,
            "style": paragraph.style.name
        })

    return blocks


def extract_text_from_txt(file_path: str):
    """
    Extracts text from a TXT document.
    """

    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text.strip()





def load_document(file_path: str):
    """
    Identifies the document format and extracts its text.
    """

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == ".pdf":
        content = extract_text_from_pdf(file_path)

    elif file_extension == ".docx":
        content = extract_text_from_docx(file_path)

    elif file_extension == ".txt":
        content = extract_text_from_txt(file_path)

    else:
        raise ValueError(
            f"Unsupported document format: {file_extension}"
        )

    return {
        "file_name": os.path.basename(file_path),
        "file_path": file_path,
        "file_type": file_extension,
        "content": content
    }



def load_all_documents(folder_path: str):
    supported_extensions = {".pdf", ".docx", ".txt"}
    all_documents = []

    folder = Path(folder_path)

    for file_path in folder.rglob("*"):

        # Skip files inside the Metadata folder
        relative_parts = [
            part.lower()
            for part in file_path.relative_to(folder).parts
        ]

        if "metadata" in relative_parts:
            continue

        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            try:
                document = load_document(str(file_path))
                all_documents.append(document)
                print(f"Loaded: {file_path.name}")

            except Exception as error:
                print(f"Failed: {file_path.name} | {error}")

    return all_documents


def load_documents_with_metadata(
    folder_path: str,
    workbook_path: str
):
    # Load document content
    documents = load_all_documents(folder_path)

    # Load Excel metadata
    metadata_registry = load_document_metadata(workbook_path)

    enriched_documents = []

    for document in documents:
        # Extract document ID from filename
        document_id = Path(document["file_name"]).stem.split("_")[0]

        # Find matching metadata
        metadata = metadata_registry.get(document_id)

        if metadata is None:
            print(f"WARNING: Metadata missing for {document['file_name']}")
            continue

        # Combine extracted content and metadata
        enriched_document = {
            **document,
            "document_id": document_id,
            "metadata": metadata
        }

        enriched_documents.append(enriched_document)

    print("\n========== METADATA ENRICHMENT ==========")
    print("Documents extracted:", len(documents))
    print("Documents enriched:", len(enriched_documents))
    print("Documents without metadata:", len(documents) - len(enriched_documents))
    print("=========================================")

    return enriched_documents


def extract_txt_blocks(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    blocks = []
    index = 0

    while index < len(lines):
        current_line = lines[index].strip()

        if not current_line:
            index += 1
            continue

        # Detect a heading followed by a dashed separator
        if (
            index + 1 < len(lines)
            and lines[index + 1].strip()
            and set(lines[index + 1].strip()) == {"-"}
        ):
            blocks.append({
                "text": current_line,
                "style": "Heading 1"
            })
            index += 2
            continue

        # Exclude introductory metadata and demo notices
        if (
            current_line.startswith("DEMO NOTICE:")
            or current_line.startswith("Audience:")
            or current_line.startswith("Status:")
        ):
            index += 1
            continue

        blocks.append({
            "text": current_line,
            "style": "Normal"
        })

        index += 1

    return blocks


def extract_pdf_blocks(file_path: str):
    document = pymupdf.open(file_path)

    blocks = []

    metadata_labels = {
        "Document ID",
        "Version",
        "Type",
        "Status",
        "Audience",
        "Owner",
        "Category",
        "Format"
    }

    for page_number, page in enumerate(document, start=1):
        page_data = page.get_text("dict")

        for block in page_data["blocks"]:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                spans = line["spans"]

                if not spans:
                    continue

                text = " ".join(
                    span["text"].strip()
                    for span in spans
                    if span["text"].strip()
                ).strip()

                if not text:
                    continue

                is_bold = any(
                    "bold" in span["font"].lower()
                    for span in spans
                )

                large_font = any(
                    span["size"] >= 12
                    for span in spans
                )

                is_heading = (
                    (is_bold or large_font)
                    and len(text) < 120
                    and text not in metadata_labels
                )

                blocks.append({
                    "text": text,
                    "style": "Heading 1" if is_heading else "Normal",
                    "page_number": page_number
                })

    document.close()
    return blocks
