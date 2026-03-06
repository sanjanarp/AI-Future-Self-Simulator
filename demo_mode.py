"""
Demo / mock LLM responses for running the Future Self Simulator
without Azure OpenAI credentials. Provides realistic pre-built
responses for each step of the agentic pipeline.
"""

import asyncio
import random
from dataclasses import dataclass, field

# Simulated delay range (seconds) to mimic LLM latency
_MIN_DELAY = 0.8
_MAX_DELAY = 2.0


async def _delay():
    await asyncio.sleep(random.uniform(_MIN_DELAY, _MAX_DELAY))


async def demo_generate_choices(decision: str, num_choices: int) -> list[dict]:
    """Generate plausible choices for any decision (demo mode)."""
    await _delay()

    # Build generic-but-useful choice templates that adapt to the decision text
    templates = [
        {
            "title": "Go for it fully",
            "description": (
                f"Commit wholeheartedly to the bold path implied by your decision: "
                f"\"{decision[:80]}…\". Go all-in with maximum effort, accept the risks, "
                f"and reorganize your life around making this work."
            ),
        },
        {
            "title": "Stay the course",
            "description": (
                "Keep your current trajectory. Double down on what you already have — "
                "optimize and improve your existing situation rather than making a major "
                "change. Focus on extracting more value from where you are."
            ),
        },
        {
            "title": "Hybrid / gradual transition",
            "description": (
                "Take a middle path: start moving toward the change incrementally while "
                "keeping your safety net. Test the waters part-time, build skills or "
                "savings on the side, and set a clear decision deadline 6-12 months out."
            ),
        },
        {
            "title": "Explore a different angle entirely",
            "description": (
                "Step back and question the framing. Maybe the real opportunity is something "
                "you haven't considered — a lateral move, a creative reframe, or a completely "
                "different path that addresses the underlying need driving this decision."
            ),
        },
        {
            "title": "Delay and invest in yourself",
            "description": (
                "Postpone the decision by 6-12 months and use that time strategically: "
                "build skills, save money, grow your network, or gather information. "
                "Make the same decision later from a position of greater strength."
            ),
        },
    ]
    return templates[:num_choices]


async def demo_analyze_pros_cons(choice_title: str) -> dict:
    """Generate pros/cons analysis for a choice (demo mode)."""
    await _delay()

    analyses = {
        "Go for it fully": {
            "pros": [
                "Maximum potential upside — if it works, the rewards are significant",
                "Personal growth from facing a real challenge head-on",
                "No regret from wondering 'what if' — you'll know you gave it your all",
                "Opportunity to build something meaningful and aligned with your values",
                "Potential to inspire others and open doors you can't currently see",
            ],
            "cons": [
                "Highest financial risk — may deplete savings or take on debt",
                "Stress and uncertainty could strain relationships and health",
                "Opportunity cost: you forgo the stability and benefits of your current path",
                "If it fails, rebuilding may take 1-3 years",
                "Social pressure and self-doubt can be intense during the transition",
            ],
            "risk_level": "High",
            "confidence_note": "This analysis assumes you have some runway (savings, support network). Actual risk depends heavily on your financial buffer and personal resilience.",
        },
        "Stay the course": {
            "pros": [
                "Financial stability and predictable income continue",
                "Lower stress — familiar environment and established routines",
                "Continued growth within your current role or field",
                "Preserves relationships and community ties",
                "More time to plan if you decide to change later",
            ],
            "cons": [
                "Risk of stagnation and growing dissatisfaction over time",
                "The opportunity window for change may narrow as years pass",
                "May lead to 'golden handcuffs' — comfort that prevents growth",
                "Doesn't address the underlying restlessness driving this decision",
                "Could result in long-term regret about the path not taken",
            ],
            "risk_level": "Low",
            "confidence_note": "Staying put is the most predictable option, but 'low risk' doesn't mean 'no cost.' The emotional toll of unfulfilled ambition is real but hard to quantify.",
        },
        "Hybrid / gradual transition": {
            "pros": [
                "Reduces risk by maintaining income while exploring the new path",
                "Provides real data about whether the change is right for you",
                "Builds skills and confidence before committing fully",
                "Keeps options open — you can accelerate or pull back",
                "Less disruptive to family and financial obligations",
            ],
            "cons": [
                "Divided attention means slower progress on both fronts",
                "Can be exhausting — essentially working two jobs",
                "May never fully commit, leading to a prolonged state of limbo",
                "Others who go all-in may outpace you in the new direction",
                "Risk of burnout from trying to do everything at once",
            ],
            "risk_level": "Medium",
            "confidence_note": "The hybrid approach works best for people with strong time-management skills and supportive personal circumstances. It requires honest self-assessment about capacity.",
        },
        "Explore a different angle entirely": {
            "pros": [
                "May uncover a superior option you hadn't considered",
                "Forces deeper self-reflection about what you actually want",
                "Creative reframing can lead to innovative solutions",
                "Avoids the false binary of 'change vs. stay'",
                "Could reveal that the real issue is something else entirely",
            ],
            "cons": [
                "Analysis paralysis — too many options can be paralyzing",
                "Delays action while you explore, and time is a finite resource",
                "Others may perceive you as indecisive or unfocused",
                "No guarantee the 'different angle' is actually better",
                "Can become an avoidance strategy disguised as exploration",
            ],
            "risk_level": "Medium",
            "confidence_note": "This is most valuable when you feel trapped in a binary choice. However, set a time limit for exploration to avoid perpetual deliberation.",
        },
        "Delay and invest in yourself": {
            "pros": [
                "More preparation increases probability of success when you do act",
                "Financial buffer provides greater security and confidence",
                "Additional skills and experience make you more competitive",
                "Reduces the urgency-driven mistakes that derail major changes",
                "Allows you to stress-test your motivation — is this desire persistent?",
            ],
            "cons": [
                "Momentum and excitement may fade with delay",
                "Market conditions or personal circumstances could change unfavorably",
                "Can become a form of procrastination if not structured",
                "Age-sensitive opportunities may expire (some fields favor youth)",
                "Continued dissatisfaction during the waiting period",
            ],
            "risk_level": "Low",
            "confidence_note": "Delaying strategically is underrated, but only works if you use the time intentionally. Without a concrete plan, 'delay' easily becomes 'never.'",
        },
    }

    return analyses.get(choice_title, {
        "pros": [
            "Opens new possibilities and learning opportunities",
            "Aligns with your stated goals and values",
            "Potential for meaningful personal growth",
            "Could improve long-term satisfaction and fulfillment",
            "Demonstrates courage and adaptability",
        ],
        "cons": [
            "Involves uncertainty and potential setbacks",
            "Requires time and energy investment",
            "May involve trade-offs with current stability",
            "Outcome depends on factors outside your control",
            "Adjustment period could be stressful",
        ],
        "risk_level": "Medium",
        "confidence_note": "This analysis is based on general patterns. Your specific circumstances will significantly influence actual outcomes.",
    })


async def demo_simulate_timeline(choice_title: str, time_horizons: list[str]) -> list[dict]:
    """Generate timeline projections for a choice (demo mode)."""
    await _delay()

    scenarios = {
        "Go for it fully": [
            {
                "scenario": "You've made the leap. The first few months are a whirlwind of excitement mixed with anxiety. You're working harder than ever, learning rapidly, and some days you feel electric. Other days, doubt creeps in. Your savings buffer is shrinking but still manageable.",
                "emotional_state": "Oscillating between exhilaration and nervousness. High energy but sleep quality has dipped. You feel more alive than you have in years.",
                "key_factors": ["Initial traction or early wins", "Strength of support network", "Financial runway remaining"],
            },
            {
                "scenario": "The initial chaos has settled into a rhythm. You're seeing real results — maybe not as fast as you hoped, but the trajectory is positive. You've built new skills and relationships. Some friends from your old life have drifted, but new ones have appeared.",
                "emotional_state": "Cautiously optimistic. The constant anxiety has faded, replaced by a steady determination. You're proud of how far you've come.",
                "key_factors": ["Revenue/income trajectory", "Work-life balance sustainability", "Market conditions in your new field"],
            },
            {
                "scenario": "You've established yourself in the new path. The early risks have largely paid off — your income may or may not match your old salary, but your fulfillment is markedly higher. You've become a different person: more resilient, more self-aware, more intentional.",
                "emotional_state": "Deep satisfaction mixed with occasional nostalgia for the road not taken. You feel a sense of earned confidence.",
                "key_factors": ["Long-term market viability", "Personal relationship health", "Continued passion vs. routine"],
            },
            {
                "scenario": "Looking back, this decision defined a decade of your life. Whether the material outcomes exceeded expectations or not, you've built a life that feels authentically yours. The skills and confidence gained are transferable to whatever comes next.",
                "emotional_state": "Gratitude and perspective. You understand that the 'right' choice was less about the outcome and more about who you became in the process.",
                "key_factors": ["Compounding returns on early investments", "Health and relationship longevity", "Alignment with evolving values"],
            },
        ],
        "Stay the course": [
            {
                "scenario": "Life continues its familiar rhythm. You've doubled down on your current role, perhaps taking on new responsibilities or projects. The restlessness that prompted this decision-making process still surfaces occasionally, but you've found ways to channel it.",
                "emotional_state": "Stable but occasionally wistful. Comfort is nice, but you sometimes wonder about the path not taken.",
                "key_factors": ["Career advancement opportunities", "Finding new sources of meaning within current path", "Managing recurring restlessness"],
            },
            {
                "scenario": "You've progressed in your current path — promotion, raise, or expanded responsibilities. Your financial position is strong. But the question that started this has evolved: it's less urgent but hasn't fully gone away.",
                "emotional_state": "Contentment with undercurrents of 'is this really it?' You've learned to appreciate stability but the creative itch persists.",
                "key_factors": ["Salary growth and financial health", "Finding fulfillment outside of primary career", "Industry stability"],
            },
            {
                "scenario": "You're well-established and financially secure. You may have found alternative outlets for your ambitions — side projects, mentorship, hobbies. Or you may feel that the window for change has narrowed significantly.",
                "emotional_state": "A complex mix of security and quiet reflection. You've built a good life, though it may not match the boldest version of what you once imagined.",
                "key_factors": ["Long-term career trajectory", "Personal fulfillment and identity", "Regret management"],
            },
            {
                "scenario": "A decade of compound stability has produced significant material results. Whether that translates to life satisfaction depends heavily on the relationships, hobbies, and meaning-making you've cultivated alongside your career.",
                "emotional_state": "Reflective. The decision you once agonized over now seems smaller — life's richness came from dimensions you didn't fully anticipate.",
                "key_factors": ["Retirement/financial independence progress", "Depth of personal relationships", "Health and vitality"],
            },
        ],
    }

    default_scenarios = [
        {
            "scenario": "You're in the early stages of this path. Things are moving, adjustments are being made, and the learning curve is steep but manageable. Early signals are cautiously positive.",
            "emotional_state": "Engaged and slightly nervous. The novelty keeps you motivated.",
            "key_factors": ["Early results and feedback", "Adaptation speed", "Support system strength"],
        },
        {
            "scenario": "You've found your footing. The initial turbulence has settled, and you're building momentum. Some aspects are better than expected; others require more patience.",
            "emotional_state": "Growing confidence with realistic expectations. You feel capable.",
            "key_factors": ["Sustained effort and consistency", "External market/environment", "Personal energy management"],
        },
        {
            "scenario": "This path is now well-established in your life. You've developed expertise and relationships that reinforce this direction. The choice feels more natural now.",
            "emotional_state": "Settled and purposeful, with occasional reflection on alternatives.",
            "key_factors": ["Long-term viability of this direction", "Evolving personal values", "Financial trajectory"],
        },
        {
            "scenario": "A decade on, this choice has shaped who you've become. The compound effects — both positive and challenging — are clear. You have wisdom that only comes from living through the consequences.",
            "emotional_state": "Philosophical acceptance and earned wisdom. You understand yourself better than ever.",
            "key_factors": ["Cumulative life satisfaction", "Relationship and health outcomes", "Alignment with who you've become"],
        },
    ]

    base = scenarios.get(choice_title, default_scenarios)
    result = []
    for i, horizon in enumerate(time_horizons):
        idx = min(i, len(base) - 1)
        entry = {**base[idx], "time_horizon": horizon}
        result.append(entry)
    return result


async def demo_compare_tradeoffs(choices: list) -> list[dict]:
    """Generate trade-off comparisons (demo mode)."""
    await _delay()

    trade_offs = []
    for i in range(len(choices)):
        for j in range(i + 1, len(choices)):
            a = choices[i]
            b = choices[j]
            trade_offs.append({
                "choice_a": a.title,
                "choice_b": b.title,
                "what_you_gain": f"Choosing '{a.title}' gives you the advantages of its approach — the upside potential and alignment with that specific direction — at the cost of what '{b.title}' offers.",
                "what_you_lose": f"You forgo the benefits of '{b.title}' — its unique strengths, lower/different risk profile, and the particular future it enables.",
            })
            if len(trade_offs) >= 4:
                return trade_offs
    return trade_offs


async def demo_synthesize_insight(decision: str) -> dict:
    """Generate final synthesis (demo mode)."""
    await _delay()
    return {
        "key_insight": (
            f"The most important thing about this decision isn't which option is objectively 'best' — "
            f"it's understanding what you're optimizing for. Each path trades one kind of risk for another: "
            f"the risk of failure vs. the risk of regret, the risk of instability vs. the risk of stagnation. "
            f"The right choice depends on which risks you can live with and which would keep you up at night."
        ),
        "thinking_prompt": (
            "If you imagine yourself 10 years from now, having NOT made a change — and everything else "
            "in your life went reasonably well — would you feel at peace, or would there be a persistent "
            "ache of 'I never tried'?"
        ),
    }


@dataclass
class _DemoResearchResult:
    category: str
    title: str
    snippet: str
    source_url: str = ""
    tool_name: str = ""


@dataclass
class _DemoResearchReport:
    categories_searched: list = field(default_factory=list)
    tools_invoked: list = field(default_factory=list)
    results: list = field(default_factory=list)
    summary: str = ""

    def to_prompt_context(self) -> str:
        if not self.results:
            return "No real-time research data was gathered for this decision."
        sections = []
        by_category = {}
        for r in self.results:
            by_category.setdefault(r.category, []).append(r)
        for cat, items in by_category.items():
            lines = [f"### {cat}"]
            for item in items:
                source_tag = f" (via {item.tool_name})" if item.tool_name else ""
                lines.append(f"- **{item.title}**{source_tag}: {item.snippet}")
            sections.append("\n".join(lines))
        return "\n\n".join(sections)


async def demo_research(decision: str, context: str = "") -> _DemoResearchReport:
    """Simulate MCP tool server research with plausible data (demo mode)."""
    await asyncio.sleep(random.uniform(1.0, 2.5))

    text = f"{decision} {context}".lower()
    report = _DemoResearchReport()
    demo_tools_used = set()

    # Job-related
    if any(w in text for w in ["job", "career", "salary", "hire", "quit", "work", "role", "engineer", "manager"]):
        report.categories_searched.append("Job Market & Salary Data")
        demo_tools_used.update(["duckduckgo", "hackernews", "wikipedia"])
        report.results.extend([
            _DemoResearchResult(
                category="Job Market & Salary Data",
                title="Tech Job Market 2025-2026 Outlook",
                snippet="Software engineering roles remain in high demand with median salaries of $145K-$185K for mid-level positions. AI/ML specialists command 20-30% premiums. Remote work availability has stabilized at ~60% of tech roles.",
                source_url="https://www.bls.gov/ooh/computer-and-information-technology/",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Job Market & Salary Data",
                title="Hiring Trends & Layoff Data",
                snippet="After the 2023-2024 correction, tech hiring has rebounded with 12% YoY growth in job postings. Startups (Series A-C) are hiring aggressively, while large tech companies maintain cautious but steady hiring.",
                source_url="https://layoffs.fyi/",
                tool_name="hackernews",
            ),
            _DemoResearchResult(
                category="Job Market & Salary Data",
                title="Career Switching Statistics",
                snippet="Average career changers take 3-6 months to land their first role in a new field. 72% report higher job satisfaction after switching, though 45% initially take a 10-20% pay cut.",
                source_url="https://www.indeed.com/career-advice/",
                tool_name="wikipedia",
            ),
        ])

    # Cost of living / relocation
    if any(w in text for w in ["move", "relocat", "city", "country", "rent", "living"]):
        report.categories_searched.append("Cost of Living")
        demo_tools_used.update(["restcountries", "open_meteo", "duckduckgo"])
        report.results.extend([
            _DemoResearchResult(
                category="Cost of Living",
                title="Major City Cost Comparison 2025",
                snippet="San Francisco remains the most expensive US metro (cost index 187). Austin (112) and Denver (118) offer strong tech markets at lower costs. Remote-friendly cities like Raleigh (95) and Salt Lake City (97) are gaining popularity.",
                source_url="https://www.numbeo.com/cost-of-living/",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Cost of Living",
                title="Remote Work & Geographic Arbitrage",
                snippet="35% of remote workers have relocated to lower-cost areas since 2022. Average monthly savings: $800-$1,500. However, some companies have adjusted pay bands by location.",
                source_url="https://www.flexjobs.com/",
                tool_name="open_meteo",
            ),
        ])

    # Housing
    if any(w in text for w in ["house", "home", "buy", "rent", "mortgage", "property", "apartment"]):
        report.categories_searched.append("Housing & Real Estate")
        demo_tools_used.update(["duckduckgo"])
        report.results.extend([
            _DemoResearchResult(
                category="Housing & Real Estate",
                title="US Housing Market Forecast 2025-2026",
                snippet="Median home prices are $412K nationally, up 4.2% YoY. Mortgage rates hover around 6.2-6.5% for 30-year fixed. Inventory remains tight but improving in Sun Belt metros.",
                source_url="https://www.zillow.com/research/",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Housing & Real Estate",
                title="Rent vs. Buy Analysis",
                snippet="In 78% of US metro areas, monthly mortgage payments exceed rent for comparable properties. The break-even period for buying averages 5-7 years at current rates. Renting + investing the difference outperforms buying in high-cost markets.",
                source_url="https://www.nytimes.com/interactive/2024/upshot/buy-rent-calculator.html",
                tool_name="duckduckgo",
            ),
        ])

    # Startup / entrepreneurship
    if any(w in text for w in ["startup", "start", "company", "business", "found", "entrepren", "venture"]):
        report.categories_searched.append("Startup & Entrepreneurship")
        demo_tools_used.update(["hackernews", "wikipedia", "github_trending"])
        report.results.extend([
            _DemoResearchResult(
                category="Startup & Entrepreneurship",
                title="Startup Success Rates 2025",
                snippet="~10% of startups succeed long-term. First-time founders have a 18% success rate; repeat founders reach 30%. The median time to Series A is 22 months. Bootstrapped companies have higher survival rates (25%) but slower growth.",
                source_url="https://www.failory.com/blog/startup-failure-rate",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Startup & Entrepreneurship",
                title="Venture Funding Climate",
                snippet="Global VC funding reached $345B in 2025, recovering from the 2023 trough. AI-focused startups captured 38% of all funding. Pre-seed rounds average $500K-$2M; seed rounds $2M-$5M.",
                source_url="https://news.crunchbase.com/",
                tool_name="hackernews",
            ),
        ])

    # Education
    if any(w in text for w in ["degree", "school", "phd", "master", "mba", "university", "college", "educat", "bootcamp"]):
        report.categories_searched.append("Education & Training ROI")
        demo_tools_used.update(["wikipedia", "duckduckgo", "numbersapi"])
        report.results.extend([
            _DemoResearchResult(
                category="Education & Training ROI",
                title="Graduate Degree ROI Analysis",
                snippet="MBA graduates see average salary increases of 50-80% within 3 years. STEM master's degrees yield 15-25% premiums. PhDs in industry earn $120K-$180K median starting salary but spend 4-7 years in program.",
                source_url="https://www.usnews.com/education/",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Education & Training ROI",
                title="Average Tuition Costs 2025-2026",
                snippet="Top MBA programs: $150K-$230K total. CS Master's: $40K-$120K. Coding bootcamps: $12K-$20K. Online alternatives from accredited universities: $15K-$40K for master's degrees.",
                source_url="https://www.usnews.com/best-graduate-schools",
                tool_name="wikipedia",
            ),
        ])

    # Financial planning
    if any(w in text for w in ["invest", "retire", "saving", "financial", "money", "debt", "budget"]):
        report.categories_searched.append("Financial Planning")
        demo_tools_used.update(["numbersapi", "duckduckgo"])
        report.results.extend([
            _DemoResearchResult(
                category="Financial Planning",
                title="Economic Indicators 2025-2026",
                snippet="US inflation at 2.8%. Federal funds rate: 4.25-4.50%. S&P 500 trailing 12-month return: +18%. Average savings rate: 4.6%. 30-year Treasury yield: 4.3%.",
                source_url="https://www.federalreserve.gov/",
                tool_name="duckduckgo",
            ),
            _DemoResearchResult(
                category="Financial Planning",
                title="Savings Benchmarks by Age",
                snippet="Recommended emergency fund: 3-6 months expenses. By age 30: 1x salary saved. By 40: 3x salary. Median 401(k) balance age 30-39: $48K. Average net worth age 35: $250K (skewed by top earners; median ~$50K).",
                source_url="https://www.fidelity.com/",
                tool_name="numbersapi",
            ),
        ])

    # Fallback if nothing matched
    if not report.results:
        report.categories_searched.append("General Decision Research")
        demo_tools_used.add("wikipedia")
        report.results.append(_DemoResearchResult(
            category="General Decision Research",
            title="Decision-Making Research",
            snippet="Studies show that major life decisions benefit from a 2-week minimum deliberation period. People who systematically analyze trade-offs report 23% higher satisfaction with their choices. The #1 regret is inaction, not failed attempts.",
            source_url="https://hbr.org/",
            tool_name="wikipedia",
        ))

    report.tools_invoked = sorted(demo_tools_used)
    tool_names = ", ".join(report.tools_invoked)
    report.summary = (
        f"Queried {len(report.tools_invoked)} MCP tool servers ({tool_names}). "
        f"Searched {len(report.categories_searched)} categories: "
        f"{', '.join(report.categories_searched)}. "
        f"Found {len(report.results)} data points."
    )
    return report
