
from datetime import datetime, timezone
from uuid import uuid4

from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

from backend.app.core.database import get_db_connection
from backend.app.schemas.ticket import Ticket


def create_ticket(
    conversation_id: str,
    guest_email: str,
    issue: str,
    issue_description: str,
    conversation_transcript: list[dict]
):

    # 1. Create and validate the ticket
    ticket = Ticket(
        ticket_id=f"TKT-{uuid4().hex[:8].upper()}",
        conversation_id=conversation_id,
        guest_email=guest_email,
        issue=issue,
        issue_description=issue_description,
        conversation_transcript=conversation_transcript,
        created_at=datetime.now(timezone.utc),
        status="Open"
    )

    # 2. Save ticket permanently in PostgreSQL
    try:
        with get_db_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO tickets (
                        ticket_id,
                        conversation_id,
                        guest_email,
                        issue,
                        issue_description,
                        conversation_transcript,
                        created_at,
                        status,
                        agent_response_reference
                    )
                    VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                    """,
                    (
                        ticket.ticket_id,
                        ticket.conversation_id,
                        ticket.guest_email,
                        ticket.issue,
                        ticket.issue_description,
                        Jsonb(ticket.conversation_transcript),
                        ticket.created_at,
                        ticket.status,
                        ticket.agent_response_reference
                    )
                )

        return ticket

    except UniqueViolation:
        raise ValueError(
            "A ticket already exists for conversation: "
            f"{conversation_id}"
        )
