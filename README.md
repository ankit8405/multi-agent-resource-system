# ResearchConclave

A four-stage multi-agent AI research pipeline built with [LangChain](https://python.langchain.com/)
and [Streamlit](https://streamlit.io/). Specialized agents collaborate to produce a
cited research report on any topic.

[ResearchConclave Live](http://3.219.124.98:8501/)

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
| `deploy/` | AWS EC2 deploy files: `setup-ec2.sh`, `nginx.conf`, and the full runbook |

## Deployment

[ResearchConclave Live](http://3.219.124.98:8501)

The app runs on a **`t3.micro` Ubuntu 24.04 LTS** instance as a **systemd service**
(`researchconclave`), so it starts on boot and restarts on crash.

One-time setup on a fresh instance:

```bash
# push the deploy files first, then on the EC2 box:
git clone https://github.com/ankit8405/multi-agent-resource-system.git
cd multi-agent-resource-system
bash deploy/setup-ec2.sh
```

Secrets live in `.env` on the server (never committed):

```bash
printf 'OPENAI_API_KEY=sk-...\nTAVILY_API_KEY=tvly-...\n' > .env
chmod 600 .env
sudo systemctl restart researchconclave
```

| Task | Command |
|------|---------|
| Deploy an update | `cd ~/multi-agent-resource-system && git pull && sudo systemctl restart researchconclave` |
| Restart | `sudo systemctl restart researchconclave` |
| Logs | `journalctl -u researchconclave -f` |
| Health check | `curl http://localhost:8501/_stcore/health` |

Stop / start the VM from the EC2 console (**Instance state → Stop / Start**); the Elastic
IP keeps the address stable across restarts.
