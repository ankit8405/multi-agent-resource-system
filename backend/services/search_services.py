import asyncio
from tavily import TavilyClient
from exa_py import Exa
from arxiv import Client as ArxivClient
from arxiv import Search
from semanticscholar import SemanticScholar

from backend.config import settings
from backend.logger import logger
from backend.models import ResearchSource
from backend.constants import VALID_PROVIDERS
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

def reconstruct_openalex_abstract(
    inverted_index: dict[str, list[int]] | None,
) -> str:
    if not inverted_index:
        return ""
    try:
        ordered_words = []
        for word, positions in inverted_index.items():
            for pos in positions:
                ordered_words.append((pos, word))
        ordered_words.sort(key=lambda x: x[0])
        return " ".join(word for _, word in ordered_words)
    except Exception as e:
        logger.warning("Failed to reconstruct abstract: %s", e)
        return ""

def tavily_search(query: str, max_results: int = 5) -> list[ResearchSource]:
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
                score=res.get("score")
            ))
        return results

    except Exception:
        logger.exception("Tavily search failed.")
        return []

def exa_search(query: str, max_results: int = 5) -> list[ResearchSource]:
    logger.info("Searching Exa | query=%s", query)

    try:
        client = get_exa()
        response = client.search_and_contents(
            query,
            num_results=max_results,
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
                score=getattr(res, "score", None) 
            ))
        return results

    except Exception:
        logger.exception("Exa search failed.")
        return []

def arxiv_search(query: str, max_results: int = 5) -> list[ResearchSource]:
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
                authors=[
                    author.name
                    for author in res.authors
                ],
                published_date=(
                    res.published.date().isoformat()
                    if res.published
                    else None
                ),
                doi=res.doi,
            ))
        return results

    except Exception:
        logger.exception("arXiv search failed.")
        return []

def semantic_scholar_search(query: str, max_results: int = 5) -> list[ResearchSource]:
    logger.info("Searching Semantic Scholar | query=%s", query)

    try:
        client = get_semantic_scholar()
        response = client.search_paper(
            query=query,
            limit=max_results,
            fields=["title", "url", "abstract"]
        )
        
        results = []
        for paper in response:
            results.append(ResearchSource(
                title=getattr(paper, "title", "") or "",
                source="semanticscholar",
                url=getattr(paper, "url", "") or "",
                content=getattr(paper, "abstract", "") or "",
                authors=[
                    a.name
                    for a in getattr(paper, "authors", [])
                ],
                published_date=(
                    str(getattr(paper, "year"))
                    if getattr(paper, "year", None)
                    else None
                ),
                doi=getattr(paper, "doi", None),
            ))
        return results

    except Exception:
        logger.exception("Semantic Scholar search failed.")
        return []

async def openalex_search(query: str, max_results: int = 5) -> list[ResearchSource]:
    logger.info("Searching OpenAlex | query=%s", query)

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                "https://api.openalex.org/works",
                params={
                    "search": query,
                    "per_page": max_results,
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
                    authors=[
                        author["author"]["display_name"]
                        for author in work.get("authorships", [])
                        if author.get("author", {}).get("display_name")
                    ],
                    published_date=work.get("publication_date"),
                    doi=work.get("doi"),
                ))
            return results

    except Exception:
        logger.exception("OpenAlex search failed.")
        return []


async def search_all(
    query: str,
    providers: list[str],
    max_results: int = 5,
) -> dict[str, list[ResearchSource]]:
    tasks: dict[str, asyncio.Future] = {}

    unknown = set(providers) - VALID_PROVIDERS

    if unknown:
        logger.warning(
            "Unknown providers requested: %s",
            ", ".join(sorted(unknown)),
        )

    if "tavily" in providers:
        tasks["tavily"] = asyncio.to_thread(tavily_search, query, max_results)

    if "exa" in providers:
        tasks["exa"] = asyncio.to_thread(exa_search, query, max_results)

    if "arxiv" in providers:
        tasks["arxiv"] = asyncio.to_thread(arxiv_search, query, max_results)

    if "semanticscholar" in providers:
        tasks["semanticscholar"] = asyncio.to_thread(
            semantic_scholar_search,
            query, max_results
        )

    if "openalex" in providers:
        tasks["openalex"] = openalex_search(query, max_results)

    if not tasks:
        raise ValueError("No valid providers selected.")
    
    results = await asyncio.gather(
        *tasks.values(),
        return_exceptions=True,
    )
    logger.info(
        "Research Service | Raw results: %s",
        [type(r).__name__ for r in results],
    )
    
    provider_results: dict[str, list[ResearchSource]] = {
        provider: []
        for provider in providers
    }
    failed_providers: list[str] = []

    for provider, result in zip(tasks.keys(), results):
        if isinstance(result, Exception):
            logger.error("Research Service | %s search failed | %s", provider, result)
            failed_providers.append(provider)
            provider_results[provider] = []
            continue

        provider_results[provider] = result
    
    if len(failed_providers) == len(tasks):
        raise RuntimeError(
            f"All providers failed: {', '.join(failed_providers)}"
        )

    total_sources = sum(
        len(sources)
        for sources in provider_results.values()
    )

    logger.info(
        "Research Service | query=%s | %s | total=%d",
        query,
        ", ".join(
            f"{provider}={len(sources)}"
            for provider, sources in provider_results.items()
        ),
        total_sources,
    )

    return provider_results