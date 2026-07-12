from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.prompts import WRITER_PROMPT
from backend.services.openai_service import get_llm


writer_llm = get_llm()


async def writer_agent(state: ResearchState) -> ResearchState:
    logger.info("Writer Agent | Started")

    try:
        research_sources = state.get("research_sources", [])

        if not research_sources:
            raise ValueError("No verified research available.")

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

        prompt = f"""{WRITER_PROMPT}

User Query:
{state["query"]}

Verified Research:

{source_text}
"""

        response = await writer_llm.ainvoke(prompt)

        report = response.content.strip()

        if not report:
            raise ValueError("Writer produced an empty report.")

        state["final_report"] = report

        state["conversation_summary"] = (
            f"Previous query: {state['query']}\n"
            f"Generated a research report."
        )

        state["current_step"] = "completed"

        logger.info("Writer Agent | Report generated successfully.")

        return state

    except Exception as e:
        logger.exception("Writer Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state