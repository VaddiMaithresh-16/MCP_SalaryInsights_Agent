"""## Import Libraries"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from composio import Composio
from composio_langchain import LangchainProvider

import asyncio
import argparse
import warnings
warnings.filterwarnings("ignore")
import logging
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)
logging.getLogger("langchain_google_genai._function_utils").setLevel(logging.ERROR)

"""## Load API Keys"""

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY")
COMPOSIO_USER_ID = os.getenv("COMPOSIO_USER_ID")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

"""## Validation"""

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY")
if not COMPOSIO_API_KEY:
    raise ValueError("Missing COMPOSIO_API_KEY")

"""# Step 1: Initialize Model"""

model = init_chat_model(
    "google_genai:gemini-3.1-flash-lite",
    api_key=GEMINI_API_KEY
)

"""# Step 2: Define System Prompt"""

system_prompt = """
You are a Competitor Salary Scanner that helps students understand REAL compensation for a skill by scraping actual salary websites.

You have access to these tools:

- FIRECRAWL_SEARCH: Search the web for salary pages, compensation reports, and career guides.
- FIRECRAWL_SCRAPE: Scrape a specific URL to extract full salary data, compensation breakdowns, and company-wise pay details.

Your workflow:

1. Use FIRECRAWL_SEARCH to find salary pages for the skill (search for things like "[skill] salary India 2025 Glassdoor", "[skill] developer compensation AmbitionBox", "[skill] pay scale levels.fyi").
2. From the search results, pick the best 2-3 URLs from salary sites like Glassdoor, AmbitionBox, PayScale, or Levels.fyi.
3. Use FIRECRAWL_SCRAPE on those URLs to extract the full salary breakdown including experience levels, city-wise splits, and company comparisons.

Present your findings in this format:

SALARY BREAKDOWN BY EXPERIENCE

- Entry Level (0-2 years): salary range
- Mid Level (3-5 years): salary range
- Senior Level (6+ years): salary range

Also include internship stipend information, company-wise salary comparisons, and source URLs.
"""

"""# Step 3: Initialize Composio"""

composio = Composio(
    api_key=COMPOSIO_API_KEY,
    provider=LangchainProvider()
)

"""# Step 4: Load MCP Tools"""

mcp_tools = composio.tools.get(
    user_id=COMPOSIO_USER_ID,
    toolkits=[
        "FIRECRAWL"
    ]
)

checkpointer = InMemorySaver()
MemoryConfig = {
    "configurable": {
        "thread_id": "salary-agent"
    }
}

agent = create_agent(
    model=model,
    tools=mcp_tools,
    system_prompt=system_prompt,
    checkpointer=checkpointer,
)

"""# Step 4: Build Agent"""

async def salary_insights_agent(agent, user_query):

    response = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        }, config=MemoryConfig
    )

    return response

"""# Step 5: Run Agent"""


async def main():

    parser = argparse.ArgumentParser(description="AI Salary Insights Agent")
    parser.add_argument(
        "--query",
        default=None,
        help="Salary question to ask. If not given, you'll be prompted interactively."
    )
    args = parser.parse_args()

    query = args.query
    if not query:
        query = input("Enter your salary question: ").strip()

    if not query:
        print("No question entered. Exiting.")
        return

    result = await salary_insights_agent(agent, query)

    print(result["messages"][-1].content[0]["text"])


if __name__ == "__main__":
    asyncio.run(main())
