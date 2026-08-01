# AI Salary Insights Agent with MCP & Conversational Memory

A Python CLI agent that answers salary-related questions by scraping real salary data (Glassdoor, AmbitionBox, PayScale, Levels.fyi) via Firecrawl tools loaded through Composio MCP, reasoned over by Google Gemini, with LangGraph conversation memory.

## Features

- Gemini chat model through LangChain
- Firecrawl search + scrape tools through Composio MCP
- LangGraph in-memory conversation checkpointing (multi-turn follow-ups)
- `.env` based configuration
- Query via `--query` flag, or interactive prompt if not given

## Project Structure

```text
MCP_SalaryInsights_Agent/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## Requirements

- Python 3.11 or newer
- Google Gemini API key
- Composio API key
- Composio user id with Firecrawl access configured

## Setup

Clone the repo:

```bash
git clonehttps://github.com/VaddiMaithresh-16/SalaryInsight_Agent.git
cd MCP_SalaryInsights_Agent
```

Create and activate a virtual environment.

macOS or Linux:

```bash
python3 -m venv avenv
source avenv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv avenv
avenv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment Variables

Create `.env` from the example file:

```bash
cp .env.example .env
```

Update the values:

```env
GEMINI_API_KEY=your_gemini_api_key
COMPOSIO_API_KEY=your_composio_api_key
COMPOSIO_USER_ID=your_composio_user_id
```

### Where to Get Each Key

| Key | Get it from |
|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey — Google AI Studio, free tier available |
| `COMPOSIO_API_KEY` | https://app.composio.dev — Dashboard → Settings → API Keys |
| `COMPOSIO_USER_ID` | Composio dashboard → your account/user id, or generate one via Composio SDK on first auth |

Firecrawl access must also be connected inside your Composio account (Composio dashboard → Toolkits → Firecrawl → Connect) — this app loads Firecrawl tools through Composio, not a direct Firecrawl API key.

## Running

Run without a query — you'll be prompted to type one:

```bash
python main.py
```

Or pass the query directly from the command line:

```bash
python main.py --query "Python developer internship stipend and salary in India"
```

Another example:

```bash
python main.py --query "Compare Data Analyst salaries at MNCs vs startups in Bengaluru"
```

## How It Works

1. Loads environment variables from `.env`.
2. Initializes Gemini as the reasoning model.
3. Loads Firecrawl search/scrape tools through Composio MCP.
4. Creates a LangChain agent with LangGraph memory checkpointing (`thread_id="salary-agent"` — follow-up questions in the same run share context).
5. Sends your query to the agent, which decides whether to search, scrape, or answer directly.
6. Prints the final formatted salary breakdown.

## Known Behavior

- The system prompt instructs the agent to use `FIRECRAWL_SEARCH` and `FIRECRAWL_SCRAPE` before answering, but the model can still choose to answer from general knowledge instead of calling tools — Gemini isn't forced to invoke them. If output looks like a generic estimate rather than scraped data with source URLs, the agent skipped the tools that run. This is unchanged from the original notebook behavior.
- `langchain-mcp-adapters` is listed in requirements (carried over from the original notebook's install line) but isn't imported or used anywhere in `main.py` — Composio's own LangChain provider supplies the tools instead. Safe to remove if you want a leaner install; left in as-is since logic wasn't touched.
- Memory is in-process only (`InMemorySaver`) — conversation context resets every time you restart the script. No persistence across runs, unlike DocuChat's Chroma store.

## Troubleshooting

### Missing Environment Variable

If you see `Missing GEMINI_API_KEY` or `Missing COMPOSIO_API_KEY`, check that `.env` exists and includes those keys. Note: `COMPOSIO_USER_ID` is loaded but not validated — if it's missing or wrong, you'll get a Composio-side error instead of a clean message.

### Dependency Error

Make sure the virtual environment (`avenv`) is active, then reinstall:

```bash
python -m pip install -r requirements.txt
```

### Empty or Generic Answers

If responses look like general knowledge instead of scraped data, confirm Firecrawl is connected in your Composio account and re-run with a more specific query (include skill name + location + year).

## Security

- Do not commit `.env`.
- Do not expose API keys in logs, screenshots, or public repositories.
- Rotate API keys if they are accidentally shared.

## License

This project is intended for educational, research, and learning purposes.