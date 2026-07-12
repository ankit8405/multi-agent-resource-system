from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import PlannerOutput
from backend.prompts import PLANNER_PROMPT
from backend.services.openai_service import get_structured_llm


planner_llm = get_structured_llm(PlannerOutput)


async def planner_agent(state: ResearchState) -> ResearchState:
    logger.info("Planner Agent | Started")

    try:
        prompt = f"""
            {PLANNER_PROMPT}

            User Query:
            {state["query"]}

            Previous Query:
            {state.get("previous_query", "")}

            Conversation Summary:
            {state.get("conversation_summary", "")}
        """

        plan: PlannerOutput = await planner_llm.ainvoke(prompt)

        VALID_ACTIONS = {
            "new_research",
            "follow_up",
            "compare",
            "elaborate",
            "rewrite",
            "summarize",
            "optimize",
        }

        if plan.action not in VALID_ACTIONS:
            raise ValueError(f"Invalid planner action: {plan.action}")

        logger.info(
            "Planner Agent | action=%s",
            plan.action,
        )
        state["research_plan"] = plan
        state["action"] = plan.action
        state["current_step"] = "routing"

        return state

    except Exception as e:
        logger.exception("Planner Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state