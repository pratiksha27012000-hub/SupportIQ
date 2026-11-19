
from fastapi import APIRouter, HTTPException
from backend.app.core.database import get_db_connection
from backend.app.schemas.ticket import (
    TicketCreateRequest,
    TicketStatusUpdateRequest,
)
from backend.app.services.ticket_service import create_ticket


router = APIRouter(prefix="/tickets", tags=["Tickets"])


def row_to_dict(cursor, row):
    """Convert a database row into a dictionary."""
    if row is None:
        return None

    columns = [column.name for column in cursor.description]
    return dict(zip(columns, row))


@router.post("/create")
def create_ticket_endpoint(request: TicketCreateRequest):
    """Create a ticket after receiving guest consent."""

    try:
        ticket = create_ticket(
            conversation_id=request.conversation_id,
            guest_email=request.guest_email,
            issue=request.issue,
            issue_description=request.issue_description,
            conversation_transcript=request.conversation_transcript,
        )

        return {
            "message": "Ticket created successfully.",
            "ticket_id": ticket.ticket_id,
            "conversation_id": ticket.conversation_id,
            "status": ticket.status,
        }

    except ValueError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error),
        )


@router.get("/")
def get_all_tickets():
    """Return all tickets for the agent dashboard."""

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        ticket_id,
                        conversation_id,
                        guest_email,
                        issue,
                        created_at,
                        status
                    FROM tickets
                    ORDER BY created_at DESC
                    """
                )

                rows = cursor.fetchall()
                tickets = [
                    row_to_dict(cursor, row)
                    for row in rows
                ]

        return {
            "total": len(tickets),
            "tickets": tickets,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve tickets.",
        )


@router.get("/{ticket_id}")
def get_ticket_details(ticket_id: str):
    """Return complete ticket details and conversation transcript."""

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        ticket_id,
                        conversation_id,
                        guest_email,
                        issue,
                        issue_description,
                        conversation_transcript,
                        created_at,
                        status,
                        agent_response_reference
                    FROM tickets
                    WHERE ticket_id = %s
                    """,
                    (ticket_id,),
                )

                row = cursor.fetchone()
                ticket = row_to_dict(cursor, row)

        if ticket is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found.",
            )

        return ticket

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve ticket details.",
        )


@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: str,
    request: TicketStatusUpdateRequest,
):
    """Update the status of an existing ticket."""

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE tickets
                    SET status = %s
                    WHERE ticket_id = %s
                    RETURNING ticket_id, status
                    """,
                    (request.status, ticket_id),
                )

                row = cursor.fetchone()
                result = row_to_dict(cursor, row)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Ticket not found.",
            )

        return {
            "message": "Ticket status updated successfully.",
            "ticket_id": result["ticket_id"],
            "status": result["status"],
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to update ticket status.",
        )
