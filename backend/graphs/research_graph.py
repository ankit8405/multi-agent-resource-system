from langgraph.graph import StateGraph, START, END
from backend.graphs.state import ResearchState
from backend.graphs.nodes import (
    planner_node,
    router_node,
    research_node,
    fact_checker_node,
    writer_node,
    reducer_node,
)

def route(state: ResearchState) -> str:
    return state["action"]


def build_research_graph():
    research_graph = StateGraph(ResearchState)

    research_graph.add_node("planner", planner_node)
    research_graph.add_node("router", router_node)
    research_graph.add_node("research", research_node)
    research_graph.add_node("fact_checker", fact_checker_node)
    research_graph.add_node("writer", writer_node)
    research_graph.add_node("reducer", reducer_node)

    research_graph.add_edge(START, "planner")
    research_graph.add_edge("planner", "router")

    research_graph.add_conditional_edges(
        "router",
        route,
        {
            "new_research": "research",
            "follow_up": "research",
            "compare": "research",
            "elaborate": "research",

            "rewrite": "writer",
            "summarize": "writer",
            "optimize": "writer",
        },
    )

    research_graph.add_edge("research", "reducer")
    research_graph.add_edge("reducer", "fact_checker")
    research_graph.add_edge("fact_checker", "writer")
    research_graph.add_edge("writer", END)

    return research_graph.compile()

research_graph = build_research_graph()