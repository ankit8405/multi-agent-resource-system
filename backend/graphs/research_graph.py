from backend.constants import RESEARCH_ACTIONS, WRITER_ACTIONS
from langgraph.graph import StateGraph, START, END
from backend.graphs.state import ResearchState
from backend.graphs.nodes import (
    planner_node,
    router_node,
    research_node,
    comparator_node,
    fact_checker_node,
    writer_node,
)

def route(state: ResearchState) -> str:
    if state.get("current_step") == "failed":
        return END

    plan = state.get("research_plan")

    if plan is None:
        return END

    if (
        plan.action not in RESEARCH_ACTIONS
        and plan.action not in WRITER_ACTIONS
    ):
        return END

    return plan.action

def build_research_graph():
    research_graph = StateGraph(ResearchState)

    research_graph.add_node("planner", planner_node)
    research_graph.add_node("router", router_node)
    research_graph.add_node("research", research_node)
    research_graph.add_node("comparator", comparator_node)
    research_graph.add_node("fact_checker", fact_checker_node)
    research_graph.add_node("writer", writer_node)

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

    research_graph.add_edge("research", "comparator")
    research_graph.add_edge("comparator", "fact_checker")
    research_graph.add_edge("fact_checker", "writer")
    research_graph.add_edge("writer", END)

    return research_graph.compile()

research_graph = build_research_graph()