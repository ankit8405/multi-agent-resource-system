import asyncio
import time
from backend.graphs.state import ResearchState
from backend.models import ResearchSource
from backend.logger import logger
from backend.services.search_services import search_all


async def researcher_agent(state: ResearchState) -> ResearchState:
    logger.info("Research Agent | Started")

    try:
        plan = state.get("research_plan")

        if plan is None:
            raise ValueError("Research plan not found.")

        if not plan.search_queries:
            raise ValueError("Planner produced no search queries.")

        search_queries = list(
            dict.fromkeys(
                q.strip()
                for q in plan.search_queries
                if q.strip()
            )
        )

        if not plan.providers:
            raise ValueError("Planner selected no providers.")

        semaphore = asyncio.Semaphore(5)
        
        async def search(query: str) -> dict[str, list[ResearchSource]]:
            async with semaphore:
                return await search_all(
                    query,
                    providers=plan.providers,
                )
        
        start = time.perf_counter()

        logger.info(
                "Research Agent | Executing %d search queries",
                len(search_queries),
            )

        results = await asyncio.gather(
            *(search(query) for query in search_queries),
            return_exceptions=True,
        )

        provider_results: dict[str, list[ResearchSource]] = {
            provider: []
            for provider in plan.providers
        }

        for result in results:
            if isinstance(result, Exception):
                logger.warning(
                    "Research Agent | Search query failed | error=%s",
                    result,
                )
                continue

            if not isinstance(result, dict):
                logger.warning(
                    "Research Agent | Invalid search response: %r",
                    result,
                )
                continue

            for provider, sources in result.items():
                provider_results[provider].extend(sources)

        total_sources = sum(
            len(sources)
            for sources in provider_results.values()
        )

        if total_sources == 0:
            raise ValueError("No research sources were retrieved.")

        state["provider_results"] = provider_results

        state["current_step"] = "comparator"

        provider_stats = " ".join(
            f"{provider}={len(sources)}"
            for provider, sources in provider_results.items()
        )

        logger.info(
            "Research Agent | Finished | %s total=%d | %.2fs",
            provider_stats,
            total_sources,
            time.perf_counter() - start,
        )
        return state

    except Exception as e:
        logger.exception("Research Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state