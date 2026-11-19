
from backend.app.services.ticket_service import create_ticket


def test_create_ticket(conversation_id):

    return create_ticket(
        conversation_id=conversation_id,
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


# First attempt
ticket = test_create_ticket("CONV-001")

print("FIRST ATTEMPT: SUCCESS")
print("Ticket ID:", ticket.ticket_id)


# Second attempt using the same conversation
try:
    test_create_ticket("CONV-001")

    print("ERROR: Duplicate ticket was created!")

except ValueError as error:
    print("SECOND ATTEMPT: SUCCESSFULLY BLOCKED")
    print("Reason:", error)


# Third attempt using a different conversation
new_ticket = test_create_ticket("CONV-002")

print("THIRD ATTEMPT: SUCCESS")
print("New Ticket ID:", new_ticket.ticket_id)
