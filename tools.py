from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv
from rich import print

load_dotenv()

tavily = TavilySearch(
    max_results=5,
    includeImages=False,
    # searchDepth="advanced"
)

@tool
def web_search(query : str) -> str :
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets ."""

    results = tavily.invoke({"query": query})

    out = []
    for result in results['results']:
        out.append(f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}\n")

    return "\n---\n".join(out)


@tool
def scrape_url(url : str) -> str :
    """Scrape and return clean text content from a given url for deeper reading"""

    try :
        resp = requests.get(url , timeout=8 , headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text , 'html.parser')
        for tag in soup(['script' , 'style', 'nav' ,'footer']) :
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e :
        return f"Could not scrape URL : {str(e)}"