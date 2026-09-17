from typing import Self

from pydantic import BaseModel, Field, model_validator

from erp_agent_graph.models.extracted_customer_address import ExtractedCustomerAddress
from erp_agent_graph.models.extracted_order_line import ExtractedOrderLine


class ExtractedOrder(BaseModel):
    customer_reference: str | None = Field(
        description="Customer reference as you find in the email. "
        "It should be some sort of code or identifier, "
        "that customer use to refer that order "
        "but is not always there. Please leave it blank if you can't find it. "
        "example: OD20261012, PO-2311444"
    )
    shipping_address_id: int | None = Field(
        default=None,
        description="Id of the delivery address, ONLY when the email says where to "
        "deliver AND you matched it against the customer addresses with the tool. "
        "Leave it empty otherwise: the default address will be used.",
    )
    shipping_address: ExtractedCustomerAddress | None = Field(
        default=None,
        description="The delivery place named in the email when it matches none of the "
        "customer addresses. Fill either this or shipping_address_id, never both: "
        "a person will decide whether to add it to the customer.",
    )
    lines: list[ExtractedOrderLine] = Field(description="Order lines")

    @model_validator(mode="after")
    def only_one(self) -> Self:
        if self.shipping_address_id and self.shipping_address:
            raise ValueError(
                "Fill either shipping_address_id or shipping_address, not both: "
                "use the id when the address is already the customer's, "
                "the other one when the email names a place you could not match"
            )
        return self
