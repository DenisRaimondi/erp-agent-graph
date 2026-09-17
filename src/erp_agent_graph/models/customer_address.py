from typing import Literal

from pydantic import BaseModel

AddressKind = Literal["headquarters", "shipping", "billing"]


class CustomerAddress(BaseModel):
    """A customer address. Mirrors the `customer_addresses` table.

    An order is delivered to an address, not to a company: that is why
    `orders.shipping_address_id` points here and not at `customers`.
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
