from langchain_openai import ChatOpenAI
from backend.config import settings
from typing import Type

_llm = None

def get_llm(temperature: float = 0) -> ChatOpenAI:
    global _llm

    if _llm is None:
        _llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=settings.OPEN_AI_MODEL,
            temperature=temperature,
        )

    return _llm

def get_structured_llm(schema: Type):
    return get_llm().with_structured_output(schema)

def invoke_structured(prompt: str, schema: Type):
    return get_structured_llm(schema).invoke(prompt)