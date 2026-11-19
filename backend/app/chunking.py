
from typing import List, Dict


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 75
) -> List[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be non-negative and smaller than chunk_size"
        )

    words = text.split()
    chunks = []

    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

        start = end - chunk_overlap

    return chunks

def split_document_into_section_chunks(pages, section_headings):

    chunks = []
    current_section = None
    current_page = None
    current_lines = []

    def save_section():
        if current_section and current_lines:
            section_text = "\n".join(current_lines).strip()

            if section_text:
                chunks.append({
                    "section": current_section,
                    "page_number": current_page,
                    "text": section_text
                })

    for page in pages:
        for line in page["text"].splitlines():
            cleaned_line = line.strip()

            if cleaned_line in section_headings:
                save_section()
                current_section = cleaned_line
                current_page = page["page_number"]
                current_lines = []

            elif current_section and cleaned_line:
                current_lines.append(cleaned_line)

    save_section()

    return chunks


def split_docx_blocks_into_section_chunks(blocks):

    chunks = []
    current_section = None
    current_lines = []

    def save_section():
        if current_section and current_lines:
            section_text = "\n".join(current_lines).strip()

            if section_text:
                chunks.append({
                    "section": current_section,
                    "page_number": None,
                    "text": section_text
                })

    for block in blocks:
        text = block["text"].strip()
        style = block["style"]

        if style.startswith("Heading"):
            save_section()

            current_section = text
            current_lines = []

        elif current_section and text:
            if style == "List Bullet":
                current_lines.append(f"• {text}")
            else:
                current_lines.append(text)

    save_section()

    return chunks


def split_pdf_blocks_into_section_chunks(blocks):
    chunks = []
    current_section = None
    current_page = None
    current_lines = []

    # The first detected heading is the document title.
    heading_blocks = [
        block for block in blocks
        if block["style"] == "Heading 1"
    ]

    document_title = (
        heading_blocks[0]["text"]
        if heading_blocks else None
    )

    def save_section():
        if current_section and current_lines:
            section_text = "\n".join(current_lines).strip()

            if section_text:
                chunks.append({
                    "section": current_section,
                    "page_number": current_page,
                    "text": section_text
                })

    for block in blocks:
        text = block["text"].strip()
        style = block["style"]

        if not text:
            continue

        if style == "Heading 1":
            if text == document_title:
                continue

            save_section()
            current_section = text
            current_page = block["page_number"]
            current_lines = []

        elif current_section:
            current_lines.append(text)

    save_section()
    return chunks
