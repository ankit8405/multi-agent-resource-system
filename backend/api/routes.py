from fastapi import APIRouter, HTTPException

from backend.graphs.research_graph import research_graph
from backend.graphs.state import create_initial_state
from backend.models import ResearchRequest
from backend.logger import logger

router = APIRouter()
    
@router.post("/research")
async def research_endpoint(request: ResearchRequest):
    logger.info(
        "Received research request | thread_id=%s | query=%s",
        request.thread_id,
        request.query,
    )
    try:
        result = await research_graph.ainvoke(
            create_initial_state(request.query, request.previous_query, request.conversation_summary),
            config={
                "configurable": {
                    "thread_id": request.thread_id,
                }
            },
        )

        return {
            "thread_id": request.thread_id,
            "query": request.query,
            "report": result["final_report"],
            "conversation_summary": result.get("conversation_summary", "")
        }
    except Exception:
        logger.exception(
            "Research workflow failed | thread_id=%s",
            request.thread_id,
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to generate research report.",
        )

routes = router