import os
from dotenv import load_dotenv
from pathlib import Path
from agents import Agent, Runner, trace, Tool
from agents.mcp import MCPServerStdio
from datetime import datetime
import asyncio
from prompts import step1_prompts, step2_prompts, step3_prompts

model = "gpt-4o-mini"
async def get_researcher(mcp_servers, instructions) -> Agent:
    """Creates a research agent with connected MCP servers."""
    researcher = Agent(
        name="Researcher",
        instructions=instructions,
        model=model,
        mcp_servers=mcp_servers,
    )
    return researcher

async def get_researcher_tool(mcp_servers, instructions) -> Tool:
    """Converts the researcher agent into a usable tool."""
    researcher = await get_researcher(mcp_servers, instructions)
    return researcher.as_tool(
            tool_name="Researcher",
            tool_description="This tool researches online for news and opportunities, \
                either based on your specific request to look into a certain stock, \
                or generally for notable financial news and opportunities. \
                Provide clear research objectives for best results."
        )
    
def save_to_markdown(content: str, filename: str | None = None) -> None:
    """Saves the content to a markdown file."""
    output_dir = Path("Database")
    output_dir.mkdir(exist_ok=True)
    
    if filename is None:
        filename = f"Research_Results_{today_date}.md"
    
    # Create full filepath
    filepath = output_dir / filename
    
    # Save content
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Results saved to {filepath}")