"""Reasoning engine adapter for Vertex AI Agent Engine."""

from typing import Any
from fastapi import FastAPI


def attach_reasoning_engine_routes(app: FastAPI) -> None:
    @app.get("/reasoningEngine/health")
    def re_health():
        return {"status": "HEALTHY", "engine": "gail_grid_advisor"}
