from backend.agents.planner import planner_agent
from backend.agents.router import router_agent
from backend.agents.researcher import researcher_agent
from backend.agents.comparator import comparator_agent
from backend.agents.fact_check import fact_checker_agent
from backend.agents.writer import writer_agent

from backend.graphs.state import ResearchState

async def planner_node(state: ResearchState) -> ResearchState:
    return await planner_agent(state)

async def router_node(state: ResearchState) -> ResearchState:
    return await router_agent(state)

async def research_node(state: ResearchState) -> ResearchState:
    return await researcher_agent(state)

async def comparator_node(state: ResearchState) -> ResearchState:
    return await comparator_agent(state)

async def fact_checker_node(state: ResearchState) -> ResearchState:
    return await fact_checker_agent(state)

async def writer_node(state: ResearchState) -> ResearchState:
    return await writer_agent(state)