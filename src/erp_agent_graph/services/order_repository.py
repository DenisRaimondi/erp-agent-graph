from erp_agent_graph.models.order_line import OrderLine
from erp_agent_graph.services.base_repository import BaseRepository


class OrderRepository(BaseRepository):
    def get_last_n_orders_lines_by_customer(
        self, customer_id: int, limit: int = 30
    ) -> list[OrderLine]:
        """Le righe degli ordini piu' recenti di un cliente.

        Servono a dare al modello un riferimento su cosa compra abitualmente:
        quando la mail e' vaga ("le solite guarnizioni") o il codice e' storpiato,
        lo storico dice quali articoli sono plausibili per quel cliente.
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
