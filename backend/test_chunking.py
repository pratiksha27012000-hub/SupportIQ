
from typing import List


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 75
) -> List[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Invalid chunk_overlap")

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
