"""
MCP Tool Server: DuckDuckGo Web Search (Free, no key required)

Provides web search results for general research.
Uses the DuckDuckGo HTML search interface and extracts real destination URLs.

API Docs: https://duckduckgo.com/api
"""

import re
import aiohttp
from urllib.parse import quote_plus, urlparse, parse_qs, unquote

from mcp_framework import MCPTool, MCPToolResult, registry


class DuckDuckGoTool(MCPTool):
    """Web search via DuckDuckGo for broad research coverage."""

    @property
    def name(self) -> str:
        return "duckduckgo"

    @property
    def description(self) -> str:
        return "DuckDuckGo web search — broad coverage of current news, articles, and data"

    @property
    def categories(self) -> list[str]:
        return [
            "Job Market & Salary Data",
            "Cost of Living",
            "Housing & Real Estate",
            "Industry & Sector Trends",
            "Education & Training ROI",
            "Startup & Entrepreneurship",
            "Immigration & Visa",
            "Financial Planning",
        ]

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        queries = self._build_queries(decision, context)

        for query, category in queries[:3]:  # Max 3 searches
            search_results = await self._search(query, session)
            for sr in search_results[:2]:  # Top 2 per query
                results.append(MCPToolResult(
                    tool_name=self.name,
                    category=category,
                    title=sr["title"],
                    snippet=sr["snippet"],
                    source_url=sr.get("url", ""),
                    confidence=0.7,
                ))

        return results

    async def _search(self, query: str, session: aiohttp.ClientSession) -> list[dict]:
        """Search DuckDuckGo HTML and extract results."""
        url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    return self._parse_results(html)
        except Exception:
            pass
        return []

    def _parse_results(self, html: str) -> list[dict]:
        """Extract search results from DuckDuckGo HTML."""
        results = []
        link_pattern = re.compile(
            r'<a[^>]+class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL
        )
        snippet_pattern = re.compile(
            r'<a[^>]+class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL
        )
        links = link_pattern.findall(html)
        snippets = snippet_pattern.findall(html)

        for i in range(min(len(links), len(snippets), 5)):
            title = re.sub(r'<[^>]+>', '', links[i][1]).strip()
            snippet = re.sub(r'<[^>]+>', '', snippets[i]).strip()
            raw_url = links[i][0]
            url = self._resolve_url(raw_url)
            if title and snippet and url:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": url,
                })
        return results

    @staticmethod
    def _resolve_url(raw_url: str) -> str:
        """Extract the real destination URL from a DuckDuckGo redirect link."""
        # DDG wraps URLs as //duckduckgo.com/l/?uddg=<encoded_real_url>&rut=...
        if "duckduckgo.com/l/" in raw_url or "uddg=" in raw_url:
            # Ensure scheme so urlparse works
            if raw_url.startswith("//"):
                raw_url = "https:" + raw_url
            parsed = parse_qs(urlparse(raw_url).query)
            uddg = parsed.get("uddg", [""])[0]
            if uddg:
                return unquote(uddg)
        # Already a direct URL
        if raw_url.startswith("http"):
            return raw_url
        if raw_url.startswith("//"):
            return "https:" + raw_url
        return ""

    def _build_queries(self, decision: str, context: str) -> list[tuple[str, str]]:
        """Build category-tagged search queries."""
        text = f"{decision} {context}".lower()
        queries = []

        # Always do a general decision-relevant search
        short_decision = decision[:80]
        queries.append((f"{short_decision} latest data 2025 2026", "Industry & Sector Trends"))

        # Category-specific queries
        if any(w in text for w in ["job", "career", "salary", "hire", "quit", "work"]):
            role = self._extract(text, ["software engineer", "data scientist", "product manager",
                                        "designer", "analyst", "developer", "manager", "engineer"])
            queries.append((f"{role} job market salary 2025 2026", "Job Market & Salary Data"))

        if any(w in text for w in ["move", "relocat", "city", "rent", "cost"]):
            queries.append((f"cost of living comparison cities 2025 2026", "Cost of Living"))

        if any(w in text for w in ["house", "buy", "mortgage", "property"]):
            queries.append((f"housing market forecast 2025 2026", "Housing & Real Estate"))

        if any(w in text for w in ["degree", "school", "phd", "master", "mba", "bootcamp"]):
            queries.append((f"graduate degree ROI worth it 2025 2026", "Education & Training ROI"))

        if any(w in text for w in ["startup", "business", "found", "venture"]):
            queries.append((f"startup success rate funding trends 2025 2026", "Startup & Entrepreneurship"))

        return queries

    @staticmethod
    def _extract(text: str, options: list[str]) -> str:
        for opt in options:
            if opt in text:
                return opt
        return "professional"


# Auto-register
registry.register(DuckDuckGoTool())
