from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.prompts import WRITER_PROMPT
from backend.services.openai_service import get_llm

async def writer_agent(
    state: ResearchState,
) -> ResearchState:
    writer_llm = get_llm()

    logger.info("Writer Agent | Started")

    try:

        plan = state.get("research_plan")

        if plan is None:
            raise ValueError("Research plan not found.")

        web_findings = state.get(
            "verified_web_findings",
            [],
        )

        academic_findings = state.get(
            "verified_academic_findings",
            [],
        )

        if not web_findings and not academic_findings:
            raise ValueError("No verified findings available.")

        prompt = f"""
{WRITER_PROMPT}

Objective:
{plan.objective}

Report Sections:
{plan.report_sections}

Web Findings:
{web_findings}

Academic Findings:
{academic_findings}
"""

        report = await writer_llm.ainvoke(prompt)

        final_report = report.content.strip()
        state["report"] = final_report
        state["final_report"] = final_report
        state["current_step"] = "completed"

        logger.info(
            "Writer Agent | Report generated | %d characters",
            len(final_report),
        )

        return state

    except Exception as e:

        logger.exception("Writer Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state