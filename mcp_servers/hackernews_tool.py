"""
MCP Tool Server: Hacker News API (Free, no key required)

Provides current tech community discussions and trends from
the Hacker News (Y Combinator) API.

API Docs: https://github.com/HackerNewsAPI/HackerNews-API
"""

import re
import aiohttp

from mcp_framework import MCPTool, MCPToolResult, registry


class HackerNewsTool(MCPTool):
    """Fetches relevant Hacker News discussions for tech/career/startup context."""

    @property
    def name(self) -> str:
        return "hackernews"

    @property
    def description(self) -> str:
        return "Hacker News (Y Combinator) — tech industry discussions, career debates, startup stories"

    @property
    def categories(self) -> list[str]:
        return [
            "Job Market & Salary Data",
            "Industry & Sector Trends",
            "Startup & Entrepreneurship",
            "Education & Training ROI",
        ]

    @property
    def api_base_url(self) -> str:
        return "https://hacker-news.firebaseio.com/v0"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []

        # Search HN via Algolia's free HN search API
        keywords = self._extract_keywords(decision, context)
        if not keywords:
            return results

        search_query = " ".join(keywords)
        stories = await self._search_stories(search_query, session)

        for story in stories[:4]:  # Top 4 relevant stories
            category = self._categorize_story(story, decision)
            title = story.get("title", "")
            # Build snippet from available data
            points = story.get("points", 0)
            comments = story.get("num_comments", 0)
            snippet = f"Discussion with {points} points and {comments} comments."
            if story.get("url"):
                snippet += f" Links to: {story['url'][:80]}"

            results.append(MCPToolResult(
                tool_name=self.name,
                category=category,
                title=f"HN: {title}",
                snippet=snippet,
                source_url=f"https://news.ycombinator.com/item?id={story.get('objectID', '')}",
                confidence=0.6,
                raw_data={"points": points, "comments": comments},
            ))

        return results

    async def _search_stories(self, query: str, session: aiohttp.ClientSession) -> list[dict]:
        """Search Hacker News stories via Algolia's HN Search API."""
        import time
        # Only get stories from the last 12 months
        one_year_ago = int(time.time()) - (365 * 24 * 60 * 60)
        url = "https://hn.algolia.com/api/v1/search"
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": 5,
            "numericFilters": f"points>20,created_at_i>{one_year_ago}",
        }
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("hits", [])
        except Exception:
            pass
        return []

    def _extract_keywords(self, decision: str, context: str) -> list[str]:
        """Extract relevant search keywords for HN."""
        text = f"{decision} {context}".lower()
        keywords = []

        keyword_map = {
            "software": "software engineer",
            "startup": "startup",
            "career": "career change",
            "salary": "salary",
            "remote": "remote work",
            "ai ": "AI",
            "machine learning": "machine learning",
            "data science": "data science",
            "mba": "MBA",
            "phd": "PhD",
            "freelanc": "freelancing",
            "found": "founder",
            "invest": "investing",
            "side project": "side project",
            "quit": "quit job",
            "burnout": "burnout",
            "management": "engineering manager",
        }

        for trigger, keyword in keyword_map.items():
            if trigger in text:
                keywords.append(keyword)

        return keywords[:3] if keywords else ["career decision"]

    def _categorize_story(self, story: dict, decision: str) -> str:
        """Categorize a HN story into a research category."""
        title = (story.get("title", "") + " " + story.get("url", "")).lower()
        if any(w in title for w in ["salary", "compensation", "hiring", "job", "career"]):
            return "Job Market & Salary Data"
        if any(w in title for w in ["startup", "founder", "vc", "funding", "yc"]):
            return "Startup & Entrepreneurship"
        if any(w in title for w in ["learn", "degree", "bootcamp", "school", "course"]):
            return "Education & Training ROI"
        return "Industry & Sector Trends"


# Auto-register
registry.register(HackerNewsTool())
