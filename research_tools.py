"""
Real-Time Research Tools for the Future Self Simulator.

This module bridges the agentic pipeline and the MCP tool framework.
It detects relevant research categories from the user's decision,
discovers matching MCP tool servers, invokes them in parallel, and
returns a unified research report.

MCP Tool Servers Available:
  - Wikipedia API         — factual background & definitions
  - DuckDuckGo Search     — broad web search for current articles
  - Hacker News (Algolia) — tech community discussions & trends
  - REST Countries API    — country data for relocation decisions
  - GitHub Trending       — technology momentum & ecosystem activity
  - Numbers API           — contextual facts about ages/years/numbers
  - Open-Meteo            — weather & climate data for cities
"""

import re
from dataclasses import dataclass, field

# Import MCP framework and auto-register all tool servers
from mcp_framework import MCPResearchReport, registry
import mcp_servers  # noqa: F401  — triggers auto-registration of all tools


# ─── Data Structures ─────────────────────────────────────────────────────────

@dataclass
class ResearchResult:
    """A single piece of research with source attribution."""
    category: str
    title: str
    snippet: str
    source_url: str = ""
    tool_name: str = ""


@dataclass
class ResearchReport:
    """Aggregated research findings for a decision."""
    categories_searched: list[str] = field(default_factory=list)
    tools_invoked: list[str] = field(default_factory=list)
    results: list[ResearchResult] = field(default_factory=list)
    summary: str = ""

    def to_prompt_context(self) -> str:
        """Format research findings as citation-ready context for LLM prompts."""
        if not self.results:
            return "No real-time research data was gathered for this decision."

        sections = []
        by_category: dict[str, list[ResearchResult]] = {}
        for r in self.results:
            by_category.setdefault(r.category, []).append(r)

        for cat, items in by_category.items():
            lines = [f"### {cat}"]
            for item in items:
                if item.source_url:
                    lines.append(
                        f"- **{item.title}**: {item.snippet} "
                        f"— cite as [{item.title}]({item.source_url})"
                    )
                else:
                    tool_tag = f" (via {item.tool_name})" if item.tool_name else ""
                    lines.append(f"- **{item.title}**{tool_tag}: {item.snippet}")
            sections.append("\n".join(lines))

        return "\n\n".join(sections)


# ─── Topic Detection ─────────────────────────────────────────────────────────

TOPIC_PATTERNS: dict[str, list[str]] = {
    "Job Market & Salary Data": [
        r"\bjob\b", r"\bcareer\b", r"\bsalar(?:y|ies)\b", r"\bhir(?:e|ing)\b",
        r"\bquit\b", r"\bleav(?:e|ing)\b.{0,20}\bjob\b", r"\brole\b",
        r"\bemploy(?:ment|er|ee)\b", r"\bprofession\b", r"\boccupation\b",
        r"\bwork(?:ing|place)?\b", r"\bswitch(?:ing)?\b.{0,15}\b(?:career|field|role)\b",
        r"\bremote\b", r"\bfreelance\b", r"\bcontract(?:or)?\b",
        r"\bpromo(?:tion|te)\b", r"\braise\b", r"\bmanager\b",
    ],
    "Cost of Living": [
        r"\bmov(?:e|ing)\b", r"\brelocat(?:e|ing|ion)\b", r"\bcity\b", r"\bcountry\b",
        r"\bcost of living\b", r"\bexpens(?:e|ive|es)\b.{0,20}\b(?:city|area|place)\b",
        r"\bafford\b", r"\brent\b.{0,10}\b(?:city|area|apartment)\b",
        r"\btransfer\b.{0,15}\b(?:office|location|city)\b",
    ],
    "Housing & Real Estate": [
        r"\bbuy(?:ing)?\b.{0,15}\b(?:house|home|apartment|condo|property)\b",
        r"\brent(?:ing)?\b.{0,10}\b(?:vs|or|versus)\b", r"\bmortgage\b",
        r"\breal estate\b", r"\bhous(?:e|ing)\b.{0,10}\b(?:market|price)\b",
        r"\bproperty\b", r"\bdownpayment\b", r"\bdown payment\b",
    ],
    "Industry & Sector Trends": [
        r"\bstartup\b", r"\bindustry\b", r"\bsector\b", r"\btech\b",
        r"\bAI\b", r"\bmarket\b.{0,10}\b(?:trend|grow|decline)\b",
        r"\bautomation\b", r"\bdisrupt(?:ion|ive)\b",
        r"\bemerging\b", r"\bfuture of\b", r"\bgrowing field\b",
    ],
    "Education & Training ROI": [
        r"\bgrad(?:uate)?\b.{0,10}\b(?:school|degree|program)\b",
        r"\bPhD\b", r"\bmaster(?:'s)?\b", r"\bMBA\b",
        r"\bbootcamp\b", r"\bcertificat(?:e|ion)\b", r"\bdegree\b",
        r"\btuition\b", r"\bstudent\b.{0,10}\b(?:loan|debt)\b",
        r"\buniversity\b", r"\bcollege\b", r"\beducat(?:ion|e)\b",
        r"\bschool\b", r"\blearn(?:ing)?\b.{0,10}\bnew\b",
    ],
    "Startup & Entrepreneurship": [
        r"\bstart(?:ing)?\b.{0,15}\b(?:company|business|venture)\b",
        r"\bfound(?:er|ing)?\b", r"\bentrepreneur\b", r"\bco-found\b",
        r"\bventure\b", r"\bfunding\b", r"\binvest(?:or|ment)\b",
        r"\bself-employ\b", r"\bown business\b", r"\bside hustle\b",
    ],
    "Immigration & Visa": [
        r"\bvisa\b", r"\bimmigrat(?:e|ion)\b", r"\babroad\b",
        r"\bwork permit\b", r"\bgreen card\b", r"\bcitizenship\b",
        r"\bexpatriate\b", r"\bexpat\b", r"\bforeign\b.{0,10}\bcountry\b",
        r"\binternational\b.{0,10}\b(?:move|offer|job|opportunity)\b",
    ],
    "Financial Planning": [
        r"\binvest(?:ing|ment)?\b", r"\bretir(?:e|ement)\b", r"\bsav(?:e|ings)\b",
        r"\bfinancial\b", r"\bdebt\b", r"\bbudget\b",
        r"\binterest rate\b", r"\binflation\b", r"\bstock\b",
        r"\b401k\b", r"\bpension\b", r"\bwealth\b",
    ],
}


def detect_research_topics(decision: str, context: str = "") -> list[str]:
    """Analyze decision text to determine relevant research categories."""
    full_text = f"{decision} {context}".lower()
    matched = []

    for category, patterns in TOPIC_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                matched.append(category)
                break

    if not matched:
        matched = ["Industry & Sector Trends"]

    return matched[:5]  # Cap at 5 categories


# ─── MCP-Powered Research ────────────────────────────────────────────────────

async def conduct_research(
    decision: str,
    context: str = "",
) -> ResearchReport:
    """
    Conduct real-time research using the MCP tool framework.

    1. Detects which research categories are relevant
    2. Discovers MCP tool servers that can serve those categories
    3. Invokes all matching tools in parallel
    4. Aggregates results into a unified ResearchReport
    """
    # Step 1: Detect relevant categories
    categories = detect_research_topics(decision, context)

    # Step 2: Discover matching MCP tools
    tools = registry.find_tools_for_categories(categories)

    if not tools:
        return ResearchReport(
            categories_searched=categories,
            summary="No MCP tools available for the detected categories.",
        )

    # Step 3: Invoke all tools in parallel via the MCP registry
    mcp_report: MCPResearchReport = await registry.invoke_tools(
        tools=tools,
        decision=decision,
        context=context,
    )

    # Step 4: Convert MCPResearchReport → ResearchReport (legacy interface)
    report = ResearchReport(
        categories_searched=mcp_report.categories_searched,
        tools_invoked=mcp_report.tools_invoked,
        summary=mcp_report.summary,
        results=[
            ResearchResult(
                category=r.category,
                title=r.title,
                snippet=r.snippet,
                source_url=r.source_url,
                tool_name=r.tool_name,
            )
            for r in mcp_report.results
        ],
    )

    return report
