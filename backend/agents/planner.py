from backend.graphs.state import ResearchState
from backend.logger import logger
from backend.models import PlannerOutput
from backend.prompts import PLANNER_PROMPT
from backend.services.openai_service import get_structured_llm

async def planner_agent(state: ResearchState) -> ResearchState:
    planner_llm = get_structured_llm(PlannerOutput)
    logger.info("Planner Agent | Started")

    try:
        prompt = f"""{PLANNER_PROMPT}

        User Query:
        {state["query"]}

        Previous Query:
        {state.get("previous_query", "")}

        Conversation Summary:
        {state.get("conversation_summary", "")}
        """

        plan: PlannerOutput = await planner_llm.ainvoke(prompt)
        
        plan.search_queries = list(dict.fromkeys(
            q.strip()
            for q in plan.search_queries
            if q.strip()
        ))   
        plan.search_queries = plan.search_queries[:10]

        plan.providers = list(dict.fromkeys(
            p.strip().lower()
            for p in plan.providers
            if p.strip()
        ))

        plan.report_sections = list(
            dict.fromkeys(
                section.strip()
                for section in plan.report_sections
                if section.strip()
            )
        )[:10]  

        plan.objective = plan.objective.strip()
        
        if not plan.report_sections:
            raise ValueError("Planner produced no report sections.")

        if not plan.objective:
            raise ValueError("Planner produced no objective.")

        if not plan.providers:
            raise ValueError("Planner selected no providers.")

        logger.info(
            "Planner Agent | action=%s providers=%s queries=%d strategy=%s fact_check=%s",
            plan.action,
            ",".join(plan.providers),
            len(plan.search_queries),
            plan.comparison_strategy,
            plan.requires_fact_check,
        )

        state["research_plan"] = plan
        state["current_step"] = "routing"

        return state

    except Exception as e:
        logger.exception("Planner Agent failed.")

        state["errors"].append(str(e))
        state["current_step"] = "failed"

        return state