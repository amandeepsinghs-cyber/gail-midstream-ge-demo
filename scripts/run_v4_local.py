"""
F2: local end-to-end rehearsal of the V4 flow through the real ADK agent + Gemini (Vertex AI).

    GOOGLE_CLOUD_PROJECT=og-agentic-ecosystem .venv/bin/python scripts/run_v4_local.py

For each business question prints: tools called, the agent's reply, and whether an A2UI card was attached.
"""

import asyncio
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "og-agentic-ecosystem")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "asia-south1")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from app.agent import root_agent  # noqa: E402
from app.render.a2ui_envelope import A2A_DATA_PART_OPEN_TAG  # noqa: E402

QUESTIONS = [
    ("Q1", "What is the impact of the Qatar force majeure on our winter gas supply?"),
    ("Q2", "Check our own position: inventory, customer commitments."),
    ("Q3", "What is gas costing today, and what does that mean for our contracts and our budget?"),
    ("Q4", "How have gas prices moved over the last 5 years, and what drove them?"),
    ("Q5", "What do the experts expect?"),
    ("Q6", "Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?"),
    ("Q7", "Prepare the approval and stage it in SAP."),
]


async def main() -> None:
    runner = InMemoryRunner(agent=root_agent, app_name="app")
    session = await runner.session_service.create_session(app_name="app", user_id="rehearsal")
    for qid, q in QUESTIONS:
        t0 = time.time()
        tools, text, card = [], [], False
        async for ev in runner.run_async(user_id="rehearsal", session_id=session.id,
                                         new_message=types.Content(role="user", parts=[types.Part(text=q)])):
            for p in (ev.content.parts if ev.content else []) or []:
                if getattr(p, "function_call", None):
                    tools.append(p.function_call.name)
                blob = getattr(p, "inline_data", None)
                if blob is not None and blob.data and A2A_DATA_PART_OPEN_TAG.encode() in blob.data:
                    card = True
                if getattr(p, "text", None):
                    if A2A_DATA_PART_OPEN_TAG in p.text:
                        card = True
                    elif ev.author == root_agent.name:
                        text.append(p.text)
        print(f"\n=== {qid}: {q}  ({time.time() - t0:.1f}s)")
        print(f"tools: {tools} | card attached: {card}")
        print("".join(text).strip())


if __name__ == "__main__":
    asyncio.run(main())
