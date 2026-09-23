#!/usr/bin/env python3
"""
Interactive & Automated 5-Act Demonstration Runner for GAIL Pipeline Grid Agent.
Executes all 5 Acts sequentially, validates responses, and generates live artifacts.
Usage:
    python demo_runner.py
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.agent import GailPipelineAgent

DEMO_ACTS = [
    {
        "act_num": 1,
        "name": "Spatial GIS Grid Infrastructure & Environmental Weather Layer",
        "prompt": "Gemini, initialize a grid health and risk audit across the HVJ and MNJPL pipeline corridors for the next 24 hours.",
        "expected_keywords": ["18,700", "Gauna-Bawana", "Yamuna", "206.4m", "danger mark"]
    },
    {
        "act_num": 2,
        "name": "SCADA Telemetry Ingestion & Turbine Observability",
        "prompt": "Access live telemetry for Chhainsa Compressor Station and plot 72-hour historical trends for line-pack pressure, gas flow rate, and Siemens turbine exhaust temperatures.",
        "expected_keywords": ["Chhainsa", "Yokogawa", "81.47", "549.4"]
    },
    {
        "act_num": 3,
        "name": "Deterministic SARIMAX Demand Forecasting & Optimal Setpoint",
        "prompt": "Execute a 24-hour predictive SARIMAX demand forecast for Chhainsa station considering downstream fertilizer plant off-takes, and calculate optimal compressor setpoints at Vijaipur.",
        "expected_keywords": ["SARIMAX", "deficit", "Vijaipur", "+3.8%", "18,500 SCM", "Project Sanchay"]
    },
    {
        "act_num": 4,
        "name": "Multi-Source Automated Executive Briefing Compilation",
        "prompt": "Compile this grid audit, weather assessment, SARIMAX forecast, and fuel-saving calculations into an official Daily Line-Pack & Integrity Executive Briefing.",
        "expected_keywords": ["Executive Briefing", "compiled", ".html"]
    },
    {
        "act_num": 5,
        "name": "Closed-Loop SAP S/4HANA Work Order Staging",
        "prompt": "Log this optimization advisory and stage a preventive work order directly into RISE with SAP S/4HANA Cloud.",
        "expected_keywords": ["SAP S/4HANA", "Work Order", "Project Navodaya", "Plant 1102"]
    },
    {
        "act_num": 5.5,
        "name": "GAIL AI Tarang Natural Language Enterprise Q&A",
        "prompt": "What was our total natural gas transmission volume last fiscal year, and what is our Net Zero Scope-1 target timeline?",
        "expected_keywords": ["122.18 MMSCMD", "2035", "Scope 1"]
    }
]

def run_demonstration():
    print("=" * 80)
    print("  GAIL (INDIA) LIMITED | GEMINI ENTERPRISE 5-ACT DEMONSTRATION RUNNER")
    print("=" * 80)
    print("Initializing ADK Agent Orchestrator...")
    
    agent = GailPipelineAgent()
    print("Agent ready. Commencing 5-Act Demonstration Sequence.\n")
    
    total_passed = 0
    start_all = time.time()
    
    for item in DEMO_ACTS:
        act_id = item["act_num"]
        title = item["name"]
        prompt = item["prompt"]
        expected = item["expected_keywords"]
        
        print(f"\n--- [ACT {act_id}]: {title} ---")
        print(f"Presenter Prompt: \"{prompt}\"")
        
        t0 = time.time()
        result = agent.execute_prompt(prompt)
        elapsed = time.time() - t0
        
        narrative = result.get("narrative", "")
        print(f"Latency: {elapsed:.2f}s | Act Tag: {result.get('act')}")
        print(f"Agent Response:\n{narrative}")
        
        # Verify keywords
        missing = [kw for kw in expected if kw.lower() not in narrative.lower() and kw.lower() not in str(result.get("data", "")).lower()]
        if not missing:
            print("Status: [PASS] All operational facts and numerical targets verified.")
            total_passed += 1
        else:
            print(f"Status: [WARN] Missing expected keywords: {missing}")
            
    total_elapsed = time.time() - start_all
    print("\n" + "=" * 80)
    print(f"DEMONSTRATION SCORECARD: {total_passed}/{len(DEMO_ACTS)} Acts Verified in {total_elapsed:.2f}s")
    print("Executive Briefing Artifacts generated in output_artifacts/")
    print("=" * 80)

if __name__ == "__main__":
    run_demonstration()
