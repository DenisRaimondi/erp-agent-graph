from typing import TypedDict

from erp_agent_graph.models.customer_choice import CustomerChoice
from erp_agent_graph.models.email import Email
from erp_agent_graph.models.extracted_order import ExtractedOrder
from erp_agent_graph.models.verdict import Verdict


class State(TypedDict):
    email: Email
    verdict: Verdict
    customer_choice: CustomerChoice
    extracted_order: ExtractedOrder
    confirmed_customer_id: int | None


class PartialState(TypedDict):
    email: Email


class CustomerDecision(TypedDict):
    customer_id: int
