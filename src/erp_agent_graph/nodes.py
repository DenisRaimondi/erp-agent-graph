import logging

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from erp_agent_graph.context import Context
from erp_agent_graph.models.customer_choice import CustomerChoice
from erp_agent_graph.models.verdict import Verdict
from erp_agent_graph.state import State
from erp_agent_graph.tools.customers import (
    find_customer_by_domain,
    find_customer_by_email,
    search_customers_by_name,
)

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


def extract_customer(state: State, runtime: Runtime[Context]) -> dict:

    SYSTEM_PROMPT = """
        you must extract the customer from the email provided.
        Use the minimum amount of tools that allow you to identify clearly the customer.
        Try to follow at least these rules:
        1. try exact email first that you found from sender
        2. assigning a wrong customer is worse then not assigning one
        3. if you can't manage to assign None to customer_id """

    agent = create_agent(
        runtime.context.llm_model,
        [find_customer_by_email, find_customer_by_domain, search_customers_by_name],
        system_prompt=SYSTEM_PROMPT,
        # ToolStrategy: l'output strutturato passa da una chiamata a tool invece che dal
        # response_format nativo del provider, che DeepSeek non supporta (400 "This
        # response_format type is not supported"). E' lo stesso motivo per cui in
        # classify usiamo with_structured_output(method="function_calling").
        response_format=ToolStrategy(CustomerChoice),
        context_schema=Context,
    )

    # create_agent costruisce un grafo LangGraph, quindi invoke restituisce lo stato
    # finale dell'agente, non una risposta secca:
    #   ["messages"]            tutto lo scambio, richieste di tool comprese
    #   ["structured_response"] il CustomerChoice, perche' abbiamo passato response_format
    customer = agent.invoke(
        {"messages": [HumanMessage(state["email"].to_prompt())]}, context=runtime.context
    )["structured_response"]

    logger.info("Mail %s, cliente scelto: %s", state["email"].id, customer)

    return {"customer_choice": customer}
