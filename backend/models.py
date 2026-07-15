from __future__ import annotations
from pydantic import BaseModel, Field
from backend.constants import Action, Provider, ComparisonStrategy

class ResearchRequest(BaseModel):
    query: str = Field(..., description="Research query provided by the user")
    thread_id: str | None = None
    previous_query: str = ""
    conversation_summary: str = ""

class PlannerOutput(BaseModel):
    action: Action
    objective: str
    search_queries: list[str]
    providers: list[Provider]
    comparison_strategy: ComparisonStrategy
    requires_fact_check: bool
    report_sections: list[str]

class ResearchSource(BaseModel):
    title: str
    source: Provider
    url: str
    content: str
    authors: list[str] = []
    published_date: str | None = None
    doi: str | None = None
    score: float | None = None

class ResearchFinding(BaseModel):
    claim: str
    summary: str
    supporting_sources: list[ResearchSource] = []
    conflicting_sources: list[ResearchSource] = []
    overall_confidence: float

class ComparisonOutput(BaseModel):
    findings: list[ResearchFinding]

class FactCheckOutput(BaseModel):
    verified_findings: list[ResearchFinding]
    issues: list[str]
    overall_confidence: float

class ResearchResponse(BaseModel):
    thread_id: str | None = None
    query: str
    report: str
    conversation_summary: str = ""