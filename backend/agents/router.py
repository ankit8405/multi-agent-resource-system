from backend.graphs import state
from backend.graphs.state import ResearchState
from backend.logger import logger


VALID_ACTIONS = {
    "new_research",
    "follow_up",
    "compare",
    "elaborate",
    "rewrite",
    "summarize",
    "optimize",
}


async def router_agent(state: ResearchState) -> ResearchState:
    logger.info("Router Agent | Started")

    try:
        action = state.get("action", "new_research")

        if action not in VALID_ACTIONS:
            raise ValueError(f"Invalid routing action: {action}")

        logger.info(
            "Router Agent | action=%s",
            action,
        )

        if action in {
            "new_research",
            "follow_up",
            "compare",
            "elaborate",
        }:
            state["current_step"] = "research"

        elif action in {
            "rewrite",
            "summarize",
            "optimize",
        }:
            state["current_step"] = "writer"

        return state

    except Exception as e:
        logger.exception("Router Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state