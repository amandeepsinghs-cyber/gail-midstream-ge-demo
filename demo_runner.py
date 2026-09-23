"""
GAIL (India) Limited | Gemini Enterprise 5-Act Demonstration Test Runner.
Verifies end-to-end autonomous execution across:
  - Act 1: Spatial GIS Infrastructure & Environmental Weather Risk
  - Weather AI: Google DeepMind WeatherNext 3 Probabilistic Ensemble Model
  - Act 2: SCADA Telemetry & Siemens RDS Observability
  - Act 3: Econometric SARIMAX Demand Forecasting (PPAC Standard)
  - Act 4: Sovereign Multi-Source Executive Briefing Compilation
  - Act 5: Closed-Loop SAP S/4HANA Work Order Staging & GAIL AI Tarang
"""

import sys
import time
from pathlib import Path

# Add current workspace to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent import GailPipelineAgent

DEMO_PROMPTS = [
    {
        "act": "ACT 1",
        "title": "Spatial GIS Grid Infrastructure & Environmental Weather Layer",
        "prompt": "Gemini, initialize a grid health and risk audit across the HVJ and MNJPL pipeline corridors for the next 24 hours.",
        "expected_keywords": ["18,700 km", "Yamuna", "206.4m", "205.33m"]
    },
    {
        "act": "WEATHER AI",
        "title": "Google DeepMind WeatherNext 3 Probabilistic Weather Forecast",
        "prompt": "Gemini, what is the WeatherNext 3 probabilistic weather forecast for the Yamuna River crossing?",
        "expected_keywords": ["WeatherNext", "0.05°", "Station Ensemble", "precipitation", "CRITICAL"]
    },
    {
        "act": "ACT 2",
        "title": "SCADA Telemetry Ingestion & Turbine Observability",
        "prompt": "Access live telemetry for Chhainsa Compressor Station and plot 72-hour historical trends for line-pack pressure, gas flow rate, and Siemens turbine exhaust temperatures.",
        "expected_keywords": ["Yokogawa", "72-hour", "81.47", "549.4"]
    },
    {
        "act": "ACT 3",
        "title": "Deterministic Econometric SARIMAX Demand Forecasting & Optimal Setpoint",
        "prompt": "Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa station considering downstream fertilizer plant off-takes, and calculate optimal compressor setpoints at Vijaipur.",
        "expected_keywords": ["SARIMAX", "deficit", "+3.8%", "18,500 SCM/day", "Sanchay"]
    },
    {
        "act": "ACT 4",
        "title": "Sovereign Multi-Source Automated Executive Briefing Compilation",
        "prompt": "Compile this grid audit, weather assessment, SARIMAX forecast, and fuel-saving calculations into an official Daily Line-Pack & Integrity Executive Briefing.",
        "expected_keywords": ["Executive Briefing", "compiled", "gs://"]
    },
    {
        "act": "ACT 5",
        "title": "Closed-Loop SAP S/4HANA Work Order Staging",
        "prompt": "Log this optimization advisory and stage a preventive work order directly into RISE with SAP S/4HANA Cloud.",
        "expected_keywords": ["WO-", "EQ-VIJ-GT-01", "Navodaya", "Plant 1102"]
    },
    {
        "act": "ACT 5.5",
        "title": "GAIL AI Tarang Natural Language Enterprise Q&A",
        "prompt": "What was our total natural gas transmission volume last fiscal year, and what is our Net Zero Scope-1 target timeline?",
        "expected_keywords": ["18,700 km", "122.18 MMSCMD", "2035", "Scope 1"]
    }
]

def run_demonstration():
    print("=" * 80)
    print("  GAIL (INDIA) LIMITED | GEMINI ENTERPRISE 5-ACT SOVEREIGN DEMONSTRATION RUNNER")
    print("=" * 80)
    print("Initializing ADK Agent Orchestrator...")
    agent = GailPipelineAgent()
    print("Agent ready. Commencing Demonstration Sequence.\n")

    total_start = time.time()
    passed = 0

    for step in DEMO_PROMPTS:
        act = step["act"]
        title = step["title"]
        prompt = step["prompt"]
        
        print(f"\n--- [{act}]: {title} ---")
        print(f"Presenter Prompt: \"{prompt}\"")
        
        t0 = time.time()
        response = agent.execute_prompt(prompt)
        elapsed = time.time() - t0
        
        narrative = response.get("narrative", "")
        print(f"Latency: {elapsed:.2f}s | Act Tag: {response.get('act')}")
        print(f"Agent Response:\n{narrative}")
        
        # Verify keywords
        missing = [kw for kw in step["expected_keywords"] if kw.lower() not in narrative.lower()]
        if not missing:
            print("Status: [PASS] All operational facts, metrics, and models verified.")
            passed += 1
        else:
            print(f"Status: [WARNING] Missing expected keywords: {missing}")

    total_elapsed = time.time() - total_start
    print("\n" + "=" * 80)
    print(f"DEMONSTRATION SCORECARD: {passed}/{len(DEMO_PROMPTS)} Gates Verified in {total_elapsed:.2f}s")
    print("Sovereign Executive Briefing generated in output_artifacts/ and GCS Data Lake.")
    print("=" * 80 + "\n")

    return passed == len(DEMO_PROMPTS)

if __name__ == "__main__":
    success = run_demonstration()
    sys.exit(0 if success else 1)
