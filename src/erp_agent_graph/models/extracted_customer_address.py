from pydantic import BaseModel, Field

from erp_agent_graph.models.customer_address import AddressKind


class ExtractedCustomerAddress(BaseModel):
    """An address as written in an email, not yet in the ERP.

    Needed in the two cases where an address has to be *created* instead of
    picked: a new customer, and a destination the customer names that is not
    among their registered addresses.

    Not a `CustomerAddress`: that one has an `id` and a `customer_id` because it
    exists in the database. This is text read from an email, and becomes a real
    address only once a person confirms it.
    """

    kind: AddressKind = Field(
        default="shipping",
        description="'headquarters' for the company address, 'shipping' for a delivery "
        "destination, 'billing' when the email tells them apart.",
    )
    street: str | None = Field(
        default=None, description="Street and number, as written in the email."
    )
    postal_code: str | None = Field(
        default=None, description="Postal code, only if the email states it."
    )
    city: str | None = Field(default=None, description="Town or city.")
    province: str | None = Field(default=None, description="Two-letter province code, e.g. 'MI'.")
    country: str = Field(default="IT", description="Country code, 'IT' when not specified.")

    raw: str | None = Field(
        default=None,
        description="The original sentence naming the place, when you cannot break it "
        "down into street, postal code and city (e.g. 'al cantiere di Collegno'). "
        "Copy it, do not rewrite it.",
    )
