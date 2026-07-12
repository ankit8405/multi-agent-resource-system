import logging
import sys
from backend.config import settings

LOGGER_NAME = "multi_agent_research_system"

def setup_logger(name: str = LOGGER_NAME) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.hasHandlers():
        logger.handlers.clear()

    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    
    logger.addHandler(handler)
    logger.propagate = False

    return logger

logger = setup_logger()