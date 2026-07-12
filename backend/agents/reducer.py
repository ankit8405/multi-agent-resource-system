from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import ResearchSource


def normalize(text: str) -> str:
    return " ".join(text.lower().split())


async def reducer_agent(state: ResearchState) -> ResearchState:
    logger.info("Reducer Agent | Started")

    try:
        all_sources = (
            state.get("tavily_results", [])
            + state.get("exa_results", [])
            + state.get("arxiv_results", [])
            + state.get("semanticscholar_results", [])
            + state.get("openalex_results", [])
        )

        if not all_sources:
            raise ValueError("No research sources available.")

        best_sources: dict[str, ResearchSource] = {}

        for source in all_sources:

            if not source.content.strip():
                continue

            key = normalize(source.title)

            if key not in best_sources:
                best_sources[key] = source
                continue

            current = best_sources[key]

            # Keep the version with the richer content
            if len(source.content) > len(current.content):
                best_sources[key] = source

        unique_sources = list(best_sources.values())

        unique_sources.sort(
            key=lambda x: (
                len(x.content),
                x.title.lower(),
            ),
            reverse=True,
        )

        state["research_sources"] = unique_sources
        state["current_step"] = "fact_check"

        logger.info(
            "Reducer Agent | Reduced %d -> %d sources",
            len(all_sources),
            len(unique_sources),
        )

        return state

    except Exception as e:
        logger.exception("Reducer Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state