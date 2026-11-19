
from openpyxl import load_workbook
from pathlib import Path


def load_document_metadata(workbook_path: str):
    workbook_path = Path(workbook_path)

    if not workbook_path.exists():
        raise FileNotFoundError(
            f"Metadata workbook not found: {workbook_path}"
        )

    workbook = load_workbook(
        workbook_path,
        read_only=True,
        data_only=True
    )

    try:
        sheet = workbook["Document_Master"]

        headers = next(
            sheet.iter_rows(
                min_row=1,
                max_row=1,
                values_only=True
            )
        )

        metadata_registry = {}

        for row in sheet.iter_rows(
            min_row=2,
            values_only=True
        ):
            record = dict(zip(headers, row))

            document_id = record.get("document_id")

            if not document_id:
                continue

            document_id = str(document_id).strip()

            if document_id in metadata_registry:
                raise ValueError(
                    f"Duplicate document ID found: {document_id}"
                )

            metadata_registry[document_id] = record

        return metadata_registry

    finally:
        workbook.close()
