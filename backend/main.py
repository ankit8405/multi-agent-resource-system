from fastapi import FastAPI
from backend.api.routes import routes
from backend.logger import logger
from backend.services.db import init_db
from backend.services.caching import cache


app = FastAPI(
    title="Multi Agent Research System",
    version="1.0.0"
)

app.include_router(routes, prefix="/api")

@app.on_event("startup")
async def on_startup():
    logger.info("Initializing backend...")

    try:
        init_db()
        logger.info("Database initialized.")
        logger.info("Backend started successfully.")
    except Exception:
        logger.exception("Failed to initialize backend.")
        raise

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await cache.close()
        logger.info("Backend shutdown complete.")
    except Exception:
        logger.exception("Failed during shutdown.")

@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "multi_agent_research_system"}
