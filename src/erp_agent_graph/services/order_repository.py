from erp_agent_graph.models.order_line import OrderLine
from erp_agent_graph.services.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    def get_last_n_orders_lines_by_customer(
        self, customer_id: int, limit: int = 30
    ) -> list[OrderLine]:
        """The lines of a customer's most recent orders.

        They give the model a reference on what this customer usually buys:
        when the email is vague ("the usual gaskets") or the code is mangled, the
        history tells which articles are plausible for that customer.
        """
        return self._get_all(
            OrderLine,
            """
            SELECT order_lines.*
            FROM orders
            JOIN order_lines ON order_lines.order_id = orders.id
            WHERE orders.customer_id = %s
            ORDER BY orders.order_date DESC
            LIMIT %s
            """,
            (customer_id, limit),
        )
