"""ADK session and artifact services configuration."""

import os

SESSION_SERVICE_URI = os.getenv("SESSION_SERVICE_URI", "sqlite:///./adk_sessions.db")
ARTIFACT_SERVICE_URI = os.getenv("ARTIFACT_SERVICE_URI", None)


def get_session_service():
    from google.adk.sessions import DatabaseSessionService
    return DatabaseSessionService(db_url=SESSION_SERVICE_URI)


def get_artifact_service():
    return None
