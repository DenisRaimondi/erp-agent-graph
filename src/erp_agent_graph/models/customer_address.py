from typing import Literal

from pydantic import BaseModel

AddressKind = Literal["sede", "spedizione", "fatturazione"]


class CustomerAddress(BaseModel):
    """Indirizzo di un cliente. Rispecchia la tabella `customer_addresses`.

    Un ordine si consegna a un indirizzo, non a un'azienda: per questo
    `orders.shipping_address_id` punta qui e non a `customers`.
    """

    id: int
    customer_id: int
    kind: AddressKind
    street: str
    postal_code: str
    city: str
    province: str
    country: str
    is_default: bool
