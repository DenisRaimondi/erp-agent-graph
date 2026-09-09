from typing import TypedDict

from erp_agent_graph.models.email import Email
from erp_agent_graph.models.verdict import Verdict


class State(TypedDict):
    email: Email
    verdict: Verdict


class PartialState(TypedDict):
    email: Email
