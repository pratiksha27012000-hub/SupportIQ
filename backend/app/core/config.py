# SupportIQ Environment Configuration

# Development mode allows Draft documents for testing.
# Set to False before production deployment.
ALLOW_DRAFT_DOCUMENTS = True

APPROVED_STATUS = "Approved"
DRAFT_STATUS = "Draft"

# Documents eligible for retrieval
ALLOWED_DOCUMENT_STATUSES = (
    [APPROVED_STATUS, DRAFT_STATUS]
    if ALLOW_DRAFT_DOCUMENTS
    else [APPROVED_STATUS]
)