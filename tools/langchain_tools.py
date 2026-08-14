"""MCP Tool utilities for loading tools dynamically via Model Context Protocol."""

import sys
import logging
from typing import List, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

logger = logging.getLogger("tools.mcp_tools")

# StdioServerParameters pointing to mcp_server.py
server_params = StdioServerParameters(
    command=sys.executable,
    args=["mcp_server.py"]
)


async def get_mcp_tools() -> List[Any]:
    """
    Connect to mcp_server.py over stdio transport using MCP ClientSession 
    and load tools dynamically using langchain-mcp-adapters.
    """
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await load_mcp_tools(session)
                logger.info(f"Successfully loaded {len(tools)} tools dynamically from MCP server")
                return tools
    except Exception as e:
        logger.error(f"Failed to load MCP tools from server: {str(e)}")
        return []
