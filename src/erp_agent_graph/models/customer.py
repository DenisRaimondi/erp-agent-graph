from datetime import datetime

from pydantic import BaseModel


class Customer(BaseModel):
    """Anagrafica cliente. Rispecchia la tabella `customers`."""

    id: int
    code: str
    name: str
    vat_number: str
    payment_terms: str
    created_at: datetime
