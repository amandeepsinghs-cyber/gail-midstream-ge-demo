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
  - ADK Reasoning Engine endpoints: /api/reasoning_engine, /api/stream_reasoning_engine
  - Agent Card: GET /a2a/gail_grid_advisor/.well-known/agent-card.json
  - A2A JSON-RPC 0.3 / 1.0: POST /a2a/gail_grid_advisor
  - Direct Prompt: POST /api/v1/prompt
  - Health: GET /health
  - Demo Console UI: GET /demo
"""

import contextlib
import os
from pathlib import Path
from collections.abc import AsyncIterator

from a2a.server.tasks import InMemoryTaskStore
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from google.adk.cli.fast_api import get_fast_api_app
from google.adk.runners import Runner
from pydantic import BaseModel

from app.agent import GailPipelineAgent
from app.app_utils import services
from app.app_utils.a2a import attach_a2a_routes
from app.app_utils.reasoning_engine_adapter import (
    attach_reasoning_engine_routes,
)

load_dotenv()
otel_to_cloud = os.environ.get(
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY", ""
).lower() in ("true", "1")
allow_origins = (
    os.getenv("ALLOW_ORIGINS", "").split(",") if os.getenv("ALLOW_ORIGINS") else None
)

AGENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output_artifacts"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

legacy_agent = GailPipelineAgent()


class PromptPayload(BaseModel):
    prompt: str


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    from app.agent import app as adk_app
    from app.agent import root_agent

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

    for rpc_path in (f"/a2a/{adk_app.name}", "/a2a/gail_grid_advisor"):
        await attach_a2a_routes(
            app,
            agent=root_agent,
            runner=runner,
            task_store=InMemoryTaskStore(),
            rpc_path=rpc_path,
            capabilities=build_agent_capabilities(),
            executor=A2uiNegotiatingExecutor(runner=runner),
        )
    yield


app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    web=True,
    artifact_service_uri=services.ARTIFACT_SERVICE_URI,
    allow_origins=allow_origins,
    session_service_uri=services.SESSION_SERVICE_URI,
    otel_to_cloud=otel_to_cloud,
    lifespan=lifespan,
)
app.title = "GAIL Gas Supply Decision Agent"
app.description = "Combines GAIL's contracts, inventory and SAP data with live gas markets to recommend and stage winter LNG procurement decisions."

attach_reasoning_engine_routes(app)


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


@app.post("/api/v1/prompt")
def handle_prompt(payload: PromptPayload):
    """Handles natural language conversational prompts from the 5-Act demonstration."""
    return legacy_agent.execute_prompt(payload.prompt)


@app.get("/api/v1/report/latest", response_class=HTMLResponse)
def get_latest_executive_report():
    """Returns the latest compiled sovereign HTML executive briefing."""
    reports = sorted(OUTPUT_DIR.glob("GAIL_Executive_Briefing_*.html"), reverse=True)
    if not reports:
        res = legacy_agent.execute_prompt("compile executive briefing")
        local_path = Path(res["data"]["local_file_path"])
        return local_path.read_text(encoding="utf-8")
    return reports[0].read_text(encoding="utf-8")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
