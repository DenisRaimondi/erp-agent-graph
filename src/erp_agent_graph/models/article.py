from decimal import Decimal

from pydantic import BaseModel


class Article(BaseModel):
    """Articolo a catalogo. Rispecchia la tabella `articles`.

    `unit_price` e' `Decimal` e non `float`: psycopg restituisce `Decimal` per le
    colonne `numeric`, e su un prezzo l'aritmetica binaria dei float introduce
    errori che si vedono in fattura, non nei test.
    """

    code: str
    description: str
    unit_of_measure: str
    unit_price: Decimal
    stock_qty: int
