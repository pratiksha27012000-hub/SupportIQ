
from datetime import datetime, timezone

from backend.app.schemas.ticket import Ticket


sample_ticket = {
    "ticket_id": "TKT-1001",
    "conversation_id": "CONV-001",
    "guest_email": "guest@example.com",
    "issue": "Duplicate payment inquiry",
    "issue_description": (
        "Guest reports that the payment was deducted twice "
        "and wants to know the status."
    ),
    "conversation_transcript": [
        {
            "role": "user",
            "content": "I was charged twice."
        },
        {
            "role": "assistant",
            "content": "I can help you raise this for investigation."
        }
    ],
    "created_at": datetime.now(timezone.utc),
    "status": "Open",
    "agent_response_reference": None
}


ticket = Ticket(**sample_ticket)

print("TICKET VALIDATION SUCCESSFUL")
print(ticket.model_dump())



from pydantic import ValidationError

invalid_ticket = sample_ticket.copy()
invalid_ticket["status"] = "Pending"

try:
    Ticket(**invalid_ticket)
    print("ERROR: Invalid status was accepted!")

except ValidationError:
    print("SUCCESS: Invalid status was rejected.")
