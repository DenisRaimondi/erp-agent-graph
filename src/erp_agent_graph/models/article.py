from decimal import Decimal

from pydantic import BaseModel


class Article(BaseModel):
    """Catalogue article. Mirrors the `articles` table.

    `unit_price` is a `Decimal` and not a `float`: psycopg returns `Decimal` for
    `numeric` columns, and on a price the binary arithmetic of floats introduces
    errors that show up on an invoice, not in the tests.
    """

    code: str
    description: str
    unit_of_measure: str
    unit_price: Decimal
    stock_qty: int
