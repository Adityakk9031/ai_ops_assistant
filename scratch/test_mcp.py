"""Scratch script to test MCP server and langchain-mcp-adapters tool loading."""

import sys
import asyncio
import logging
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

load_dotenv()
logging.basicConfig(level=logging.INFO)


async def test_mcp():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"]
    )
    
    print("Connecting to MCP server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session initialized successfully!")
            
            tools = await load_mcp_tools(session)
            print(f"Loaded {len(tools)} tools from MCP server:")
            for t in tools:
                print(f"  - {t.name}: {t.description}")
                
            # Test invoking one tool
            weather_tool = next((t for t in tools if "weather" in t.name), None)
            if weather_tool:
                print("\nTesting weather_current tool call...")
                res = await weather_tool.ainvoke({"city": "London"})
                print(f"Result: {res}")


if __name__ == "__main__":
    asyncio.run(test_mcp())
