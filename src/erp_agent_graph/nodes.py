import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.verdict import Verdict
from erp_agent_graph.state import State

logger = logging.getLogger(__name__)


def classify(state: State, runtime: Runtime[Context]) -> dict:
    email = state["email"]

    SYSTEM_PROMPT = (
        "You are an email classification agent. "
        "Your task is to analyze the content of the email and determine various topic categories."
    )

    verdict = (
        runtime.context.llm_model.with_structured_output(Verdict, method="function_calling")
        .with_retry(stop_after_attempt=3)
        .invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=email.to_prompt())])
    )

    logger.info("Mail %s classificata come %s", email.id, verdict)

    return {"verdict": verdict}
