import asyncio

from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import (
    FactCheckOutput,
    ResearchFinding,
)
from backend.prompts import FACT_CHECK_PROMPT
from backend.services.openai_service import get_structured_llm


async def verify_findings(
    findings: list[ResearchFinding],
) -> FactCheckOutput:
    fact_checker_llm = get_structured_llm(FactCheckOutput)
    prompt = f"""
{FACT_CHECK_PROMPT}

Research Findings:

{findings}
"""

    return await fact_checker_llm.ainvoke(prompt)


async def fact_checker_agent(
    state: ResearchState,
) -> ResearchState:

    logger.info("Fact Checker | Started")

    try:

        web_findings = state.get("web_findings", [])
        academic_findings = state.get("academic_findings", [])

        tasks = {}

        if web_findings:
            tasks["web"] = verify_findings(web_findings)

        if academic_findings:
            tasks["academic"] = verify_findings(academic_findings)

        if not tasks:
            raise ValueError("No findings available for verification.")

        outputs = await asyncio.gather(
            *tasks.values(),
            return_exceptions=True,
        )

        results: dict[str, FactCheckOutput] = {}

        for name, output in zip(tasks.keys(), outputs):

            if isinstance(output, Exception):
                logger.warning(
                    "Fact Checker | %s verification failed | %s",
                    name,
                    output,
                )
                continue

            results[name] = output

        if not results:
            raise ValueError("Fact Checker produced no verified findings.")

        web_output = results.get("web")
        academic_output = results.get("academic")

        if web_output and web_output.issues:
            logger.warning(
                "Fact Checker | Web issues=%d",
                len(web_output.issues),
            )

        if academic_output and academic_output.issues:
            logger.warning(
                "Fact Checker | Academic issues=%d",
                len(academic_output.issues),
            )

        state["verified_web_findings"] = (
            web_output.verified_findings
            if web_output
            else []
        )

        state["verified_academic_findings"] = (
            academic_output.verified_findings
            if academic_output
            else []
        )

        state["current_step"] = "writer"

        logger.info(
            "Fact Checker | verified_web=%d verified_academic=%d",
            len(state["verified_web_findings"]),
            len(state["verified_academic_findings"]),
        )

        return state

    except Exception as e:

        logger.exception("Fact Checker failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state