import asyncio
from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import ComparisonOutput, ResearchSource
from backend.prompts import WEB_COMPARATOR_PROMPT, ACADEMIC_COMPARATOR_PROMPT
from backend.services.openai_service import get_structured_llm

async def compare_web(
    sources: list[ResearchSource],
) -> ComparisonOutput:
    comparison_llm = get_structured_llm(ComparisonOutput)

    prompt = f"""
{WEB_COMPARATOR_PROMPT}
Sources:
{sources}
"""
    return await comparison_llm.ainvoke(prompt)

async def compare_academic(
    sources: list[ResearchSource],
) -> ComparisonOutput:
    comparison_llm = get_structured_llm(ComparisonOutput)

    prompt = f"""
{ACADEMIC_COMPARATOR_PROMPT}
Sources:
{sources}
"""

    return await comparison_llm.ainvoke(prompt)

async def comparator_agent(
    state: ResearchState,
) -> ResearchState:

    logger.info("Comparator Agent | Started")

    try:

        provider_results = state.get("provider_results")

        if not provider_results:
            raise ValueError("No provider results found.")

        web_sources = (
            provider_results.get("tavily", [])
            + provider_results.get("exa", [])
        )

        academic_sources = (
            provider_results.get("arxiv", [])
            + provider_results.get("semanticscholar", [])
            + provider_results.get("openalex", [])
        )

        logger.info(
            "Comparator Agent | web=%d academic=%d",
            len(web_sources),
            len(academic_sources),
        )

        tasks = {}

        if web_sources:
            tasks["web"] = compare_web(web_sources)

        if academic_sources:
            tasks["academic"] = compare_academic(academic_sources)

        if not tasks:
            raise ValueError("No sources available for comparison.")

        outputs = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True,
        )

        results: dict[str, ComparisonOutput] = {}
        for name, output in zip(tasks.keys(), outputs):
            if isinstance(output, Exception):
                logger.warning(
                    "Comparator Agent | %s comparison failed | %s",
                    name,
                    output,
                )
                continue
            results[name] = output
            
        if not results:
            raise ValueError("Comparator produced no comparison results.")

        web_output = results.get("web")
        academic_output = results.get("academic")

        if web_output and not web_output.findings:
            logger.warning(
                "Comparator Agent | Web comparator produced no findings."
            )

        if academic_output and not academic_output.findings:
            logger.warning(
                "Comparator Agent | Academic comparator produced no findings."
            )

        state["web_findings"] = (
            web_output.findings
            if web_output
            else []
        )

        state["academic_findings"] = (
            academic_output.findings
            if academic_output
            else []
        )

        state["current_step"] = "fact_check"

        logger.info(
            "Comparator Agent | web_findings=%d academic_findings=%d",
            len(state["web_findings"]),
            len(state["academic_findings"]),
        )

        return state

    except Exception as e:

        logger.exception("Comparator Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state