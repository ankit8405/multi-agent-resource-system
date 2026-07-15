from langchain_openai import ChatOpenAI
from backend.config import settings
from typing import Any, Type

_llm: ChatOpenAI | None = None

def get_llm() -> ChatOpenAI:
    global _llm

    if _llm is None:
        _llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPENAI_MODEL,
            temperature=0,
        )

    return _llm

def get_structured_llm(schema: Type) -> Any:
    return get_llm().with_structured_output(schema)