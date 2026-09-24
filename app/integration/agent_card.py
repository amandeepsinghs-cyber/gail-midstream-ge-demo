"""Agent card capabilities declaration for Gemini Enterprise and Agent Registry.

Declares ADK executor and A2UI v0.9 extension support for GAIL Pipeline Grid Advisor.
"""

from typing import Dict, Any
from a2a.types import AgentCapabilities, AgentExtension

ADK_AGENT_EXECUTOR_EXTENSION_URI: str = (
    "https://google.github.io/adk-docs/a2a/a2a-extension/"
)
A2UI_V09_EXTENSION_URI: str = "https://a2ui.org/a2a-extension/a2ui/v0.9"
DEFAULT_GE_CATALOG_ID: str = (
    "https://www.gstatic.com/vertexaisearch/a2ui/v0_9/gemini_enterprise_composite_catalog.json"
)


def build_agent_capabilities() -> AgentCapabilities:
    """Build the comprehensive A2A capabilities descriptor for the agent card."""
    from google.protobuf.struct_pb2 import Struct

    catalog_params = Struct()
    catalog_params.update({"supportedCatalogIds": [DEFAULT_GE_CATALOG_ID]})

    return AgentCapabilities(
        streaming=True,
        extensions=[
            AgentExtension(
                uri=ADK_AGENT_EXECUTOR_EXTENSION_URI,
                description="Ability to use the modern ADK agent executor implementation",
            ),
            AgentExtension(
                uri=A2UI_V09_EXTENSION_URI,
                description="Ability to render rich A2UI v0.9 interactive components (VegaChart, Canvas, Material 3)",
                params=catalog_params,
            ),
        ],
    )


def get_agent_card() -> Dict[str, Any]:
    """Compatibility agent card dictionary for JSON-RPC endpoints."""
    return {
        "id": "GAIL-GRID-ADVISOR",
        "name": "GAIL Autonomous Pipeline Grid & Executive Advisory Agent",
        "version": "1.0.0",
        "protocol": "A2A JSON-RPC 0.3 / 1.0",
        "ui_extension": A2UI_V09_EXTENSION_URI,
        "governing_entity": "GAIL (India) Limited",
        "runtime_target": "agent_runtime",
        "description": "From a morning demand change to an actioned decision: nominations shortfall, LNG sourcing comparison, fitted SARIMAX line-pack forecast, executive brief and SAP order.",
        "skills": [
            "audit_grid_and_weather_risk",
            "evaluate_lng_supply_options",
            "publish_decision_brief",
            "get_weathernext_forecast",
            "query_scada_telemetry",
            "run_sarimax_linepack_forecast",
            "compile_executive_briefing",
            "stage_sap_maintenance_order",
            "query_enterprise_knowledge"
        ],
        "capabilities": {
            "streaming": True,
            "extensions": [
                ADK_AGENT_EXECUTOR_EXTENSION_URI,
                A2UI_V09_EXTENSION_URI,
            ],
        },
    }
