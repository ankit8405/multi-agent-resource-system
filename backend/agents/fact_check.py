from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import FactCheckOutput
from backend.prompts import FACT_CHECK_PROMPT
from backend.services.openai_service import get_structured_llm


fact_checker_llm = get_structured_llm(FactCheckOutput)


async def fact_checker_agent(state: ResearchState) -> ResearchState:
    logger.info("Fact Checker Agent | Started")

    try:
        research_sources = state.get("research_sources", [])

        if not research_sources:
            raise ValueError("No research sources available for verification.")

        source_text = "\n\n".join(
            f"""
Title: {source.title}

Source: {source.source}

URL: {source.url}

Content:
{source.content}
"""
            for source in research_sources
        )

        prompt = f"""{FACT_CHECK_PROMPT}

User Query:
{state["query"]}

Research Sources:

{source_text}
"""

        result: FactCheckOutput = await fact_checker_llm.ainvoke(prompt)

        state["fact_check_result"] = result
        state["research_sources"] = result.verified_sources
        state["current_step"] = "writer"

        logger.info(
            "Fact Checker Agent | Verified %d sources",
            len(result.verified_sources),
        )

        return state

    except Exception as e:
        logger.exception("Fact Checker Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state