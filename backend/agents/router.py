from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.constants import RESEARCH_ACTIONS, WRITER_ACTIONS

async def router_agent(state: ResearchState) -> ResearchState:
    logger.info("Router Agent | Started")

    try:
        plan = state.get("research_plan")
        if plan is None:
            raise ValueError("Research plan not found.")
            
        action = plan.action
        state["action"] = action

        if action in RESEARCH_ACTIONS:
            if not plan.search_queries:
                raise ValueError("Planner produced no search queries.")

            if not plan.providers:
                raise ValueError("Planner selected no providers.")
            state["current_step"] = "research"

        elif action in WRITER_ACTIONS:
            state["current_step"] = "writer"
            
        else:
            raise ValueError(f"Invalid routing action: {action}")

        if action in RESEARCH_ACTIONS:
            logger.info(
                "Router Agent | action=%s -> research | providers=%s | strategy=%s",
                action,
                ",".join(plan.providers),
                plan.comparison_strategy,
            )
        else:
            logger.info(
                "Router Agent | action=%s -> writer",
                action,
            )

        return state

    except Exception as e:
        logger.exception("Router Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state