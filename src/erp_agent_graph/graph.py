from langgraph.graph import END, START, StateGraph

from erp_agent_graph.context import Context
from erp_agent_graph.nodes import classify
from erp_agent_graph.state import PartialState, State

builder = StateGraph(state_schema=State, context_schema=Context, input_schema=PartialState)
builder.add_node("classify", classify)
builder.add_edge(START, "classify")
builder.add_edge("classify", END)
