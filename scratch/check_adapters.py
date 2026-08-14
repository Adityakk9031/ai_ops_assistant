"""Inspect langchain_mcp_adapters exports."""

try:
    import langchain_mcp_adapters
    print("langchain_mcp_adapters module dir:", [x for x in dir(langchain_mcp_adapters) if not x.startswith('_')])
except Exception as e:
    print("Error importing langchain_mcp_adapters:", e)

try:
    from langchain_mcp_adapters.tools import load_mcp_tools
    print("Successfully imported load_mcp_tools from langchain_mcp_adapters.tools!")
except Exception as e:
    print("Error importing from langchain_mcp_adapters.tools:", e)

try:
    from langchain_mcp_adapters.client import MultiServerMcpClient
    print("Found MultiServerMcpClient in client!")
except Exception as e:
    print("Error importing MultiServerMcpClient:", e)
