from langgraph.graph import END, START, StateGraph

from erp_agent_graph.context import Context
from erp_agent_graph.nodes import classify, extract_customer
from erp_agent_graph.state import PartialState, State


def route_from_classify(state: State) -> str:
    match state["verdict"].topic:
        case topics if "new_order_request" in topics:
            return "extract_customer"
        case _:
            return END


builder = StateGraph(state_schema=State, context_schema=Context, input_schema=PartialState)
builder.add_node("classify", classify)
builder.add_node("extract_customer", extract_customer)
builder.add_edge(START, "classify")
# Il terzo argomento elenca le destinazioni possibili: senza, LangGraph non conosce
# gli archi che partono da qui e il grafo risulterebbe con extract_customer isolato.
builder.add_conditional_edges("classify", route_from_classify, ["extract_customer", END])
builder.add_edge("extract_customer", END)
