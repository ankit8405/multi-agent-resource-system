from typing import TypedDict

from backend.models import (
    PlannerOutput,
    ResearchSource,
    FactCheckOutput,
)


class ResearchState(TypedDict, total=False):

    # user
    query: str

    # workflow
    current_step: str
    action: str

    # summary
    previous_query: str
    conversation_summary: str
    
    # planner
    research_plan: PlannerOutput | None

    # retrieval
    tavily_results: list[ResearchSource]
    exa_results: list[ResearchSource]
    arxiv_results: list[ResearchSource]
    semanticscholar_results: list[ResearchSource]
    openalex_results: list[ResearchSource]

    # combined research
    research_sources: list[ResearchSource]

    # fact checking
    fact_check_result: FactCheckOutput | None

    # current report
    final_report: str

    # errors
    errors: list[str]

def create_initial_state(
    query: str,
    previous_query: str = "",
    conversation_summary: str = "") -> ResearchState:
    return {
        "query": query,
        "previous_query": previous_query,
        "conversation_summary": conversation_summary,
        "action": "new_research",
        "current_step": "planning",
        "research_plan": None,
        "tavily_results": [],
        "exa_results": [],
        "arxiv_results": [],
        "semanticscholar_results": [],
        "openalex_results": [],
        "research_sources": [],
        "fact_check_result": None,
        "final_report": "",
        "errors": [],
    }