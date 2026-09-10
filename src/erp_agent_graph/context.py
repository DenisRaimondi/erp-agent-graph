from dataclasses import dataclass

from langchain_core.language_models import BaseChatModel

from erp_agent_graph.services.customer_repository import CustomerRepository


@dataclass(frozen=True)
class Context:
    llm_model: BaseChatModel
    customer_repository: CustomerRepository
