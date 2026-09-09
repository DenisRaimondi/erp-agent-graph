from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

OrderStatus = Literal["confermato", "evaso", "annullato"]


class Order(BaseModel):
    """Testata dell'ordine. Rispecchia la tabella `orders`.

    Modello di sola LETTURA: `id`, `order_date`, `total_amount` e `created_at`
    li assegna il database. Per creare un ordine si passano i valori espliciti al
    repository, invece di costruire un `Order` con dei campi finti.

    Un ordine arriva qui solo quando e' valido: il cliente e' identificato e le
    discrepanze sono state risolte dall'umano. Quello che e' ancora incompleto
    vive nello stato del grafo, non in questa tabella.
    """

    id: int
    # ID Mailpit della mail di origine, e thread_id del checkpointer.
    source_email_id: str
    # Il mittente come l'ha scritto lui, anche se l'aggancio e' passato dal dominio.
    sender_email: str
    # Il riferimento usato dal cliente ("Ordine 2026/0447"), se l'ha indicato.
    customer_reference: str | None = None

    customer_id: int
    shipping_address_id: int

    order_date: date
    status: OrderStatus
    total_amount: Decimal
    created_at: datetime
