# Multi-Agent Research System

A four-stage AI research pipeline built with [LangChain](https://python.langchain.com/)
and [Streamlit](https://streamlit.io/). Specialized agents collaborate to produce a
cited research report on any topic.

## Pipeline

1. **Search Agent** – finds recent, reliable sources on the topic (Tavily web search).
2. **Reader Agent** – picks the most relevant URL and scrapes its content.
3. **Writer Chain** – drafts a structured research report from the gathered research.
4. **Critic Chain** – reviews the report and returns a score, strengths, and improvements.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- An OpenAI API key
- A Tavily API key

## Setup

```bash
uv sync
```

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

## Usage

Streamlit UI:

```bash
uv run streamlit run app.py
```

Command line:

```bash
uv run python pipeline.py
```

## Project layout

| File | Purpose |
|------|---------|
| `agents.py` | LLM setup, the search/reader agents and the writer/critic chains |
| `tools.py` | `web_search` (Tavily) and `scrape_url` (BeautifulSoup) tools |
| `pipeline.py` | CLI pipeline that runs all four steps |
| `app.py` | Streamlit UI wrapping the same pipeline |
