"""
Agentic Reasoning Engine for the Future Self Simulator.

This module orchestrates a multi-step agentic pipeline where each step
builds on the output of previous steps. The agent reasons through a
decision in 5 stages:

  1. Generate Choices — identify distinct paths the user could take
  2. Analyze Pros & Cons — deep analysis of each choice
  3. Simulate Timelines — project outcomes at multiple future horizons
  4. Compare Trade-offs — pairwise trade-off analysis between choices
  5. Synthesize Insight — distill a key insight and reflective question

Each step calls the LLM with a focused prompt and structured output format,
making this an agentic workflow rather than a single monolithic prompt.
"""

import json
import asyncio
import re
import time
from typing import AsyncGenerator

from config import settings
from llm_client import chat_completion
from prompts import (
    SYSTEM_PROMPT,
    STEP1_GENERATE_CHOICES,
    STEP2_ANALYZE_PROS_CONS,
    STEP3_SIMULATE_TIMELINE,
    STEP4_COMPARE_TRADEOFFS,
    STEP5_SYNTHESIZE_INSIGHT,
)
from models import (
    DecisionRequest,
    Choice,
    ProsCons,
    TimelineOutcome,
    TradeOff,
    SimulationResult,
    ResearchFinding,
    AgentStep,
)
from demo_mode import (
    demo_generate_choices,
    demo_analyze_pros_cons,
    demo_simulate_timeline,
    demo_compare_tradeoffs,
    demo_synthesize_insight,
    demo_research,
)
from research_tools import conduct_research

# When True, uses pre-built demo responses instead of calling Azure OpenAI
USE_DEMO_MODE = not settings.is_configured


def _parse_json_response(text: str) -> dict:
    """Extract and parse JSON from an LLM response that may contain markdown fences."""
    text = text.strip()
    # Try to extract JSON from markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    # If the assistant prefixed a short text before the JSON (e.g., "OK\n{...}"),
    # find the first JSON object/array start and parse from there. Be tolerant
    # of stray backslashes by sanitizing invalid escapes before a final attempt.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        idx_obj = min([i for i in [text.find('{'), text.find('[')] if i >= 0], default=-1)
        candidate = text if idx_obj == -1 else text[idx_obj:]
        # Sanitization strategy:
        # 1) Remove stray backslashes that precede characters which are NOT
        #    valid JSON escape sequences (e.g., \$ or \%). These produce
        #    Invalid \escape errors when calling json.loads.
        # 2) Handle a few common cases explicitly (e.g., \$ -> $).
        try:
            def _sanitize_backslashes(s: str) -> str:
                allowed_simple = set('"\\/bfnrt')
                out = []
                i = 0
                L = len(s)
                while i < L:
                    ch = s[i]
                    if ch == '\\' and i + 1 < L:
                        nxt = s[i + 1]
                        if nxt in allowed_simple:
                            out.append('\\')
                            out.append(nxt)
                            i += 2
                            continue
                        # handle unicode escape \uXXXX where XXXX are hex digits
                        if nxt == 'u' and i + 5 < L:
                            hex_seq = s[i + 2 : i + 6]
                            if all(c in '0123456789abcdefABCDEF' for c in hex_seq):
                                out.append('\\')
                                out.append('u')
                                out.extend(hex_seq)
                                i += 6
                                continue
                        # otherwise drop the stray backslash and continue
                        i += 1
                        continue
                    else:
                        out.append(ch)
                        i += 1
                return ''.join(out)

            sanitized = _sanitize_backslashes(candidate)
            # Fix common model-escaped dollar signs
            sanitized = sanitized.replace('\\$', '$')
            return json.loads(sanitized)
        except Exception:
            pass
        # As a last resort, try un-escaping common double-escaped sequences
        # (e.g., model returned backslashes that were escaped in transit) and
        # then attempt progressive substring parsing. This helps when the
        # assistant double-escapes characters like \\$ or \\uXXXX.
        try:
            unescaped = candidate.encode('utf-8').decode('unicode_escape')
            return json.loads(unescaped)
        except Exception:
            pass

        # As a further fallback, try progressively shorter slices ending at potential
        # closing braces/brackets. This can recover when the assistant appended
        # extra text after a valid JSON object/array.
        closing_positions = [i for i, ch in enumerate(candidate) if ch in ("}", "]")]
        for end in closing_positions:
            snippet = candidate[: end + 1]
            try:
                sn_sanitized = (
                    (lambda x: x.replace('\\$', '$'))(_sanitize_backslashes(snippet))
                )
                return json.loads(sn_sanitized)
            except Exception:
                continue
        raise


def _call_llm(user_prompt: str, temperature: float = 0.7) -> dict:
    """Call the LLM with the system prompt and a user prompt, return parsed JSON."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    # Add a short retry loop to handle transient empty responses from the LLM/data-plane.
    response_text = ""
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        response_text = chat_completion(messages, temperature=temperature)
        if response_text and response_text.strip():
            break
        if attempt < max_attempts:
            time.sleep(0.8 * attempt)
    # Log raw response to stdout so it appears in container logs for debugging
    try:
        print("LLM_RAW_RESPONSE_START")
        print(response_text)
        print("LLM_RAW_RESPONSE_END")
    except Exception:
        pass

    try:
        if not response_text or not response_text.strip():
            raise Exception("Empty LLM response")
        return _parse_json_response(response_text)
    except Exception as exc:
        # Surface the raw LLM response in errors for easier debugging
        raise Exception(f"LLM parse error: {exc}; raw_response_snippet={response_text[:1000]}")


async def _call_llm_async(user_prompt: str, temperature: float = 0.7) -> dict:
    """Async wrapper around the synchronous LLM call."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _call_llm, user_prompt, temperature)


# ─── Step 1: Generate Choices ─────────────────────────────────────────────────

async def step_generate_choices(request: DecisionRequest, research_context: str = "") -> list[dict]:
    """Generate distinct decision choices based on the user's input."""
    if USE_DEMO_MODE:
        return await demo_generate_choices(request.decision, request.num_choices)
    prompt = STEP1_GENERATE_CHOICES.format(
        decision=request.decision,
        context=request.context or "No additional context provided.",
        num_choices=request.num_choices,
        research_context=research_context,
    )
    result = await _call_llm_async(prompt, temperature=0.8)
    return result["choices"]


# ─── Step 2: Analyze Pros & Cons ──────────────────────────────────────────────

async def step_analyze_pros_cons(
    request: DecisionRequest, choice: dict, research_context: str = ""
) -> dict:
    """Analyze pros, cons, risk, and confidence for a single choice."""
    if USE_DEMO_MODE:
        return await demo_analyze_pros_cons(choice["title"])
    prompt = STEP2_ANALYZE_PROS_CONS.format(
        decision=request.decision,
        context=request.context or "No additional context provided.",
        choice_title=choice["title"],
        choice_description=choice["description"],
        research_context=research_context,
    )
    return await _call_llm_async(prompt, temperature=0.6)


# ─── Step 3: Simulate Timelines ───────────────────────────────────────────────

async def step_simulate_timeline(
    request: DecisionRequest, choice: dict, research_context: str = ""
) -> list[dict]:
    """Simulate future outcomes at each time horizon for a single choice."""
    if USE_DEMO_MODE:
        return await demo_simulate_timeline(choice["title"], request.time_horizons)
    horizons_list = "\n".join(f"- {h}" for h in request.time_horizons)
    prompt = STEP3_SIMULATE_TIMELINE.format(
        decision=request.decision,
        context=request.context or "No additional context provided.",
        choice_title=choice["title"],
        choice_description=choice["description"],
        time_horizons_list=horizons_list,
        research_context=research_context,
    )
    result = await _call_llm_async(prompt, temperature=0.7)
    return result["timeline_outcomes"]


# ─── Step 4: Compare Trade-offs ───────────────────────────────────────────────

async def step_compare_tradeoffs(
    request: DecisionRequest, choices: list[Choice], research_context: str = ""
) -> list[dict]:
    """Generate pairwise trade-off comparisons between all choices."""
    if USE_DEMO_MODE:
        return await demo_compare_tradeoffs(choices)
    choices_summary = "\n".join(
        f"- **{c.title}**: {c.description}" for c in choices
    )
    n = len(choices)
    num_tradeoffs = min(n * (n - 1) // 2, 6)  # cap at 6
    prompt = STEP4_COMPARE_TRADEOFFS.format(
        decision=request.decision,
        context=request.context or "No additional context provided.",
        choices_summary=choices_summary,
        num_tradeoffs=num_tradeoffs,
        research_context=research_context,
    )
    result = await _call_llm_async(prompt, temperature=0.6)
    return result["trade_offs"]


# ─── Step 5: Synthesize Insight ───────────────────────────────────────────────

async def step_synthesize_insight(
    request: DecisionRequest,
    choices: list[Choice],
    trade_offs: list[TradeOff],
    research_context: str = "",
) -> dict:
    """Produce a final key insight and reflective thinking prompt."""
    if USE_DEMO_MODE:
        return await demo_synthesize_insight(request.decision)
    full_analysis = ""
    for c in choices:
        full_analysis += f"\n#### {c.title}\n{c.description}\n"
        full_analysis += f"**Risk Level:** {c.risk_level}\n"
        full_analysis += "**Pros:** " + ", ".join(c.pros_cons.pros) + "\n"
        full_analysis += "**Cons:** " + ", ".join(c.pros_cons.cons) + "\n"
        for t in c.timeline_outcomes:
            full_analysis += f"- *{t.time_horizon}*: {t.scenario}\n"

    trade_offs_summary = "\n".join(
        f"- {t.choice_a} vs {t.choice_b}: Gain — {t.what_you_gain} | Lose — {t.what_you_lose}"
        for t in trade_offs
    )

    prompt = STEP5_SYNTHESIZE_INSIGHT.format(
        decision=request.decision,
        context=request.context or "No additional context provided.",
        full_analysis=full_analysis,
        trade_offs_summary=trade_offs_summary,
        research_context=research_context,
    )
    return await _call_llm_async(prompt, temperature=0.7)


# ─── Full Agentic Pipeline ────────────────────────────────────────────────────

def _build_agent_steps() -> list[AgentStep]:
    """Define the agent's step plan."""
    return [
        AgentStep(step_name="research", description="Gathering real-time data"),
        AgentStep(step_name="generate_choices", description="Identifying possible choices"),
        AgentStep(step_name="analyze_pros_cons", description="Analyzing pros & cons for each choice"),
        AgentStep(step_name="simulate_timelines", description="Simulating future timelines"),
        AgentStep(step_name="compare_tradeoffs", description="Comparing trade-offs between choices"),
        AgentStep(step_name="synthesize_insight", description="Synthesizing final insight"),
    ]


async def run_simulation(request: DecisionRequest) -> AsyncGenerator[dict, None]:
    """
    Execute the full agentic simulation pipeline.

    Yields progress updates as dicts with structure:
        {"type": "step_update", "step": <step_name>, "status": <status>, "message": <msg>}
        {"type": "result", "data": <SimulationResult dict>}
    """
    steps = _build_agent_steps()

    # ── Step 0: Real-Time Research (MCP Tool Invocation) ──
    yield {"type": "step_update", "step": "research", "status": "running",
           "message": "Invoking MCP tool servers for real-time data..."}
    research_context = ""
    research_findings = []
    research_summary = ""
    tools_invoked = []
    try:
        if USE_DEMO_MODE:
            report = await demo_research(request.decision, request.context)
        else:
            report = await conduct_research(request.decision, request.context)

        research_context = report.to_prompt_context()
        research_summary = report.summary
        tools_invoked = getattr(report, 'tools_invoked', [])
        for r in report.results:
            research_findings.append(ResearchFinding(
                category=r.category,
                title=r.title,
                snippet=r.snippet,
                source_url=r.source_url,
                tool_name=getattr(r, 'tool_name', ''),
            ))

        if research_context and research_context != "No real-time research data was gathered for this decision.":
            research_context = f"## Real-Time Research Data\\n\\nThe following current data was gathered from the web to inform this analysis:\\n\\n{research_context}"
        else:
            research_context = ""

        cat_count = len(report.categories_searched)
        res_count = len(report.results)
        tool_count = len(tools_invoked)
        yield {"type": "step_update", "step": "research", "status": "completed",
               "message": f"Queried {tool_count} MCP tools — found {res_count} data points across {cat_count} categories"}
    except Exception as e:
        yield {"type": "step_update", "step": "research", "status": "completed",
               "message": f"Research skipped (non-critical): {str(e)[:80]}"}
        research_context = ""

    # ── Step 1: Generate Choices ──
    yield {"type": "step_update", "step": "generate_choices", "status": "running",
           "message": "Brainstorming possible paths you could take..."}
    try:
        raw_choices = await step_generate_choices(request, research_context)
        yield {"type": "step_update", "step": "generate_choices", "status": "completed",
               "message": f"Identified {len(raw_choices)} distinct choices"}
    except Exception as e:
        yield {"type": "step_update", "step": "generate_choices", "status": "failed",
               "message": f"Error generating choices: {str(e)}"}
        return

    # ── Step 2: Analyze Pros & Cons (parallel per choice) ──
    yield {"type": "step_update", "step": "analyze_pros_cons", "status": "running",
           "message": "Deep-diving into pros, cons, and risks for each choice..."}
    try:
        pros_cons_tasks = [step_analyze_pros_cons(request, c, research_context) for c in raw_choices]
        pros_cons_results = await asyncio.gather(*pros_cons_tasks)
        yield {"type": "step_update", "step": "analyze_pros_cons", "status": "completed",
               "message": "Completed pros/cons analysis for all choices"}
    except Exception as e:
        yield {"type": "step_update", "step": "analyze_pros_cons", "status": "failed",
               "message": f"Error analyzing pros/cons: {str(e)}"}
        return

    # ── Step 3: Simulate Timelines (parallel per choice) ──
    yield {"type": "step_update", "step": "simulate_timelines", "status": "running",
           "message": f"Projecting your future across {len(request.time_horizons)} time horizons..."}
    try:
        timeline_tasks = [step_simulate_timeline(request, c, research_context) for c in raw_choices]
        timeline_results = await asyncio.gather(*timeline_tasks)
        yield {"type": "step_update", "step": "simulate_timelines", "status": "completed",
               "message": "Future timelines generated for all choices"}
    except Exception as e:
        yield {"type": "step_update", "step": "simulate_timelines", "status": "failed",
               "message": f"Error simulating timelines: {str(e)}"}
        return

    # ── Assemble Choice objects ──
    choices: list[Choice] = []
    for i, raw in enumerate(raw_choices):
        pc = pros_cons_results[i]
        tl = timeline_results[i]
        choice = Choice(
            title=raw["title"],
            description=raw["description"],
            pros_cons=ProsCons(pros=pc["pros"], cons=pc["cons"]),
            timeline_outcomes=[
                TimelineOutcome(
                    time_horizon=t["time_horizon"],
                    scenario=t["scenario"],
                    emotional_state=t["emotional_state"],
                    key_factors=t["key_factors"],
                )
                for t in tl
            ],
            risk_level=pc.get("risk_level", "Medium"),
            confidence_note=pc.get("confidence_note", ""),
        )
        choices.append(choice)

    # ── Step 4: Compare Trade-offs ──
    yield {"type": "step_update", "step": "compare_tradeoffs", "status": "running",
           "message": "Mapping the trade-offs between your options..."}
    try:
        raw_tradeoffs = await step_compare_tradeoffs(request, choices, research_context)
        trade_offs = [
            TradeOff(
                choice_a=t["choice_a"],
                choice_b=t["choice_b"],
                what_you_gain=t["what_you_gain"],
                what_you_lose=t["what_you_lose"],
            )
            for t in raw_tradeoffs
        ]
        yield {"type": "step_update", "step": "compare_tradeoffs", "status": "completed",
               "message": f"Identified {len(trade_offs)} key trade-offs"}
    except Exception as e:
        yield {"type": "step_update", "step": "compare_tradeoffs", "status": "failed",
               "message": f"Error comparing trade-offs: {str(e)}"}
        return

    # ── Step 5: Synthesize Insight ──
    yield {"type": "step_update", "step": "synthesize_insight", "status": "running",
           "message": "Distilling everything into a key insight..."}
    try:
        synthesis = await step_synthesize_insight(request, choices, trade_offs, research_context)
        yield {"type": "step_update", "step": "synthesize_insight", "status": "completed",
               "message": "Final synthesis complete"}
    except Exception as e:
        yield {"type": "step_update", "step": "synthesize_insight", "status": "failed",
               "message": f"Error synthesizing insight: {str(e)}"}
        return

    # ── Yield final result ──
    result = SimulationResult(
        original_decision=request.decision,
        research_findings=research_findings,
        research_summary=research_summary,
        tools_invoked=tools_invoked,
        choices=choices,
        trade_offs=trade_offs,
        key_insight=synthesis.get("key_insight", ""),
        thinking_prompt=synthesis.get("thinking_prompt", ""),
    )
    yield {"type": "result", "data": result.model_dump()}
