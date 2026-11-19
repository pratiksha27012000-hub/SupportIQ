
CREATE TABLE IF NOT EXISTS tickets (

    ticket_id VARCHAR(50) PRIMARY KEY,

    conversation_id VARCHAR(100) NOT NULL UNIQUE,

    guest_email VARCHAR(255) NOT NULL,

    issue TEXT NOT NULL,

    issue_description TEXT NOT NULL,

    conversation_transcript JSONB NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,

    status VARCHAR(20) NOT NULL DEFAULT 'Open',

    agent_response_reference TEXT,

    CONSTRAINT valid_ticket_status
        CHECK (
            status IN (
                'Open',
                'In Progress',
                'Resolved'
            )
        )
);