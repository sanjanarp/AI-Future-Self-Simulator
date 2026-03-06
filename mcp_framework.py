"""
MCP (Model Context Protocol) Tool Framework for the Future Self Simulator.

Implements an MCP-inspired architecture where each external data source is
a "tool server" with a standardized interface. The agent discovers available
tools, invokes relevant ones in parallel, and aggregates results.

Key concepts:
  - MCPTool: Base class for all tool servers (standard interface)
  - MCPToolRegistry: Discovers and manages available tools
  - MCPToolResult: Standardized result format from any tool
  - MCPResearchReport: Aggregated results from multiple tool invocations
"""

import asyncio
import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


# ─── MCP Data Structures ─────────────────────────────────────────────────────

@dataclass
class MCPToolResult:
    """Standardized result from any MCP tool invocation."""
    tool_name: str          # Which tool produced this result
    category: str           # Research category (e.g., "Job Market")
    title: str              # Brief title of the finding
    snippet: str            # Main data/content
    source_url: str = ""    # Attribution URL
    confidence: float = 0.8 # How confident in this data (0-1)
    raw_data: dict = field(default_factory=dict)  # Original API response


@dataclass
class MCPResearchReport:
    """Aggregated research from multiple MCP tool invocations."""
    tools_invoked: list[str] = field(default_factory=list)
    categories_searched: list[str] = field(default_factory=list)
    results: list[MCPToolResult] = field(default_factory=list)
    summary: str = ""
    errors: list[str] = field(default_factory=list)

    def to_prompt_context(self) -> str:
        """Format all findings as context for LLM prompts."""
        if not self.results:
            return "No real-time research data was gathered for this decision."

        sections = []
        by_category: dict[str, list[MCPToolResult]] = {}
        for r in self.results:
            by_category.setdefault(r.category, []).append(r)

        for cat, items in by_category.items():
            lines = [f"### {cat}"]
            for item in items:
                source_tag = f" (via {item.tool_name})"
                lines.append(f"- **{item.title}**{source_tag}: {item.snippet}")
                if item.source_url:
                    lines.append(f"  Source: {item.source_url}")
            sections.append("\n".join(lines))

        return "\n\n".join(sections)


# ─── MCP Tool Base Class ─────────────────────────────────────────────────────

class MCPTool(ABC):
    """
    Base class for MCP tool servers.

    Each tool server wraps a free API and exposes:
      - name: Unique identifier for the tool
      - description: What this tool provides
      - categories: Which research categories it can serve
      - is_available(): Health check
      - invoke(): Execute the tool and return results
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of this tool server."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this tool provides."""
        ...

    @property
    @abstractmethod
    def categories(self) -> list[str]:
        """List of research categories this tool can serve."""
        ...

    @property
    def api_base_url(self) -> str:
        """Base URL for this tool's API."""
        return ""

    async def is_available(self, session: aiohttp.ClientSession) -> bool:
        """Check if this tool's API is reachable."""
        if not self.api_base_url:
            return True
        try:
            async with session.head(
                self.api_base_url,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                return resp.status < 500
        except Exception:
            return False

    @abstractmethod
    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        """
        Invoke this tool and return results relevant to the decision.

        Args:
            decision: The user's decision text
            context: Additional context about the user's situation
            session: Shared aiohttp session for HTTP requests

        Returns:
            List of MCPToolResult objects
        """
        ...


# ─── MCP Tool Registry ──────────────────────────────────────────────────────

class MCPToolRegistry:
    """
    Discovers and manages MCP tool servers.

    Analogous to an MCP host that maintains connections to multiple
    tool servers and routes requests to the appropriate ones.
    """

    def __init__(self):
        self._tools: dict[str, MCPTool] = {}

    def register(self, tool: MCPTool) -> None:
        """Register a tool server with the registry."""
        self._tools[tool.name] = tool

    def discover(self) -> list[dict]:
        """
        Discover all registered tools and their capabilities.
        Returns tool manifests (name, description, categories).
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "categories": tool.categories,
            }
            for tool in self._tools.values()
        ]

    def find_tools_for_categories(self, categories: list[str]) -> list[MCPTool]:
        """Find all tools that can serve the given research categories."""
        matched: list[MCPTool] = []
        for tool in self._tools.values():
            if any(cat in tool.categories for cat in categories):
                matched.append(tool)
        return matched

    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a specific tool by name."""
        return self._tools.get(name)

    @property
    def tool_count(self) -> int:
        return len(self._tools)

    async def invoke_tools(
        self,
        tools: list[MCPTool],
        decision: str,
        context: str,
    ) -> MCPResearchReport:
        """
        Invoke multiple tools in parallel and aggregate results.

        This is the core MCP orchestration — fan out to multiple tool
        servers simultaneously and collect their responses.
        """
        report = MCPResearchReport()
        report.tools_invoked = [t.name for t in tools]

        async with aiohttp.ClientSession() as session:
            # Invoke all tools in parallel
            tasks = [
                self._safe_invoke(tool, decision, context, session)
                for tool in tools
            ]
            results = await asyncio.gather(*tasks)

            for tool, result_or_error in zip(tools, results):
                if isinstance(result_or_error, list):
                    for r in result_or_error:
                        report.results.append(r)
                        if r.category not in report.categories_searched:
                            report.categories_searched.append(r.category)
                elif isinstance(result_or_error, str):
                    report.errors.append(f"{tool.name}: {result_or_error}")

        # Build summary
        if report.results:
            tool_names = ", ".join(report.tools_invoked)
            report.summary = (
                f"Queried {len(report.tools_invoked)} MCP tool servers ({tool_names}). "
                f"Searched {len(report.categories_searched)} categories: "
                f"{', '.join(report.categories_searched)}. "
                f"Found {len(report.results)} data points."
            )
        else:
            report.summary = "MCP tools were invoked but no results were retrieved."

        return report

    async def _safe_invoke(
        self,
        tool: MCPTool,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult] | str:
        """Invoke a tool with error handling. Returns results or error string."""
        try:
            return await asyncio.wait_for(
                tool.invoke(decision, context, session),
                timeout=15.0,  # 15 second timeout per tool
            )
        except asyncio.TimeoutError:
            return f"Timed out after 15 seconds"
        except Exception as e:
            return f"Error: {str(e)[:100]}"


# ─── Global Registry ─────────────────────────────────────────────────────────

# The global registry instance — tool servers register themselves on import
registry = MCPToolRegistry()
