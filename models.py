"""
Pydantic models for the Future Self Simulator.
Defines the data structures used across the application.
"""

from pydantic import BaseModel, Field


class DecisionRequest(BaseModel):
    """User's decision input."""
    decision: str = Field(..., description="The major decision the user is facing")
    context: str = Field("", description="Additional context about the user's situation")
    time_horizons: list[str] = Field(
        default=["6 months", "2 years", "5 years", "10 years"],
        description="Time periods to simulate outcomes for",
    )
    num_choices: int = Field(default=3, ge=2, le=5, description="Number of choices to generate")


class ProsCons(BaseModel):
    """Pros and cons for a single choice."""
    pros: list[str]
    cons: list[str]


class TimelineOutcome(BaseModel):
    """Projected outcome at a specific point in time."""
    time_horizon: str
    scenario: str
    emotional_state: str
    key_factors: list[str]


class Choice(BaseModel):
    """A single decision choice with full analysis."""
    title: str
    description: str
    pros_cons: ProsCons
    timeline_outcomes: list[TimelineOutcome]
    risk_level: str  # Low, Medium, High
    confidence_note: str


class TradeOff(BaseModel):
    """A trade-off comparison between two choices."""
    choice_a: str
    choice_b: str
    what_you_gain: str
    what_you_lose: str


class ResearchFinding(BaseModel):
    """A single piece of real-time research data."""
    category: str
    title: str
    snippet: str
    source_url: str = ""
    tool_name: str = ""


class SimulationResult(BaseModel):
    """Complete simulation output."""
    original_decision: str
    research_findings: list[ResearchFinding] = []
    research_summary: str = ""
    tools_invoked: list[str] = []
    choices: list[Choice]
    trade_offs: list[TradeOff]
    key_insight: str
    thinking_prompt: str


class AgentStep(BaseModel):
    """Represents a single step in the agent's reasoning process."""
    step_name: str
    description: str
    status: str = "pending"  # pending, running, completed, failed
    result: str = ""
