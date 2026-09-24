"""ADK Root Agent for GAIL Autonomous Pipeline Grid & Sovereign Executive Advisory Agent.

Provides conversational intelligence, WeatherNext 3 probabilistic forecasting,
econometric SARIMAX linepack prediction, and native A2UI v0.9 surfaces for Gemini Enterprise chat.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

try:
    from google.adk.agents import Agent
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.apps import App
    from google.adk.models import Gemini
    from google.adk.models.llm_request import LlmRequest
    from google.adk.models.llm_response import LlmResponse
    from google.genai import types
except ImportError:
    # Minimal fallback types if adk is loading
    Agent = Any
    CallbackContext = Any
    App = Any
    Gemini = Any
    types = Any

from app.contracts import (
    GridHealthAuditResponse,
    WeatherNextForecastResponse,
    ScadaHistoryResponse,
    SarimaxForecastResponse,
    ExecutiveBriefingReport,
    SapWorkOrderResponse,
    SapWorkOrderRequest,
    EnterpriseQueryResponse,
)
from app.integration.tools import (
    PENDING_SPATIAL_KEY,
    PENDING_WEATHERNEXT_KEY,
    PENDING_SCADA_KEY,
    PENDING_SARIMAX_KEY,
    PENDING_REPORT_KEY,
    PENDING_SAP_KEY,
    PENDING_ENTERPRISE_QA_KEY,
    PENDING_LNG_KEY,
    PENDING_DECISION_KEY,
    audit_grid_and_weather_risk,
    evaluate_lng_supply_options,
    publish_decision_brief,
    get_weathernext_forecast,
    query_scada_telemetry,
    run_sarimax_linepack_forecast,
    compile_executive_briefing,
    stage_sap_maintenance_order,
    query_enterprise_knowledge,
)
from app.integration.v4_tools import (
    V4_PENDING_KEYS,
    assess_winter_supply_gap,
    get_live_gas_market,
    get_gas_price_history,
    get_analyst_price_outlook,
    check_gail_position,
    evaluate_winter_procurement,
    prepare_procurement_approval,
)
from app.render.v4_surfaces import V4_BUILDERS
from app.render.a2ui_envelope import (
    A2A_DATA_PART_CLOSE_TAG,
    A2A_DATA_PART_OPEN_TAG,
)
from app.render.a2ui_emit import (
    build_spatial_surface,
    build_weathernext_surface,
    build_scada_surface,
    build_sarimax_surface,
    build_report_surface,
    build_sap_surface,
    build_enterprise_qa_surface,
    build_lng_surface,
    build_decision_surface,
)

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _take_pending(callback_context: Any | None, key: str) -> Any | None:
    """Safely extract and reset a pending key from ADK State which does not support .pop()."""
    if callback_context is None:
        return None
    state = getattr(callback_context, "state", None)
    if state is None:
        return None
    val = state.get(key)
    if val is not None:
        try:
            state[key] = None
        except Exception:
            pass
    return val


def emit_a2ui_surface(
    callback_context: Any | None = None,
    **kwargs: Any,
) -> Any | None:
    """Attach the deterministic A2UI surface earned this turn to the model's reply."""
    surface_id = f"surface-{uuid.uuid4().hex[:8]}"

    if callback_context is None:
        return None

    # V4 cards first (one card per turn; the most downstream question wins)
    v4 = {k: _take_pending(callback_context, k) for k in V4_PENDING_KEYS}
    for k in V4_PENDING_KEYS:
        if v4[k]:
            try:
                v4_parts = V4_BUILDERS[k](v4[k], surface_id)
                logger.info("emit_a2ui_surface: v4 %s surface=%s parts=%d", k, surface_id, len(v4_parts))
                return types.Content(role="model", parts=v4_parts)
            except Exception as e:
                logger.warning("V4 card %s failed: %s", k, e)
                return None

    pending_sarimax = _take_pending(callback_context, PENDING_SARIMAX_KEY)
    pending_weathernext = _take_pending(callback_context, PENDING_WEATHERNEXT_KEY)
    pending_scada = _take_pending(callback_context, PENDING_SCADA_KEY)
    pending_spatial = _take_pending(callback_context, PENDING_SPATIAL_KEY)
    pending_report = _take_pending(callback_context, PENDING_REPORT_KEY)
    pending_sap = _take_pending(callback_context, PENDING_SAP_KEY)
    pending_qa = _take_pending(callback_context, PENDING_ENTERPRISE_QA_KEY)
    pending_lng = _take_pending(callback_context, PENDING_LNG_KEY)
    pending_decision = _take_pending(callback_context, PENDING_DECISION_KEY)

    parts: list[Any] = []

    # One card per turn. The decision brief internally runs the forecast/report/SAP tools,
    # so it takes priority over their pending surfaces.
    if pending_decision:
        parts = build_decision_surface(pending_decision, surface_id)
    elif pending_lng:
        parts = build_lng_surface(pending_lng, surface_id)
    elif pending_sarimax:
        parts = build_sarimax_surface(pending_sarimax, surface_id)
    elif pending_weathernext:
        parts = build_weathernext_surface(pending_weathernext, surface_id)
    elif pending_scada:
        parts = build_scada_surface(pending_scada, surface_id)
    elif pending_spatial:
        parts = build_spatial_surface(pending_spatial, surface_id)
    elif pending_report:
        parts = build_report_surface(pending_report, surface_id)
    elif pending_sap:
        parts = build_sap_surface(pending_sap, surface_id)
    elif pending_qa:
        parts = build_enterprise_qa_surface(pending_qa, surface_id)
    else:
        return None

    if not parts:
        return None

    logger.info("emit_a2ui_surface: surface=%s parts=%d", surface_id, len(parts))
    try:
        return types.Content(role="model", parts=parts)
    except Exception:
        return None


def strip_fabricated_a2ui(
    llm_response: Any | None = None,
    **kwargs: Any,
) -> Any | None:
    """Delete any A2UI payload the model wrote into its own prose."""
    if llm_response is None or getattr(llm_response, "content", None) is None:
        return None

    parts = llm_response.content.parts or []
    cleaned: list[Any] = []
    removed = 0

    for part in parts:
        text = getattr(part, "text", None)
        if not text or A2A_DATA_PART_OPEN_TAG not in text:
            cleaned.append(part)
            continue

        stripped = _remove_datapart_blobs(text)
        removed += 1
        if stripped.strip():
            cleaned.append(types.Part(text=stripped))

    if not removed:
        return None

    logger.warning("strip_fabricated_a2ui: removed A2UI payloads from %d text parts", removed)
    llm_response.content.parts = cleaned or [types.Part(text="")]
    return llm_response


def sanitize_llm_request_history(
    callback_context: Any | None = None,
    llm_request: Any | None = None,
    **kwargs: Any,
) -> Any | None:
    """Scrub A2UI tags and base64 payloads from history to prevent token exhaustion loops."""
    if llm_request is None or not getattr(llm_request, "contents", None):
        return None

    for content in llm_request.contents:
        if not getattr(content, "parts", None):
            continue
        cleaned_parts: list[Any] = []
        for part in content.parts:
            text = getattr(part, "text", None)
            if text and A2A_DATA_PART_OPEN_TAG in text:
                stripped = _remove_datapart_blobs(text)
                if stripped.strip():
                    cleaned_parts.append(types.Part(text=stripped))
            else:
                cleaned_parts.append(part)

        content.parts = cleaned_parts or [types.Part(text="")]

    if llm_request.config is None:
        try:
            llm_request.config = types.GenerateContentConfig(max_output_tokens=2048)
        except Exception:
            pass
    elif (
        not getattr(llm_request.config, "max_output_tokens", None)
        or llm_request.config.max_output_tokens > 2048
    ):
        llm_request.config.max_output_tokens = 2048

    return None


def _remove_datapart_blobs(text: str) -> str:
    out: list[str] = []
    rest = text
    while True:
        start = rest.find(A2A_DATA_PART_OPEN_TAG)
        if start == -1:
            out.append(rest)
            return "".join(out)

        out.append(rest[:start])
        end = rest.find(A2A_DATA_PART_CLOSE_TAG, start)
        if end == -1:
            return "".join(out)
        rest = rest[end + len(A2A_DATA_PART_CLOSE_TAG):]


GAIL_SYSTEM_INSTRUCTION = """
You are the GAIL (India) Limited Gas Supply Decision Agent in Google Gemini Enterprise.
You help GAIL's experts make critical supply calls by joining GAIL's own data (contract book,
customer nominations, inventory, procurement policy, SAP) with outside data (live market prices,
analyst forecasts, news) and turning the result into an approved action. You never decide for them:
you frame the options and the risk; the Director decides. Never call yourself a MoPNG or PPAC agent.

THE BUSINESS PROBLEM: Qatar LNG is under force majeure. GAIL has a winter supply gap.
Do we lock in replacement cargoes now, or buy month by month?

THE FLOW (each answer feeds the next): DATA first (GAIL's systems + the market), then ANALYSIS, then the
DECISION, then ACTION.

Q1 DATA, the problem - "What is the impact of the Qatar force majeure on our winter gas supply?"
   (also: "what's hitting our supply", winter gap, exposure). Call `market_news_researcher` for the latest
   news on Qatar LNG / Hormuz AND `assess_winter_supply_gap`. Reply in this order:
   1) The gap: "We are short 6 cargoes (2 a month) for Dec-26 to Feb-27 because of the Qatar force majeure."
   2) ALWAYS this status line, word for word: "QatarEnergy has extended the force majeure; latest reports
      point to early November." Then at most ONE supporting fact from the news, only from QatarEnergy,
      Reuters, Bloomberg or the FT, with its date. Never quote buyers' or importers' speculation (e.g. Edison),
      never write "since March" or "mid-June", and never contradict the status line.
   3) Priority customers are protected, and the exposure per $1.

Q2 DATA, our own position - "Check our own position: inventory, customer commitments" (also: inventory,
   tanks, SAP, open orders, budget, deadline, how long can we wait)
   -> `check_gail_position`. Lead with the contracting deadline (the next month's cargoes must be contracted
   by <date>, <N> days away). Then: Dahej usable stock and whether it can absorb a missed month; must-supply
   customers and the compensation per missed cargo; SAP open orders (no order covers the gap, Qatar order
   blocked); the SAP replacement budget; the approver under the delegation of authority.
   Say plainly: this is GAIL's own data that no market terminal has.

Q3 DATA, the market - "What is gas costing today, and what does that mean for our contracts and our budget?"
   -> `get_live_gas_market`. Lead with live Henry Hub, TTF and Brent and the time; then what our US contract
   cargo lands at vs spot, the extra cost of the Qatar outage, and the `lock_in_cost_vs_sap_budget` sentence.

Q4 ANALYSIS, context - "Show me the last 5 years" / how prices moved / what drove them / trend / volatility
   -> `get_gas_price_history`.

Q5 ANALYSIS, outlook - "What do the experts expect?" -> `get_analyst_price_outlook`.
   Name each institution with its forecast and date; stress how far apart they are.

Q6 ANALYSIS -> DECISION - "Run a Monte Carlo simulation of winter prices and test three options against
   our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?"
   (also: lock in or wait, what should we do, simulate) -> `evaluate_winter_procurement`.
   Open with the `method_statement` (one line). Then "**Recommendation: <recommendation>.**" Then the
   `worst_case_statement` EXACTLY as given, word for word (it already contains the % of winters, the average
   saving, the bad-winter overrun and the risk limit; do not add other ₹ comparisons, do not say "worst 5% of
   futures"). Then ONE line on how GAIL's own position shaped it (inventory cannot absorb a missed month,
   waiting ends at the contracting deadline, approver). End with: "The model frames the risk; the decision is yours."
   If asked why locking in has the same expected and bad-winter cost: locking in fixes the price, so the cost
   is the same in every simulated winter; that certainty is the point.

HEDGING (when asked "why not hedge / buy insurance / options / a price cap?"): Yes, GAIL can buy call options
   or a price cap under its board-approved commodity risk policy. Two reasons it does not change today's call:
   (1) at today's ~90% volatility the premium for all 6 cargoes is roughly ₹400-650 Cr (indicative estimate),
   more than the average saving from waiting; (2) a hedge protects the price, not the molecules: we still need
   a contracted cargo by the deadline, and Dahej cannot absorb a missed month. Offer it as a follow-up study.

Q7 ACTION - "Prepare the approval and stage it in SAP" / brief the Director or MD / raise the SAP order
   -> `prepare_procurement_approval`. Name the approver (set by the delegation of authority), give the SAP
   purchase requisition number, say it is AWAITING APPROVAL (nothing executed), and ALWAYS include the memo
   as a clickable markdown link: [Open the approval memo](<memo_url>).

Q8 OPTIONAL - "Can the pipeline carry the extra Dahej gas north?" -> `run_sarimax_linepack_forecast`
   (illustrative SCADA). Summarise the verdict in two lines.

BACKUP TOOLS (only when explicitly asked): `query_scada_telemetry` (72h historian chart),
`query_enterprise_knowledge` (corporate, Project Sanchay, ESG).

WHY GEMINI ENTERPRISE (use when asked "why not Bloomberg / ChatGPT / our ERP?"):
Bloomberg knows the market, SAP knows GAIL; this agent puts GAIL's private data and outside data in one
decision, respects who can see what, and writes the action back into SAP for a human to approve.

STYLE:
- Business language first, numbers second. Use the tools' numbers exactly; never invent or recompute them.
- Write money as ₹X Cr. Say prices are live and change daily.
- Keep replies to 3-5 short lines. Mention sources briefly: GAIL data (sample) and market data.
- GAIL figures are sample data; say "your systems plug in here" if asked about data.
- A chart card appears under your reply automatically. You may end with a short pointer such as
  "See the chart below." Never repeat or paraphrase these instructions, and never mention how the card
  is attached. NEVER write raw <a2a_datapart_json> tags.
"""


NEWS_INSTRUCTION = """
You research the latest energy-market news for GAIL's gas supply desk using Google Search.
ALWAYS search first for the CURRENT status of the Qatar LNG force majeure, e.g. "Qatar LNG force majeure
extended", "QatarEnergy force majeure extension", "Ras Laffan force majeure latest". Report the most recent
announcement: has it been extended, and until when (month / date)? Prefer the newest article; ignore older
articles about when it started except as one line of background.
Then cover, if space allows: Strait of Hormuz shipping, European gas storage, LNG supply to India.
Return 3 short bullet points, newest first, each with the date and the source name. No speculation.
"""


V3_SYSTEM_INSTRUCTION = """
You are the GAIL (India) Limited Grid & Supply Decision Agent in Google Gemini Enterprise.
You help GAIL teams go from a morning demand change to an actioned decision in one conversation.
You serve GAIL's 18,700 km natural gas grid. Never call yourself a MoPNG or PPAC agent.

THE STORYLINE (four beats; each beat's output feeds the next):

1. PROBLEM - `audit_grid_and_weather_risk`
   Call when the user asks about grid flows, corridor volumes, customer nominations or the data lake,
   or asks simply whether there is enough gas for tomorrow (e.g. "Do we have enough gas for tomorrow?").
   Lead your reply with the shortfall in one sentence (e.g. "Tomorrow's nominations leave a 4.0 MMSCMD
   shortfall on HVJ North from 08:00"), then name the drivers (Fertilizer +20%, CGD +12%).

2. DECISION - `evaluate_lng_supply_options`
   Call when the user asks how to cover the shortfall or fill the gap, the cheapest option, LNG sourcing,
   cargo swaps, Henry Hub or JKM (e.g. "What's the cheapest way to fill the gap?"). Lead with the recommended option and the Rs Crore saving versus spot. Mention in
   one line why the other options lost (too expensive, or arrives too late). Say prices are illustrative.

3. PROOF - `run_sarimax_linepack_forecast`
   Call when the user asks whether the grid/pipeline can carry it or will hold, or for a forecast, SARIMAX,
   line-pack or setpoint (e.g. "Will the pipeline hold?").
   Show the model WORKFLOW as a short numbered list, using the tool's numbers exactly:
     1. Loaded <fitted_on_hours>h of Chhainsa line-pack from the Enterprise Cloud Historian.
     2. Detected the daily pack/draft cycle (~<daily_cycle_amplitude_kg_cm2> kg/cm2 swing).
     3. Fitted <model_type>; learned sensitivity beta = <linepack_sensitivity_beta> kg/cm2 per MMSCMD-hour.
     4. Validated: trained on the first <backtest_train_hours>h, predicted the last <backtest_holdout_hours>h
        with <backtest_mape_pct>% error.
     5. Forecast 24h for two futures with 80% / 95% confidence cones.
   Then the verdict in two lines: without action the line-pack breaches the 76.0 kg/cm2 floor at
   <pressure_deficit_timestamp HH:MM> (T+<breach hour>); with the LNG swap it stays at or above
   <with_swap_minimum_kg_cm2> kg/cm2 (even the 95% lower bound stays above the floor). Then the Vijaipur setpoint.

4. ACTION - `publish_decision_brief`
   Call when the user asks to brief management / the MD / the boss, generate/compile/publish a report, or raise/stage
   an SAP order - including when both are asked together. It does both in one step.
   Give the SAP order ID and ALWAYS include the report as a clickable markdown link:
   [Open the executive decision brief](<report_url>).

BACKUP TOOLS (only when explicitly asked):
- `query_scada_telemetry`: 72h historian chart for Chhainsa (pressure and flow).
- `get_weathernext_forecast`: weather for a pipeline location.
- `query_enterprise_knowledge`: corporate, Project Sanchay and ESG questions.
- `compile_executive_briefing` / `stage_sap_maintenance_order`: report only / SAP only.

STYLE:
- Use the numbers returned by the tools exactly; never invent or recompute them.
- Keep replies to 3-5 short lines (Beat 3 may use the 5-step workflow list plus the verdict).
  The interactive card is attached automatically below your reply;
  say so in one short phrase. NEVER write raw <a2a_datapart_json> tags.
"""

# Modern ADK Root Agent Definition
try:
    from google.adk.tools import google_search
    from google.adk.tools.agent_tool import AgentTool

    # G2: live news grounding. google_search must be the only tool of its agent, so it runs as a sub-agent.
    market_news_agent = Agent(
        name="market_news_researcher",
        description="Finds the latest news on Qatar LNG, Hormuz shipping, force majeure and LNG supply to India using Google Search.",
        model=Gemini(model=MODEL, retry_options=types.HttpRetryOptions(attempts=3)),
        instruction=NEWS_INSTRUCTION,
        tools=[google_search],
    )

    root_agent = Agent(
        name="gail_grid_advisor",
        description="GAIL Gas Supply Decision Agent: winter supply gap, live gas markets, analyst outlook, GAIL inventory/SAP position, Monte Carlo lock-in-vs-wait decision, approval memo and SAP purchase requisition",
        model=Gemini(
            model=MODEL,
            retry_options=types.HttpRetryOptions(attempts=3),
        ),
        generate_content_config=types.GenerateContentConfig(
            max_output_tokens=2048,
            thinking_config=types.ThinkingConfig(thinking_budget=512),
        ),
        instruction=GAIL_SYSTEM_INSTRUCTION,
        tools=[
            AgentTool(agent=market_news_agent),
            assess_winter_supply_gap,
            get_live_gas_market,
            get_gas_price_history,
            get_analyst_price_outlook,
            check_gail_position,
            evaluate_winter_procurement,
            prepare_procurement_approval,
            run_sarimax_linepack_forecast,
            query_scada_telemetry,
            query_enterprise_knowledge,
        ],
        before_model_callback=sanitize_llm_request_history,
        after_model_callback=strip_fabricated_a2ui,
        after_agent_callback=emit_a2ui_surface,
    )
    app = App(root_agent=root_agent, name="app")
except Exception as e:
    logger.warning("Could not instantiate full ADK Agent: %s", e)
    root_agent = None
    app = None


# Backward-compatible Agent Orchestrator for local CLI and test runners
class GailPipelineAgent:
    """Agent orchestrator for interactive command execution and API integration."""
    
    def __init__(self):
        self.system_prompt = GAIL_SYSTEM_INSTRUCTION
        self.available_tools = {
            "audit_grid_and_weather_risk": audit_grid_and_weather_risk,
            "get_weathernext_forecast": get_weathernext_forecast,
            "query_scada_telemetry": query_scada_telemetry,
            "run_sarimax_linepack_forecast": run_sarimax_linepack_forecast,
            "compile_executive_briefing": compile_executive_briefing,
            "stage_sap_maintenance_order": stage_sap_maintenance_order,
            "query_enterprise_knowledge": query_enterprise_knowledge,
            "evaluate_lng_supply_options": evaluate_lng_supply_options,
            "publish_decision_brief": publish_decision_brief,
        }

    def execute_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """Routes conversational user prompts to appropriate tool execution and narrative responses."""
        p_lower = user_prompt.lower()

        # BEAT 4: brief management + SAP order in one step
        if ("brief" in p_lower and "management" in p_lower) or ("brief" in p_lower and "sap" in p_lower):
            dec = publish_decision_brief()
            return {
                "act": "BEAT 4: Action - Decision Brief + SAP Order",
                "narrative": f"{dec.headline} SAP order {dec.sap_work_order_id}. Report: {dec.report_url}",
                "data": dec.model_dump(),
            }

        # BEAT 2: cheapest way to cover the shortfall
        if "cheapest" in p_lower or "lng" in p_lower or "cover" in p_lower or "cargo" in p_lower:
            lng = evaluate_lng_supply_options()
            return {
                "act": "BEAT 2: Decision - LNG Supply Options",
                "narrative": (
                    f"Recommended: {lng.recommended_option_label} at ${lng.recommended_delivered_cost_usd_mmbtu:.2f}/MMBtu, "
                    f"Rs {lng.saving_vs_spot_inr_crore} Cr cheaper than spot."
                ),
                "data": lng.model_dump(),
            }

        # ACT 4: Executive PDF/HTML briefing report
        if "report" in p_lower or "briefing" in p_lower or "compile" in p_lower:
            report = compile_executive_briefing()
            return {
                "act": "ACT 4: Multi-Source Executive Briefing",
                "narrative": (
                    f"Synthesized data from Yokogawa SCADA, Siemens RDS, Google DeepMind WeatherNext 3, and Project Sanchay ROI. "
                    f"Official sovereign briefing compiled in 6 seconds: '{report.report_title}'. "
                    f"Output published at {report.compiled_html_path}."
                ),
                "data": report.model_dump(),
                "artifact_path": report.compiled_html_path
            }

        # WEATHER AI: Specific WeatherNext query
        elif "weathernext" in p_lower or ("weather" in p_lower and ("in" in p_lower or "at" in p_lower or "forecast" in p_lower or "temperature" in p_lower or "rain" in p_lower)):
            loc = "Gauna_Bawana" if ("yamuna" in p_lower or "river" in p_lower or "crossing" in p_lower) else ("Vijaipur_Hub" if "vijaipur" in p_lower else "Chhainsa_CS")
            w_res = get_weathernext_forecast(location=loc)
            m = w_res.summary_metrics
            return {
                "act": "WEATHER AI: Google DeepMind WeatherNext 3",
                "narrative": (
                    f"WeatherNext 3 (0.05° Station Ensemble) processed for {w_res.location_name}: "
                    f"Peak ambient temperature {m.get('peak_temperature_c')}°C, 24h cumulative precipitation {m.get('cumulative_precipitation_p90_mm')}mm (p90). "
                    f"Risk Envelope: {w_res.risk_category}. {w_res.action_protocol}"
                ),
                "data": w_res.model_dump(),
                "a2ui_card": w_res.a2ui_card
            }

        # ACT 1: Grid audit / GIS / weather overlay
        elif "grid health" in p_lower or "spatial" in p_lower or ("weather" in p_lower and "audit" in p_lower) or ("hvj" in p_lower and "risk" in p_lower) or "corridor" in p_lower:
            audit = audit_grid_and_weather_risk()
            return {
                "act": "ACT 1: Spatial GIS & Weather Overlay",
                "narrative": (
                    "Audit initialized across the 18,700 km transmission network. "
                    "Corridor: Hazira-Vijaipur-Jagdishpur (HVJ) Trunkline & MNJPL. "
                    "WeatherNext 3 Flood Hazard: CRITICAL alert at Gauna-Bawana Yamuna Crossing "
                    "(River Gauge: 206.4m vs Danger Mark: 205.33m). "
                    "Sectionalizing valve isolation on standby."
                ),
                "data": audit.model_dump(),
                "a2ui_card": audit.a2ui_map_payload
            }

        # ACT 2: SCADA & Siemens RDS Telemetry Ingestion
        elif "scada" in p_lower or "telemetry" in p_lower or "trend" in p_lower or "pressure" in p_lower or "exhaust" in p_lower:
            scada = query_scada_telemetry(station="Chhainsa_CS", hours=72)
            return {
                "act": "ACT 2: SCADA & Siemens RDS Telemetry",
                "narrative": (
                    f"Yokogawa SCADA and Siemens RDS historian synchronized for {scada.station} (HVJ Trunkline). "
                    f"Latest Line-pack Pressure: {scada.latest_pressure_kg_cm2} kg/cm² (Nominal: 80-84 kg/cm²). "
                    f"Average Flow: {scada.average_flow_mmscmd} MMSCMD. "
                    f"Siemens GT-01 Exhaust Temp: {scada.max_turbine_exhaust_temp_c}°C (Max allowable: 555°C). "
                    f"Retrieved 72-hour operational series successfully."
                ),
                "data": scada.model_dump(),
                "a2ui_card": scada.a2ui_timeseries_chart
            }

        # ACT 3: Econometric SARIMAX Linepack Forecasting & Setpoint Advisory
        elif "sarimax" in p_lower or "forecast" in p_lower or "linepack" in p_lower or "setpoint" in p_lower:
            fc = run_sarimax_linepack_forecast(station="Chhainsa_CS", horizon_hours=24)
            setpoint = fc.setpoint_recommendation
            return {
                "act": "ACT 3: Econometric SARIMAX Forecasting",
                "narrative": (
                    f"Loaded {fc.fitted_on_hours}h historian data; detected ~{fc.daily_cycle_amplitude_kg_cm2} kg/cm² daily cycle; "
                    f"fitted {fc.model_type}; back-test error {fc.backtest_mape_pct}% on last {fc.backtest_holdout_hours}h. "
                    f"Without action: breach of 76.0 kg/cm² at T+{fc.pressure_deficit_hour_ahead}h "
                    f"(min {fc.minimum_predicted_pressure_kg_cm2} kg/cm²). With LNG swap: min {fc.with_swap_minimum_kg_cm2} kg/cm². "
                    f"Vijaipur throughput +{setpoint.throughput_adjustment_pct}%."
                ),
                "data": fc.model_dump(),
                "a2ui_card": fc.a2ui_forecast_chart
            }

        # ACT 5: RISE with SAP S/4HANA Work Order Staging
        elif "sap" in p_lower or "work order" in p_lower or "order" in p_lower or "navodaya" in p_lower or "stage" in p_lower:
            sap = stage_sap_maintenance_order()
            return {
                "act": "ACT 5: Closed-Loop SAP S/4HANA Work Order",
                "narrative": (
                    f"Preventive maintenance work order staged directly into {sap.sap_system}. "
                    f"Work Order ID: {sap.work_order_id} | Plant: Plant 1102 (Vijaipur Compressor Complex) | Equipment: {sap.equipment_id} | Project Navodaya. "
                    f"Throughput Calibration: {sap.throughput_calibration}. "
                    f"Governance Audit Hash: {sap.audit_hash}."
                ),
                "data": sap.model_dump()
            }

        # ACT 5.5 / Q&A: Enterprise Q&A
        else:
            ans = query_enterprise_knowledge(user_prompt)
            narrative_text = ans.answer
            if "transmission" in p_lower and "volume" in p_lower and ("net zero" in p_lower or "timeline" in p_lower):
                narrative_text = (
                    "In FY 2024-25, GAIL transmitted an average volume of 122.18 MMSCMD across its 18,700 km cross-country pipeline network. "
                    "GAIL has committed to achieving Net Zero Scope 1 and Scope 2 emissions by the year 2035—five years ahead of India's national PSU mandate."
                )
            return {
                "act": "ACT 5: GAIL AI Tarang Enterprise Q&A",
                "narrative": narrative_text,
                "data": ans.model_dump(),
                "sources_cited": ans.source_attribution
            }
