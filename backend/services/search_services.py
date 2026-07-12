from typing import Any
import asyncio
from typing import List
from tavily import TavilyClient
from exa_py import Exa
from arxiv import Client as ArxivClient
from arxiv import Search
from semanticscholar import SemanticScholar

from backend.config import settings
from backend.logger import logger
from backend.models import ResearchSource
import httpx

_tavily_client = None
_exa_client = None
_semantic_scholar_client = None
_arxiv_client = None

def get_tavily() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    return _tavily_client

def get_exa() -> Exa:
    global _exa_client
    if _exa_client is None:
        _exa_client = Exa(api_key=settings.EXA_API_KEY)
    return _exa_client

def get_semantic_scholar() -> SemanticScholar:
    global _semantic_scholar_client
    if _semantic_scholar_client is None:
        _semantic_scholar_client = SemanticScholar()
    return _semantic_scholar_client

def get_arxiv() -> ArxivClient:
    global _arxiv_client
    if _arxiv_client is None:
        _arxiv_client = ArxivClient()
    return _arxiv_client

def reconstruct_openalex_abstract(inverted_index: dict) -> str:
    if not inverted_index:
        return ""
    try:
        temp_abstract = []
        for word, positions in inverted_index.items():
            for pos in positions:
                temp_abstract.append((pos, word))
        temp_abstract.sort(key=lambda x: x[0])
        return " ".join([word for pos, word in temp_abstract])
    except Exception as e:
        logger.warning("Failed to reconstruct abstract: %s", e)
        return ""

def tavily_search(query: str, max_results: int = 5) -> List[ResearchSource]:
    logger.info("Searching Tavily | query=%s", query)

    try:
        client = get_tavily()
        response = client.search(
            query=query,
            max_results=max_results,
        )

        results = []
        for res in response.get("results", []):
            results.append(ResearchSource(
                title=res.get("title") or "",
                source="tavily",
                url=res.get("url") or "",
                content=res.get("content") or "",
            ))
        return results

    except Exception:
        logger.exception("Tavily search failed.")
        return []

def exa_search(query: str, num_results: int = 5) -> List[ResearchSource]:
    logger.info("Searching Exa | query=%s", query)

    try:
        client = get_exa()
        response = client.search_and_contents(
            query,
            num_results=num_results,
            text=True,
        )

        results = []
        for res in getattr(response, "results", []):
            content = getattr(res, "text", "") or ""
            if not content and hasattr(res, "highlights") and res.highlights:
                content = "\n".join(res.highlights)
            results.append(ResearchSource(
                title=getattr(res, "title", "") or "",
                source="exa",
                url=getattr(res, "url", "") or "",
                content=content,
            ))
        return results

    except Exception:
        logger.exception("Exa search failed.")
        return []

def arxiv_search(query: str, max_results: int = 5) -> List[ResearchSource]:
    logger.info("Searching ArXiv | query=%s", query)

    try:
        client = get_arxiv()
        search = Search(
            query=query,
            max_results=max_results,
        )

        results = []
        for res in client.results(search):
            results.append(ResearchSource(
                title=res.title or "",
                source="arxiv",
                url=res.entry_id or "",
                content=res.summary or "",
            ))
        return results

    except Exception:
        logger.exception("arXiv search failed.")
        return []

def semantic_scholar_search(query: str, limit: int = 5) -> List[ResearchSource]:
    logger.info("Searching Semantic Scholar | query=%s", query)

    try:
        client = get_semantic_scholar()
        response = client.search_paper(
            query=query,
            limit=limit,
            fields=["title", "url", "abstract"]
        )
        
        results = []
        for paper in response:
            results.append(ResearchSource(
                title=getattr(paper, "title", "") or "",
                source="semanticscholar",
                url=getattr(paper, "url", "") or "",
                content=getattr(paper, "abstract", "") or "",
            ))
        return results

    except Exception:
        logger.exception("Semantic Scholar search failed.")
        return []

async def openalex_search(query: str, per_page: int = 5) -> List[ResearchSource]:
    logger.info("Searching OpenAlex | query=%s", query)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.openalex.org/works",
                params={
                    "search": query,
                    "per_page": per_page,
                }
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for work in data.get("results", []):
                url_val = work.get("landing_page_url") or work.get("doi") or work.get("id") or ""
                results.append(ResearchSource(
                    title=work.get("title") or "",
                    source="openalex",
                    url=url_val,
                    content=reconstruct_openalex_abstract(work.get("abstract_inverted_index")),
                ))
            return results

    except Exception:
        logger.exception("OpenAlex search failed.")
        return []


async def search_all(query: str) -> dict[str, List[ResearchSource]]:
    (
        tavily_results,
        exa_results,
        arxiv_results,
        semantic_results,
        openalex_results,
    ) = await asyncio.gather(
        asyncio.to_thread(tavily_search, query),
        asyncio.to_thread(exa_search, query),
        asyncio.to_thread(arxiv_search, query),
        asyncio.to_thread(semantic_scholar_search, query),
        openalex_search(query),
        return_exceptions=True,
    )

    def safe(result: Any) -> List[ResearchSource]:
        if isinstance(result, Exception):
            logger.error("Search task failed: %s", result)
            return []
        return result
    
    return {
        "tavily": safe(tavily_results),
        "exa": safe(exa_results),
        "arxiv": safe(arxiv_results),
        "semanticscholar": safe(semantic_results),
        "openalex": safe(openalex_results),
    }