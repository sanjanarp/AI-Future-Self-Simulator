"""
MCP Tool Server: Wikipedia API (Free, no key required)

Provides factual background information, definitions, and context
for decision-related topics using the MediaWiki API.

API Docs: https://www.mediawiki.org/wiki/API:Main_page
"""

import re
import aiohttp
from urllib.parse import quote_plus

from mcp_framework import MCPTool, MCPToolResult, registry


class WikipediaTool(MCPTool):
    """Fetches relevant Wikipedia summaries for decision context."""

    @property
    def name(self) -> str:
        return "wikipedia"

    @property
    def description(self) -> str:
        return "Wikipedia encyclopedia — factual background, definitions, and historical context"

    @property
    def categories(self) -> list[str]:
        return [
            "Job Market & Salary Data",
            "Education & Training ROI",
            "Industry & Sector Trends",
            "Immigration & Visa",
            "Startup & Entrepreneurship",
            "Financial Planning",
        ]

    @property
    def api_base_url(self) -> str:
        return "https://en.wikipedia.org/api/rest_v1"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        search_terms = self._extract_search_terms(decision, context)

        for term in search_terms[:3]:  # Max 3 lookups
            summary = await self._get_summary(term, session)
            if summary:
                results.append(MCPToolResult(
                    tool_name=self.name,
                    category=self._categorize(term),
                    title=summary["title"],
                    snippet=summary["extract"][:300] + ("..." if len(summary.get("extract", "")) > 300 else ""),
                    source_url=summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
                    confidence=0.9,
                    raw_data={"pageid": summary.get("pageid")},
                ))

        return results

    async def _get_summary(self, term: str, session: aiohttp.ClientSession) -> dict | None:
        """Fetch a Wikipedia article summary via the REST API."""
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(term)}"
        headers = {"User-Agent": "FutureSelfSimulator/1.0"}
        try:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("type") == "standard" and data.get("extract"):
                        return data
        except Exception:
            pass
        return None

    def _extract_search_terms(self, decision: str, context: str) -> list[str]:
        """Extract meaningful Wikipedia search terms from the decision."""
        text = f"{decision} {context}"
        terms = []

        # Look for specific domains/fields
        domain_map = {
            r"\bdata science\b": "Data science",
            r"\bmachine learning\b": "Machine learning",
            r"\bartificial intelligence\b|\bAI\b": "Artificial intelligence",
            r"\bsoftware engineer": "Software engineering",
            r"\bproduct manag": "Product management",
            r"\bMBA\b": "Master of Business Administration",
            r"\bPhD\b": "Doctor of Philosophy",
            r"\bventure capital\b": "Venture capital",
            r"\bfranchise\b": "Franchising",
            r"\bfreelance\b": "Freelancing",
            r"\bremote work\b": "Remote work",
            r"\bentrepreneur": "Entrepreneurship",
            r"\breal estate\b": "Real estate investing",
            r"\bstock market\b": "Stock market",
            r"\bcryptocurren": "Cryptocurrency",
            r"\bblockchain\b": "Blockchain",
            r"\bconsulting\b": "Management consulting",
            r"\binvestment bank": "Investment banking",
            r"\bmedic(?:al|ine)\b": "Medicine",
            r"\bnursing\b": "Nursing",
            r"\bteaching\b": "Teaching",
            r"\blaw school\b": "Law school in the United States",
        }

        for pattern, wiki_term in domain_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                terms.append(wiki_term)

        # Look for mentioned cities/countries
        locations = {
            "austin": "Austin, Texas", "san francisco": "San Francisco",
            "new york": "New York City", "seattle": "Seattle",
            "london": "London", "berlin": "Berlin", "toronto": "Toronto",
            "singapore": "Singapore", "tokyo": "Tokyo", "dubai": "Dubai",
            "bangalore": "Bangalore", "amsterdam": "Amsterdam",
        }
        text_lower = text.lower()
        for key, wiki_term in locations.items():
            if key in text_lower:
                terms.append(wiki_term)

        # If nothing matched, try the core noun phrases
        if not terms:
            # Fall back to the most important 2-3 words
            terms.append("Career change")

        return terms[:3]

    def _categorize(self, term: str) -> str:
        """Map a search term to a research category."""
        term_lower = term.lower()
        if any(w in term_lower for w in ["engineer", "science", "managing", "consult", "work", "career"]):
            return "Job Market & Salary Data"
        if any(w in term_lower for w in ["mba", "phd", "school", "doctor of"]):
            return "Education & Training ROI"
        if any(w in term_lower for w in ["entrepren", "venture", "franchise", "freelanc"]):
            return "Startup & Entrepreneurship"
        if any(w in term_lower for w in ["invest", "stock", "crypto", "bank"]):
            return "Financial Planning"
        return "Industry & Sector Trends"


# Auto-register with global registry
registry.register(WikipediaTool())
