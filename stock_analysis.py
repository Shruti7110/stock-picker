#----------------------IMPORTS----------------------
import os
from dotenv import load_dotenv
from pathlib import Path
from agents import Agent, Runner, trace, Tool
from agents.mcp import MCPServerStdio
from datetime import datetime
import asyncio
from prompts import step1_prompts, step2_prompts, step3_prompts
from push_notifications import send_test_email
from research import get_researcher, save_to_markdown, get_researcher_tool
# from pydantic import BaseModel, Field

#---------------------SERVER SETUP--------------------------
load_dotenv(override=True)

today_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
model = "gpt-4o-mini"

researcher_params = [
    {"command": "uvx", "args": ["mcp-server-fetch"]},
    {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-brave-search"], "env": {"BRAVE_API_KEY": os.getenv("BRAVE_API_KEY")}},    
]

mcp_research_servers = [MCPServerStdio(params, client_session_timeout_seconds=30) for params in researcher_params]

fmp_params = {
    "command": "npx", 
    "args": ["-y", "@vipbat/fmp-mcp-server"],
    "env": {"FMP_API_KEY": os.getenv("FMP_API_KEY")}
}

fmp_research_servers = [MCPServerStdio(fmp_params, client_session_timeout_seconds=30)]

#-----------------------AGENT SETUP----------------------
    
async def main():
    try:
        #------------ STEP 0: CONNECT TO MCP SERVERS ------------
        for server in mcp_research_servers:
            await server.connect()
        for server in fmp_research_servers:
            await server.connect()
        print("✅  All MCP servers connected successfully.")
        
        #--------------STEP 1: FIND TOP 10 STOCKS-------------------
        step1_instructions, step1_request = step1_prompts(today_date)           
        step1_researcher = await get_researcher(mcp_research_servers, step1_instructions)
        with trace("Researcher"):
            step1_result = await Runner.run(step1_researcher, step1_request, max_turns=30)
        print(f"Step 1 completed - Shortlisted 10 tops")        
        step1_data = step1_result.final_output
        print(f"Step 1 data: {step1_data}")
        
        #--------------STEP 2: GET DETAILS OF SHORTLISTED STOCKS-------------------
        step2_instructions, step2_request = step2_prompts(today_date, step1_data)                
        step2_researcher = await get_researcher(fmp_research_servers, step2_instructions)
        with trace("Researcher"):
            step2_result = await Runner.run(step2_researcher, step2_request, max_turns=30)
        print(f"Step 2 completed - Fetched details of shortlisted stocks")
        step2_data = step2_result.final_output
        print(f"Step 2 data: {step2_data}")
        
        #-------------STEP 3: ANALYZE STOCKS AND FIND TOP 3-------------------
        step3_instructions, step3_request = step3_prompts(today_date, step2_data)
        step3_researcher = await get_researcher(mcp_research_servers, step3_instructions)
        with trace("Researcher"):
            step3_result = await Runner.run(step3_researcher, step3_request, max_turns=30)
        print(f"Step 3 completed - Analyzed stocks and found top 3")
        result = step3_result.final_output

        #------------STEP 4 : SAVE AND SEND RESULTS-------------------        
        save_to_markdown(result) # save the result is database folder        
        subject = f"Stock Market Predictions for {today_date}"
        send_test_email(subject, result.final_output) # send the same in email
    
    except Exception as e:
        print(f"⚠️ An error occurred: {e}")
    finally:        
        print("🛑 DONE 🛑")
        

asyncio.run(main())