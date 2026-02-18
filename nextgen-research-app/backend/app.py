"""Next-gen Deep Research backend API.

This backend provides a beginner-friendly HTTP API on top of the existing
LangGraph-based deep research system. It wraps the compiled
`research_agent_full.agent` graph into simple endpoints.

Endpoints:
- POST /api/research  -> run a research job and return the final result (v1: synchronous)

Later we can extend this to async job IDs and polling if needed.
"""

from typing import Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chat_models import init_chat_model

from deep_research_from_scratch.research_agent_full import agent as full_agent
from deep_research_from_scratch.research_agent import researcher_agent
from deep_research_from_scratch.state_scope import AgentInputState

app = FastAPI(title="Next-Gen Deep Research API")

# Allow the static HTML frontend and localhost origins to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchMode(str):
    """User-friendly research modes.

    - quick:     lighter research (future: single-agent)
    - deep_web:  full pipeline over the web
    - deep_web_and_local: full pipeline using web + local docs if MCP configured
    """

    QUICK = "quick"
    DEEP_WEB = "deep_web"
    DEEP_WEB_AND_LOCAL = "deep_web_and_local"


class ResearchRequest(BaseModel):
    question: str
    mode: Literal["quick", "deep_web", "deep_web_and_local", "llm_only"] = "deep_web"
    template: Optional[str] = None
    provider: Optional[str] = None  # e.g. "google_genai", "openai", "anthropic"
    model: Optional[str] = None     # e.g. "gemini-2.5-pro", "gpt-4.1", etc.


class ResearchResponse(BaseModel):
    mode: str
    question: str
    final_report: str


@app.post("/api/research", response_model=ResearchResponse)
async def run_research(request: ResearchRequest) -> ResearchResponse:
    """Run a deep research job and return the final report.

    For v1 this is a synchronous call that blocks until the underlying
    LangGraph graph finishes. This keeps the API very simple for new users
    and for the frontend.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question must not be empty.")

    # Build initial state for the LangGraph agent.
    # AgentInputState expects a `messages` list; we seed it with a single
    # user message containing the question.
    initial_state = AgentInputState(messages=[{"role": "user", "content": request.question}])

    # Route based on selected mode.
    # quick              -> single research agent (faster, no supervisor)
    # deep_web           -> full multi-agent pipeline
    # deep_web_and_local -> full pipeline (local docs usage depends on MCP config)
    # llm_only           -> direct model call with chosen provider/model (no tools)
    try:
        if request.mode == "llm_only":
            # Direct LLM answer without the full research pipeline.
            provider = request.provider or "google_genai"
            model_name = request.model or "gemini-2.5-pro"
            llm = init_chat_model(model=model_name, model_provider=provider, temperature=0.0)
            response = await llm.ainvoke([{"role": "user", "content": request.question}])
            final_report = str(getattr(response, "content", response)) or "No report generated."

        elif request.mode == "quick":
            # Use the single researcher graph directly for a lighter, faster run.
            quick_state = await researcher_agent.ainvoke(
                {
                    "researcher_messages": [
                        {"type": "human", "content": request.question}
                    ],
                    "research_topic": request.question,
                }
            )
            final_report = quick_state.get("compressed_research", "") or "No report generated."
        else:
            result_state = await full_agent.ainvoke(initial_state)
            final_report = result_state.get("final_report", "") or "No report generated."

    except Exception as exc:  # pragma: no cover - simple error passthrough
        raise HTTPException(status_code=500, detail=f"Research failed: {exc}") from exc

    return ResearchResponse(
        mode=request.mode,
        question=request.question,
        final_report=final_report,
    )
