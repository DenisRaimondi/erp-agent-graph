from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class OrderLine(BaseModel):
    """Riga d'ordine. Rispecchia la tabella `order_lines`.

    `description`, `unit_of_measure` e `unit_price` sono COPIATI dall'articolo al
    momento dell'ordine, non letti dal catalogo con una join: se cambia il listino,
    gli ordini gia' fatti devono restare come erano. Un ordine e' un documento
    storico, non una vista sui dati correnti.
    """

    id: int
    order_id: int
    line_no: int

    article_code: str
    description: str
    unit_of_measure: str
    unit_price: Decimal

    quantity: int
    # Colonna generata da Postgres (quantity * unit_price): in sola lettura.
    line_total: Decimal

    requested_date: date | None = None
