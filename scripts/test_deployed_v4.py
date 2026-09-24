"""Live A2A test of the DEPLOYED agent: Q1-Q6 in one conversation (same contextId).

Usage: .venv/bin/python scripts/test_deployed_v4.py [runs]
Prints, per question: latency, whether an A2UI card arrived, surface id, and the reply text.
"""
import json
import sys
import time
import urllib.request
import uuid

import google.auth
import google.auth.transport.requests

URL = ("https://asia-south1-aiplatform.googleapis.com/reasoningEngines/v1/projects/349946979746/"
       "locations/asia-south1/reasoningEngines/6842313636208181248/api/a2a/app")

QUESTIONS = [
    ("Q1", "What is the impact of the Qatar force majeure on our winter gas supply?"),
    ("Q2", "Check our own position: inventory, customer commitments."),
    ("Q3", "What is gas costing today, and what does that mean for our contracts and our budget?"),
    ("Q4", "How have gas prices moved over the last 5 years, and what drove them?"),
    ("Q5", "What do the experts expect?"),
    ("Q6", "Run a Monte Carlo simulation of winter prices and test three options against our risk limit and deadlines: lock in now, lock in half, or wait. What do you recommend?"),
    ("Q7", "Prepare the approval and stage it in SAP."),
    ("GE", "Why do we need Gemini Enterprise for this?"),
]


def token() -> str:
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def send(tok: str, text: str, context_id: str | None):
    msg = {"role": "user", "messageId": str(uuid.uuid4()), "parts": [{"kind": "text", "text": text}]}
    if context_id:
        msg["contextId"] = context_id
    body = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send", "params": {"message": msg}}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return json.loads(r.read().decode())


def summarise(res: dict):
    result = res.get("result") or {}
    texts, surfaces = [], []
    for art in result.get("artifacts", []) or []:
        for p in art.get("parts", []):
            if p.get("kind") == "text" or "text" in p:
                texts.append(p.get("text", ""))
            data = p.get("data")
            if isinstance(data, dict):
                blob = json.dumps(data)
                if "updateComponents" in blob or "surfaceId" in blob:
                    sid = None
                    for key in ("surfaceId", "surface_id"):
                        if key in blob:
                            i = blob.index(key)
                            sid = blob[i:i + 60].split('"')[2] if blob[i:i + 60].count('"') >= 3 else None
                            break
                    surfaces.append(sid or "card")
    for m in result.get("history", []) or []:
        if m.get("role") == "agent":
            texts.extend(p.get("text", "") for p in m.get("parts", []) if p.get("kind") == "text")
    return result.get("contextId"), texts, surfaces, res.get("error")


def main(runs: int = 1):
    for run in range(1, runs + 1):
        tok, ctx = token(), None
        print(f"\n################ RUN {run} ################")
        for qid, q in QUESTIONS:
            t0 = time.time()
            try:
                res = send(tok, q, ctx)
            except Exception as e:  # noqa: BLE001
                print(f"\n=== {qid}: {q}\nFAILED: {e}")
                continue
            new_ctx, texts, surfaces, err = summarise(res)
            ctx = ctx or new_ctx
            print(f"\n=== {qid}: {q}  ({time.time() - t0:.1f}s) card={surfaces or 'NONE'} err={err}")
            print(" ".join(t.strip() for t in texts if t.strip())[:1200])


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
