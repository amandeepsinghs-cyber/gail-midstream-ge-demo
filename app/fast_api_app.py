"""
FastAPI & A2A Server for GAIL Autonomous Pipeline Grid Agent.
Exposes:
  - Agent Card: GET /a2a/gail_grid_advisor/.well-known/agent-card.json
  - A2A RPC: POST /a2a/gail_grid_advisor
  - Direct Prompt: POST /api/v1/prompt
  - Latest Report Preview: GET /api/v1/report/latest
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent import GailPipelineAgent
from app.integration.tools import (
    audit_grid_and_weather_risk,
    query_scada_telemetry,
    run_sarimax_linepack_forecast,
    compile_executive_briefing,
    stage_sap_maintenance_order,
    query_enterprise_knowledge
)
from app.contracts import SapWorkOrderRequest

app = FastAPI(
    title="GAIL Autonomous Pipeline Grid & Advisory Agent",
    description="Gemini Enterprise End-to-End Agentic AI Microservice for GAIL (India) Limited",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = GailPipelineAgent()
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output_artifacts"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

class PromptPayload(BaseModel):
    prompt: str


@app.get("/", response_class=HTMLResponse)
@app.get("/demo", response_class=HTMLResponse)
def get_demo_console():
    """Serves the interactive 5-Act Demonstration Console UI."""
    template_path = TEMPLATES_DIR / "demo_console.html"
    if not template_path.exists():
        return HTMLResponse("<h1>Demo console template not found</h1>", status_code=404)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health_check():
    return {
        "status": "HEALTHY",
        "service": "gail_pipeline_agent",
        "grid_coverage_km": 18700,
        "active_corridor": "HVJ_Trunkline"
    }


@app.get("/a2a/gail_grid_advisor/.well-known/agent-card.json")
def get_agent_card():
    """Returns official A2A v0.3 / v1.0 Agent Card."""
    return {
        "id": "GAIL-GRID-ADVISOR",
        "name": "GAIL Autonomous Pipeline Grid & Executive Advisory Agent",
        "description": "Autonomous OT/IT agent for natural gas pipeline grid monitoring, SARIMAX forecasting, and SAP S/4HANA work order staging.",
        "version": "1.0.0",
        "protocol": "A2A JSON-RPC 0.3 / 1.0",
        "ui_extension": "https://a2ui.org/a2a-extension/a2ui/v0.9",
        "governing_entity": "GAIL (India) Limited",
        "runtime_target": "agent_runtime",
        "skills": [
            "audit_grid_and_weather_risk",
            "query_scada_telemetry",
            "run_sarimax_linepack_forecast",
            "compile_executive_briefing",
            "stage_sap_maintenance_order",
            "query_enterprise_knowledge"
        ]
    }


@app.post("/api/v1/prompt")
def handle_prompt(payload: PromptPayload):
    """Handles natural language conversational prompts from the 5-Act demonstration."""
    result = agent.execute_prompt(payload.prompt)
    return result


@app.get("/api/v1/report/latest", response_class=HTMLResponse)
def get_latest_executive_report():
    """Renders the latest compiled executive briefing directly in browser."""
    html_files = sorted(OUTPUT_DIR.glob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not html_files:
        # Generate one on the fly
        report = compile_executive_briefing()
        with open(report.compiled_html_path, "r", encoding="utf-8") as f:
            return f.read()
            
    with open(html_files[0], "r", encoding="utf-8") as f:
        return f.read()
