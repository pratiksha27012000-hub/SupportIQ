
from backend.app.services.ticket_service import create_ticket
from backend.app.core.database import get_db_connection


# 1. Create a ticket through our service
ticket = create_ticket(
    conversation_id="CONV-DB-001",
    guest_email="guest@example.com",
    issue="Duplicate payment inquiry",
    issue_description=(
        "Guest reports that the payment was deducted twice."
    ),
    conversation_transcript=[
        {
            "role": "user",
            "content": "I was charged twice."
        },
        {
            "role": "assistant",
            "content": "I can help you raise this for investigation."
        }
    ]
)

print("TICKET CREATED")
print("Ticket ID:", ticket.ticket_id)


# 2. Verify that the ticket exists in PostgreSQL
with get_db_connection() as connection:

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                ticket_id,
                conversation_id,
                guest_email,
                status
            FROM tickets
            WHERE conversation_id = %s
            """,
            ("CONV-DB-001",)
        )

        saved_ticket = cursor.fetchone()


# 3. Display database result
if saved_ticket:
    print("\nDATABASE PERSISTENCE VERIFIED")
    print("Saved record:", saved_ticket)

else:
    print("\nERROR: Ticket was not found in database.")
