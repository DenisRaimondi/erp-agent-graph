from langgraph.graph import END, START, StateGraph

from erp_agent_graph.context import Context
from erp_agent_graph.nodes import classify, extract_customer, extract_order
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
builder.add_node("extract_order", extract_order)
builder.add_edge(START, "classify")
# The third argument lists the possible destinations: without it LangGraph does not
# know the edges leaving this node, and extract_customer would look unreachable.
builder.add_conditional_edges("classify", route_from_classify, ["extract_customer", END])
builder.add_edge("extract_customer", "extract_order")
builder.add_edge("extract_order", END)
