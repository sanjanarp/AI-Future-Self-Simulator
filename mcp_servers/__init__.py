"""
MCP Tool Servers Package.

Each module in this package is an MCP tool server wrapping a free API.
All tools auto-register with the global MCPToolRegistry on import.
"""

from mcp_servers.wikipedia_tool import WikipediaTool
from mcp_servers.duckduckgo_tool import DuckDuckGoTool
from mcp_servers.hackernews_tool import HackerNewsTool
from mcp_servers.rest_countries_tool import RESTCountriesTool
from mcp_servers.github_trending_tool import GitHubTrendingTool
from mcp_servers.numbers_api_tool import NumbersAPITool
from mcp_servers.open_meteo_tool import OpenMeteoTool

__all__ = [
    "WikipediaTool",
    "DuckDuckGoTool",
    "HackerNewsTool",
    "RESTCountriesTool",
    "GitHubTrendingTool",
    "NumbersAPITool",
    "OpenMeteoTool",
]
