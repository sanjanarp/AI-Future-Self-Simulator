"""
Future Self Simulator — Main Application Entry Point

An agentic AI tool that helps users think through major decisions by
simulating how different choices could play out over time.

Uses Azure OpenAI Service (GPT) for multi-step reasoning through:
  1. Choice generation
  2. Pros & cons analysis
  3. Future timeline simulation
  4. Trade-off comparison
  5. Insight synthesis

Run with:
    python app.py
"""

import json
import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse

from config import settings
from models import DecisionRequest
from agent import run_simulation


app = FastAPI(
    title="Future Self Simulator",
    description="AI-powered decision analysis agent using Azure OpenAI",
    version="1.0.0",
)

# Serve static files (frontend)
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main UI."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
async def health_check():
    """Health check endpoint — also reports whether Azure OpenAI is configured."""
    return {
        "status": "ok",
        "azure_openai_configured": settings.is_configured,
    }


@app.post("/api/simulate")
async def simulate_decision(request: DecisionRequest):
    """
    Run the full agentic simulation pipeline.

    Streams Server-Sent Events (SSE) with step updates and the final result.
    When Azure OpenAI is not configured, runs in demo mode with simulated responses.
    """
    if not request.decision.strip():
        raise HTTPException(status_code=400, detail="Decision text is required.")

    async def event_stream():
        async for event in run_simulation(request):
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("  Future Self Simulator")
    print("  AI-Powered Decision Analysis Agent")
    print("=" * 60)

    if not settings.is_configured:
        print("\n  * Running in DEMO MODE (no AI credentials)")
        print("    The app will use simulated AI responses.")
        print("    To use real AI, add Azure OpenAI credentials to .env\n")
    elif settings.use_azure:
        print(f"\n  OK Azure OpenAI configured")
        print(f"    Endpoint:   {settings.AZURE_OPENAI_ENDPOINT}")
        print(f"    Deployment: {settings.AZURE_OPENAI_DEPLOYMENT_NAME}\n")
    else:
        print(f"\n  OK OpenAI configured")
        print(f"    Model: {settings.OPENAI_MODEL}\n")

    print("  Starting server at http://localhost:8000")
    print("=" * 60 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
