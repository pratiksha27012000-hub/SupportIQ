
from backend.app.core.database import get_db_connection


with get_db_connection() as connection:

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                ticket_id,
                conversation_id,
                guest_email,
                issue,
                status
            FROM tickets
            WHERE conversation_id = %s
            """,
            ("CONV-DB-001",)
        )

        ticket = cursor.fetchone()


if ticket:
    print("PERSISTENCE TEST PASSED")
    print("Ticket record:", ticket)

else:
    print("PERSISTENCE TEST FAILED")
