from erp_agent_graph.models.customer_address import CustomerAddress
from erp_agent_graph.services.base_repository import BaseRepository


class CustomerAddressRepository(BaseRepository):
    def find_customer_address_by_customer_id(self, customer_id: int) -> list[CustomerAddress]:
        return self._get_all(
            CustomerAddress,
            "SELECT customer_addresses.* FROM customer_addresses WHERE customer_id =%s",
            (customer_id,),
        )
