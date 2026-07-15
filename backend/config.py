import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")
    EXA_API_KEY: str = os.getenv("EXA_API_KEY", "")

    POSTGRES_HOST = os.getenv("POSTGRES_HOST","localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT","5432"))
    POSTGRES_DB = os.getenv("POSTGRES_DB","research")
    POSTGRES_USER = os.getenv("POSTGRES_USER","postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","postgres")

    DATABASE_URL: str = (
        f"postgresql+psycopg://"
        f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_SOCKET_TIMEOUT: float = float(os.getenv("REDIS_SOCKET_TIMEOUT", "2.0"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    REPORT_CACHE_TTL: int = int(os.getenv("REPORT_CACHE_TTL", "86400"))
    SEARCH_CACHE_TTL: int = int(os.getenv("SEARCH_CACHE_TTL", "3600"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()
