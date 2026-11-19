
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Ticket(BaseModel):

    ticket_id: str = Field(min_length=1)
    conversation_id: str = Field(min_length=1)

    guest_email: str = Field(min_length=1)

    issue: str = Field(min_length=1)
    issue_description: str = Field(min_length=1)

    conversation_transcript: list[dict]

    created_at: datetime

    status: Literal[
        "Open",
        "In Progress",
        "Resolved"
    ] = "Open"

    agent_response_reference: str | None = None

    model_config = {
        "extra": "forbid"
    }


from typing import Literal


class TicketCreateRequest(BaseModel):

    conversation_id: str = Field(min_length=1)
    guest_email: str = Field(min_length=1)
    issue: str = Field(min_length=1)
    issue_description: str = Field(min_length=1)

    conversation_transcript: list[dict]

    consent: Literal[True]



class TicketCreateRequest(BaseModel):

    conversation_id: str = Field(min_length=1)
    guest_email: str = Field(min_length=1)
    issue: str = Field(min_length=1)
    issue_description: str = Field(min_length=1)

    conversation_transcript: list[dict]

    consent: Literal[True]


class TicketStatusUpdateRequest(BaseModel):

    status: Literal[
        "Open",
        "In Progress",
        "Resolved"
    ]
