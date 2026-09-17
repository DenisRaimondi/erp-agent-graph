from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from erp_agent_graph.models.order_line import OrderLine

OrderStatus = Literal["confermato", "evaso", "annullato"]


class Order(BaseModel):
    """Order header. Mirrors the `orders` table.

    READ-only model: `id`, `order_date`, `total_amount` and `created_at` are
    assigned by the database. To create an order the explicit values are passed to
    the repository, instead of building an `Order` with made-up fields.

    An order gets here only once it is valid: the customer is identified and the
    discrepancies have been resolved by a person. Whatever is still incomplete
    lives in the graph state, not in this table.
    """

    id: int
    # Mailpit id of the source email, and the checkpointer thread_id.
    source_email_id: str
    # The sender as they wrote it, even when the match went through the domain.
    sender_email: str
    # The reference the customer uses ("Ordine 2026/0447"), when they state one.
    customer_reference: str | None = None

    customer_id: int
    shipping_address_id: int

    order_date: date
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime

    # Lines do not come from the header query: class_row maps one row onto one
    # object, so the repository loads them separately and assigns them here.
    # Empty by default because the header alone is often all that is needed.
    lines: list[OrderLine] = []
