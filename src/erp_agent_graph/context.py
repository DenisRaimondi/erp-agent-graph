from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel

from erp_agent_graph.services.article_repository import ArticleRepository
from erp_agent_graph.services.customer_repository import CustomerRepository
from erp_agent_graph.services.order_repository import OrderRepository


@dataclass(frozen=True)
class Context:
    llm_model: BaseChatModel
    customer_repository: CustomerRepository
    article_repository: ArticleRepository
    order_repository: OrderRepository
