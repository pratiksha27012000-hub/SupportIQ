
from backend.app.services.ticket_service import create_ticket


try:
    create_ticket(
        conversation_id="CONV-DB-001",
        guest_email="guest@example.com",
        issue="Duplicate payment inquiry",
        issue_description="Testing duplicate ticket prevention.",
        conversation_transcript=[
            {
                "role": "user",
                "content": "I was charged twice."
            }
        ]
    )

    print("ERROR: Duplicate ticket was created!")

except ValueError as error:
    print("DUPLICATE PREVENTION SUCCESSFUL")
    print("Reason:", error)
