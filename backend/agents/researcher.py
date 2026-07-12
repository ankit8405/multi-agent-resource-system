import asyncio
from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.services.search_services import search_all


async def researcher_agent(state: ResearchState) -> ResearchState:
    logger.info("Research Agent | Started")

    try:
        plan = state.get("research_plan")

        if plan is None:
            raise ValueError("Research plan not found.")

        search_queries = plan.search_queries

        if not search_queries:
            raise ValueError("Planner produced no search queries.")

        logger.info(
            "Research Agent | Executing %d search queries",
            len(search_queries),
        )

        results = await asyncio.gather(
            *(search_all(query) for query in search_queries),
            return_exceptions=True,
        )

        tavily_results = []
        exa_results = []
        arxiv_results = []
        semanticscholar_results = []
        openalex_results = []

        for result in results:
            if isinstance(result, Exception):
                logger.warning("Research Agent | Search query failed | error=%s", result)
                continue
            tavily_results.extend(result["tavily"])
            exa_results.extend(result["exa"])
            arxiv_results.extend(result["arxiv"])
            semanticscholar_results.extend(result["semanticscholar"])
            openalex_results.extend(result["openalex"])

        total_sources = (
            len(tavily_results)
            + len(exa_results)
            + len(arxiv_results)
            + len(semanticscholar_results)
            + len(openalex_results)
        )

        if total_sources == 0:
            raise ValueError("No research sources were retrieved.")

        state["tavily_results"] = tavily_results
        state["exa_results"] = exa_results
        state["arxiv_results"] = arxiv_results
        state["semanticscholar_results"] = semanticscholar_results
        state["openalex_results"] = openalex_results

        state["current_step"] = "reducer"

        logger.info(
            "Research Agent | Finished | %d total sources", total_sources
        )
        return state

    except Exception as e:
        logger.exception("Research Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state