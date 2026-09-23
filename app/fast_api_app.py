# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI & A2A Server for GAIL Autonomous Pipeline Grid Agent.

Exposes:
  - Agent Card: GET /a2a/gail_grid_advisor/.well-known/agent-card.json
  - A2A JSON-RPC 0.3 / 1.0: POST /a2a/gail_grid_advisor
  - Direct Prompt: POST /api/v1/prompt
  - Health: GET /health
  - Demo Console UI: GET /
"""

import contextlib
import os
from pathlib import Path
from collections.abc import AsyncIterator

from a2a.server.tasks import InMemoryTaskStore
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import GailPipelineAgent
from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import attach_reasoning_engine_routes

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output_artifacts"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

agent = GailPipelineAgent()


class PromptPayload(BaseModel):
    prompt: str


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        from app.agent import app as adk_app
        from app.agent import root_agent
        from google.adk.runners import Runner

        if adk_app and root_agent:
            runner = Runner(
                app=adk_app,
                session_service=services.get_session_service(),
                artifact_service=services.get_artifact_service(),
                auto_create_session=True,
            )
            app.state.runner = runner
            app.state.agent_app_name = adk_app.name

            from app.integration.agent_card import build_agent_capabilities
            from app.integration.executor import A2uiNegotiatingExecutor

            await attach_a2a_routes(
                app,
                agent=root_agent,
                runner=runner,
                task_store=InMemoryTaskStore(),
                rpc_path=f"/a2a/{adk_app.name}",
                capabilities=build_agent_capabilities(),
                executor=A2uiNegotiatingExecutor(runner=runner),
            )
    except Exception as e:
        print(f"Warning: A2A route auto-attach skipped: {e}")

    yield


app = FastAPI(
    title="GAIL Autonomous Pipeline Grid, Predictive Analytics & Executive Advisory Agent",
    description="Gemini Enterprise End-to-End Agentic AI Microservice for GAIL (India) Limited",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
@app.get("/demo", response_class=HTMLResponse)
def get_demo_console():
    """Serves the interactive 5-Act Demonstration Console UI."""
    template_path = TEMPLATES_DIR / "demo_console.html"
    if not template_path.exists():
        return HTMLResponse("<h1>GAIL Gemini Enterprise Demo Console Ready</h1>", status_code=200)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "gail_pipeline_agent",
        "grid_coverage_km": 18700,
        "active_corridor": "HVJ_Trunkline",
        "gemini_enterprise_app": "oil-and-gas-agentic-transformation"
    }


@app.get("/a2a/gail_grid_advisor/.well-known/agent-card.json")
def get_agent_card():
    """Returns official A2A v0.3 / v1.0 Agent Card."""
    from app.integration.agent_card import get_agent_card as build_card
    return build_card()


@app.post("/api/v1/prompt")
def handle_prompt(payload: PromptPayload):
    """Handles natural language conversational prompts from the 5-Act demonstration."""
    result = agent.execute_prompt(payload.prompt)
    return result


@app.get("/api/v1/report/latest", response_class=HTMLResponse)
def get_latest_executive_report():
    """Serves the latest compiled sovereign executive briefing HTML."""
    from app.integration.tools import compile_executive_briefing
    report = compile_executive_briefing()
    html_file = Path(report.compiled_html_path)
    if not html_file.exists():
        # Look in output_artifacts
        candidates = list(OUTPUT_DIR.glob("*.html"))
        if candidates:
            html_file = candidates[-1]
    if html_file.exists():
        with open(html_file, "r", encoding="utf-8") as f:
            return f.read()
    return HTMLResponse("<h3>Report compilation in progress...</h3>", status_code=200)


attach_reasoning_engine_routes(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
