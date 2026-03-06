"""
Prompt templates for each stage of the agentic reasoning pipeline.
Each prompt is designed to elicit structured, high-quality reasoning from the LLM.
"""

SYSTEM_PROMPT = """You are the Future Self Simulator — an advanced AI decision-analysis agent.
Your purpose is to help humans think through major life and career decisions by simulating
how different choices could play out over time. You reason carefully, consider nuance,
and always present balanced perspectives. You never tell people what to do — instead,
you illuminate the landscape of possibilities so they can decide with clarity.

Guidelines:
- Be specific and vivid in your scenarios — avoid vague generalities.
- Acknowledge uncertainty honestly; real life is not perfectly predictable.
- Consider emotional, financial, relational, and personal-growth dimensions.
- Use a warm but analytical tone — like a wise mentor who also thinks in systems.
- Always ground your analysis in the user's specific context when provided.
- IMPORTANT: When real-time research data is provided, you MUST weave it directly into
  your analysis. Reference specific numbers, statistics, and trends from the data.
  Whenever you use a fact from the research, cite its source as a markdown link:
  [Source Name](url) — for example: "median salary is $165K [BLS](https://bls.gov/ooh)".
  Do NOT list sources separately — embed them naturally within your sentences.
  Every pro, con, scenario, and insight should be grounded in real data when available.
"""

STEP1_GENERATE_CHOICES = """## Task: Generate Decision Choices

The user is facing this decision:
**"{decision}"**

Additional context from the user:
{context}

{research_context}

Generate exactly {num_choices} distinct, realistic choices the user could make.
For each choice, provide a clear title and a 2-3 sentence description.
If research data is provided above, reference relevant facts and cite sources as markdown links [Name](url) within your descriptions.

Respond in this exact JSON format:
```json
{{
  "choices": [
    {{
      "title": "Choice title",
      "description": "2-3 sentence description of this choice"
    }}
  ]
}}
```

Make sure the choices are meaningfully different from each other — not just slight variations.
Include at least one bold/unconventional option alongside more conventional ones.
"""

STEP2_ANALYZE_PROS_CONS = """## Task: Deep Pros/Cons Analysis

The user is deciding: **"{decision}"**
User context: {context}

{research_context}

Analyze this specific choice:
**{choice_title}**: {choice_description}

Provide a thorough pros and cons analysis. Consider these dimensions:
- Financial impact
- Career/professional growth
- Personal fulfillment and happiness
- Relationships and social life
- Health and well-being
- Skills and learning
- Risk and security
- Long-term optionality (does this open or close future doors?)

Respond in this exact JSON format:
```json
{{
  "pros": ["pro 1", "pro 2", "pro 3", "pro 4", "pro 5"],
  "cons": ["con 1", "con 2", "con 3", "con 4", "con 5"],
  "risk_level": "Low|Medium|High",
  "confidence_note": "A brief note about how confident this analysis is and what unknowns remain"
}}
```

Provide 4-6 pros and 4-6 cons. Be specific, not generic.
When research data is available, reference concrete numbers, statistics, and trends
within each pro and con. Cite sources inline as markdown links: [Source](url).
For example: "Austin's cost of living index is 112 vs NYC's 187 [Numbeo](https://numbeo.com/)"
"""

STEP3_SIMULATE_TIMELINE = """## Task: Future Timeline Simulation

The user is deciding: **"{decision}"**
User context: {context}

{research_context}

Simulate the future for this choice:
**{choice_title}**: {choice_description}

Project what the user's life could realistically look like at these time horizons:
{time_horizons_list}

For EACH time horizon, describe:
1. A vivid, specific scenario of what life looks like
2. The likely emotional state of the user
3. 2-3 key factors that would determine whether this scenario plays out

Respond in this exact JSON format:
```json
{{
  "timeline_outcomes": [
    {{
      "time_horizon": "6 months",
      "scenario": "Vivid 3-4 sentence description of life at this point...",
      "emotional_state": "Description of likely emotional state...",
      "key_factors": ["factor 1", "factor 2", "factor 3"]
    }}
  ]
}}
```

Be realistic — include both positive and challenging aspects.
Avoid pure fantasy. Ground your projections in how similar decisions typically unfold.
When research data is available, weave specific facts and statistics into your scenarios.
Cite sources inline as markdown links: [Source](url).
"""

STEP4_COMPARE_TRADEOFFS = """## Task: Trade-Off Analysis

The user is deciding: **"{decision}"**
User context: {context}

{research_context}

Here are the choices being considered:
{choices_summary}

For each meaningful pair of choices, identify the core trade-off:
what does the user gain by picking one over the other, and what do they give up?

Respond in this exact JSON format:
```json
{{
  "trade_offs": [
    {{
      "choice_a": "Title of choice A",
      "choice_b": "Title of choice B",
      "what_you_gain": "What you gain by choosing A over B (1-2 sentences)",
      "what_you_lose": "What you give up by choosing A over B (1-2 sentences)"
    }}
  ]
}}
```

Focus on the most important and non-obvious trade-offs. Aim for {num_tradeoffs} comparisons.
Reference specific research data where relevant and cite sources as markdown links: [Source](url).
"""

STEP5_SYNTHESIZE_INSIGHT = """## Task: Final Synthesis

The user is deciding: **"{decision}"**
User context: {context}

{research_context}

Here is the complete analysis so far:

### Choices Analyzed:
{full_analysis}

### Trade-Offs Identified:
{trade_offs_summary}

Now synthesize everything into:

1. **Key Insight**: The single most important thing the user should understand about
   this decision — something that cuts through the complexity and reveals the core tension.
   (2-3 sentences)

2. **Thinking Prompt**: A powerful question the user should sit with before deciding.
   This should be the kind of question that, once you really answer it honestly,
   makes the right choice clearer. (1-2 sentences)

Respond in this exact JSON format:
```json
{{
  "key_insight": "Your synthesized insight here...",
  "thinking_prompt": "Your question for the user here..."
}}
```

Be profound but practical. Avoid clichés.
Ground your insight in the research data when available. Cite key sources as markdown links: [Source](url).
"""
