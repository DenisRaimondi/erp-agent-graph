from datetime import datetime
from typing import Literal

from pydantic import BaseModel

type MailStatus = Literal[
    "pending",
    "processing",
    "interrupted",
    "discarded",
    "awaiting_review",
    "completed",
    "failed",
]


class InboundMail(BaseModel):
    """An email the dispatcher has picked up. Mirrors the `inbound_mails` table.

    It records that the email was seen and how far it got, not what the graph
    decided: `thread_id` is the LangGraph run, and the reasoning behind every
    step is read back from the checkpoints with get_state_history().
    """

    id: int | None = None
    thread_id: str

    status: MailStatus = "pending"

    sender: str
    subject: str
    body: str
    received_at: datetime

    created_at: datetime | None = None
    updated_at: datetime | None = None
