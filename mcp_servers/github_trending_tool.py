"""
MCP Tool Server: GitHub Trending (Free, no key required)

Provides current trending repositories and technology momentum data
by scraping GitHub's trending page API.

Useful for decisions about tech career moves, learning new skills,
or evaluating which technologies are gaining traction.
"""

import re
import aiohttp

from mcp_framework import MCPTool, MCPToolResult, registry


class GitHubTrendingTool(MCPTool):
    """Fetches GitHub trending repos for technology momentum analysis."""

    @property
    def name(self) -> str:
        return "github_trending"

    @property
    def description(self) -> str:
        return "GitHub trending repositories — technology momentum, popular projects, ecosystem activity"

    @property
    def categories(self) -> list[str]:
        return [
            "Industry & Sector Trends",
            "Job Market & Salary Data",
        ]

    @property
    def api_base_url(self) -> str:
        return "https://api.github.com"

    async def invoke(
        self,
        decision: str,
        context: str,
        session: aiohttp.ClientSession,
    ) -> list[MCPToolResult]:
        results = []
        languages = self._detect_languages(decision, context)

        # Search for trending/popular repos related to the decision
        queries = self._build_queries(decision, context, languages)

        for query in queries[:2]:
            repos = await self._search_repos(query, session)
            for repo in repos[:2]:
                results.append(self._format_result(repo, decision))

        return results

    async def _search_repos(self, query: str, session: aiohttp.ClientSession) -> list[dict]:
        """Search GitHub repositories via the public API (no auth needed for basic search)."""
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 3,
        }
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FutureSelfSimulator/1.0",
        }
        try:
            async with session.get(url, params=params, headers=headers,
                                   timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("items", [])
        except Exception:
            pass
        return []

    def _format_result(self, repo: dict, decision: str) -> MCPToolResult:
        """Format a GitHub repo into a research result."""
        name = repo.get("full_name", "unknown")
        description = repo.get("description", "No description") or "No description"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        language = repo.get("language", "Unknown")
        updated = repo.get("updated_at", "")[:10]

        stars_str = f"{stars:,}" if stars else "0"
        forks_str = f"{forks:,}" if forks else "0"

        snippet = (
            f"{description[:150]}. "
            f"Stars: {stars_str}, Forks: {forks_str}. "
            f"Language: {language}. Last updated: {updated}."
        )

        return MCPToolResult(
            tool_name=self.name,
            category="Industry & Sector Trends",
            title=f"Trending: {name}",
            snippet=snippet,
            source_url=repo.get("html_url", ""),
            confidence=0.65,
            raw_data={"stars": stars, "forks": forks, "language": language},
        )

    def _detect_languages(self, decision: str, context: str) -> list[str]:
        """Detect programming languages mentioned in the decision."""
        text = f"{decision} {context}".lower()
        lang_map = {
            "python": "python", "javascript": "javascript", "typescript": "typescript",
            "java": "java", "golang": "go", "go ": "go", "rust": "rust",
            "c++": "c++", "c#": "c#", "ruby": "ruby", "swift": "swift",
            "kotlin": "kotlin", "scala": "scala", "r ": "r",
        }
        found = []
        for trigger, lang in lang_map.items():
            if trigger in text and lang not in found:
                found.append(lang)
        return found

    def _build_queries(self, decision: str, context: str, languages: list[str]) -> list[str]:
        """Build GitHub search queries."""
        text = f"{decision} {context}".lower()
        queries = []

        # Technology-specific searches
        tech_keywords = {
            "machine learning": "machine learning",
            "data science": "data-science",
            "ai ": "artificial-intelligence",
            "deep learning": "deep-learning",
            "web development": "web-development",
            "mobile": "mobile-app",
            "devops": "devops",
            "cloud": "cloud-computing",
            "blockchain": "blockchain",
            "cybersecurity": "cybersecurity",
        }

        for trigger, topic in tech_keywords.items():
            if trigger in text:
                q = f"{topic} created:>2025-01-01"
                if languages:
                    q += f" language:{languages[0]}"
                queries.append(q)

        # Fallback: search by mentioned languages
        if not queries and languages:
            queries.append(f"language:{languages[0]} stars:>1000 created:>2025-01-01")

        # General tech career relevance
        if not queries:
            queries.append("career tools created:>2025-01-01 stars:>100")

        return queries


# Auto-register
registry.register(GitHubTrendingTool())
