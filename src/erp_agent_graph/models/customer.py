from datetime import datetime

from pydantic import BaseModel


class Customer(BaseModel):
    """Customer master data. Mirrors the `customers` table."""

    id: int
    code: str
    name: str
    vat_number: str
    payment_terms: str
    created_at: datetime
