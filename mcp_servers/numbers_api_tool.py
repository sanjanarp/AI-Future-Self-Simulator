"""
MCP Tool Server: Numbers API (Free, no key required)

Provides interesting facts about numbers — useful for adding engaging
context around ages, years, financial figures, and statistics in decisions.

API Docs: http://numbersapi.com/
"""

import re
import aiohttp

from mcp_framework import MCPTool, MCPToolResult, registry


class NumbersAPITool(MCPTool):
    """Fetches interesting number/date facts for contextual enrichment."""

    @property
    def name(self) -> str:
        return "numbersapi"

    @property
    def description(self) -> str:
        return "Numbers API — interesting facts about ages, years, and financial milestones"

    @property
    def categories(self) -> list[str]:
        return [
            "Financial Planning",
            "Education & Training ROI",
        ]

    @property
    def api_base_url(self) -> str:
        return "http://numbersapi.com"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        numbers = self._extract_numbers(decision, context)

        for number, context_type in numbers[:2]:
            fact = await self._get_fact(number, context_type, session)
            if fact:
                results.append(MCPToolResult(
                    tool_name=self.name,
                    category="Financial Planning",
                    title=f"Interesting Fact: {number}",
                    snippet=fact,
                    source_url=f"http://numbersapi.com/{number}",
                    confidence=0.5,
                ))

        return results

    async def _get_fact(self, number: int, fact_type: str, session: aiohttp.ClientSession) -> str:
        """Fetch a fact about a number."""
        # fact_type: "trivia", "math", "date", "year"
        url = f"http://numbersapi.com/{number}/{fact_type}"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status == 200:
                    return await resp.text()
        except Exception:
            pass
        return ""

    def _extract_numbers(self, decision: str, context: str) -> list[tuple[int, str]]:
        """Extract meaningful numbers from the decision text."""
        text = f"{decision} {context}"
        numbers = []

        # Age mentions → trivia facts
        age_match = re.search(r"\b(\d{2})\s*(?:years?\s*old|yo|y\.o\.)\b", text, re.IGNORECASE)
        if not age_match:
            age_match = re.search(r"\bI'?m\s+(\d{2})\b", text, re.IGNORECASE)
        if age_match:
            numbers.append((int(age_match.group(1)), "trivia"))

        # Year mentions → year facts
        year_matches = re.finditer(r"\b(20[2-3]\d)\b", text)
        for m in year_matches:
            numbers.append((int(m.group(1)), "year"))

        # Large financial numbers → math facts
        money_match = re.search(r"\$\s*([\d,]+)k?\b", text, re.IGNORECASE)
        if money_match:
            val = money_match.group(1).replace(",", "")
            try:
                num = int(val)
                if num < 1000:
                    num *= 1000  # Assume "k"
                numbers.append((num, "math"))
            except ValueError:
                pass

        return numbers


# Auto-register
registry.register(NumbersAPITool())
