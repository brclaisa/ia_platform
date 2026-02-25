from langgraph.graph import END, StateGraph

from app.agents.nodes.compliance import compliance_node
from app.agents.nodes.direct import direct_node
from app.agents.nodes.rag import rag_node
from app.agents.nodes.router import router_node
from app.agents.nodes.synthesizer import synthesizer_node
from app.agents.state import AgentState


def _check_compliance(state: AgentState) -> str:
    if state.get("is_compliant"):
        return "allowed"
    return "blocked"


def _get_route(state: AgentState) -> str:
    return state.get("route", "direct")


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("compliance", compliance_node)
    graph.add_node("router", router_node)
    graph.add_node("rag", rag_node)
    graph.add_node("direct", direct_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.set_entry_point("compliance")

    graph.add_conditional_edges(
        "compliance",
        _check_compliance,
        {"blocked": END, "allowed": "router"},
    )

    graph.add_conditional_edges(
        "router",
        _get_route,
        {"rag": "rag", "direct": "direct"},
    )

    graph.add_edge("rag", "synthesizer")
    graph.add_edge("direct", "synthesizer")
    graph.add_edge("synthesizer", END)

    return graph


def get_compiled_graph():
    graph = build_graph()
    return graph.compile()
