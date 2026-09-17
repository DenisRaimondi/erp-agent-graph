from langchain_core.tools import tool
from langgraph.runtime import get_runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.order_line import OrderLine


@tool
def get_last_n_orders_lines_by_customer(customer_id: int, limit: int) -> list[OrderLine]:
    """
    Provide a list of all orders lines by customer:
    1. list is ordered by day of creation
    2. the list is limited by the limit parameter, which defaults to 30
    """
    order_repository = get_runtime(Context).context.order_repository

    return order_repository.get_last_n_orders_lines_by_customer(customer_id, limit)
