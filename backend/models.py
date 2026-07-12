from typing import List, Literal
from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research query provided by the user")
    thread_id: str | None = None
    previous_query: str = ""
    conversation_summary: str = ""

class PlannerOutput(BaseModel):
    action: Literal[
        "new_research",
        "follow_up",
        "compare",
        "elaborate",
        "rewrite",
        "summarize",
        "optimize",
    ]
    objective: str
    research_topics: list[str]
    search_queries: list[str]
    needs_web_search: bool
    needs_academic_search: bool
    needs_news_search: bool
    requires_fact_check: bool

class ResearchPlan(BaseModel):
    needs_web_search: bool
    needs_academic_search: bool
    needs_news_search: bool
    requires_fact_check: bool
    task: str

class ResearchSource(BaseModel):
    title: str
    source: str
    url: str
    content: str

class ResearchResponse(BaseModel):
    thread_id: str | None = None
    query: str
    report: str
    conversation_summary: str = ""

class FactCheckOutput(BaseModel):
    verified_sources: list[ResearchSource]
    issues: list[str]
    confidence: float