from typing import Literal

from pydantic import BaseModel, Field


class Verdict(BaseModel):
    """Represents the classification verdict of an email, including the email ID, topic, and confidence score."""

    topic: list[Literal["new_order_request", "quote_request", "ticket", "spam", "general_info"]] = (
        Field(description="The topic of the email")
    )
    confidence: float = Field(
        description="Confidence score of the classification, between 0 and 1", ge=0.0, le=1.0
    )
    reason: str = Field(description="Reason for the classification verdict")
