"""CustomerChoice model."""

from pydantic import BaseModel, Field


class CustomerChoice(BaseModel):
    """Customer choosen"""

    id: int | None
    reason: str = Field(
        description="Provide a reason why you choose this particular customer, "
        "or why you could not choose one"
    )
