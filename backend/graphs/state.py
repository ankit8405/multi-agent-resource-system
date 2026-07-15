from typing import TypedDict
from backend.models import PlannerOutput, ResearchSource, FactCheckOutput, ResearchFinding
from backend.constants import Action, WorkflowStep



class ResearchState(TypedDict, total=False):

    # user
    query: str

    # workflow
    current_step: WorkflowStep
    action: Action

    # summary
    previous_query: str
    conversation_summary: str
    
    # planner
    research_plan: PlannerOutput | None

    # retrieval
    provider_results: dict[str, list[ResearchSource]]

    # comparator
    web_findings: list[ResearchFinding]
    academic_findings: list[ResearchFinding]

    # fact checking
    verified_web_findings: list[ResearchFinding]
    verified_academic_findings: list[ResearchFinding]

    # current report
    report: str
    final_report: str

    # errors
    errors: list[str]

def create_initial_state(
    query: str,
    previous_query: str = "",
    conversation_summary: str = "",
) -> ResearchState:
    return {
        "query": query,
        "previous_query": previous_query,
        "conversation_summary": conversation_summary,
        "action": "new_research",
        "current_step": "planning",
        "research_plan": None,
        "provider_results": {},
        "web_findings": [],
        "academic_findings": [],
        "verified_web_findings": [],
        "verified_academic_findings": [],
        "report": "",
        "final_report": "",
        "errors": [],
    }