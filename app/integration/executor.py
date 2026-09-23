"""A2UI runtime extension negotiating executor for Gemini Enterprise and A2A.

Intercepts each request to negotiate A2UI v0.9 and register activated extensions.
"""

from __future__ import annotations

import logging
from typing import Any, Optional, Sequence

from a2a.server.events import EventQueue
from a2a.types import AgentCard
from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
    RequestContext,
)

from app.contracts import ACTIVE_A2UI_CATALOG_VERSION, A2uiCatalogVersion
from app.integration.agent_card import A2UI_V09_EXTENSION_URI

logger = logging.getLogger(__name__)

A2UI_EXTENSION_PREFIX: str = "https://a2ui.org/a2a-extension/a2ui/"
A2UI_STATE_KEY: str = "active_a2ui_version"


def extract_requested_a2ui_extensions(context: RequestContext) -> list[str]:
    """Extract all A2UI extension URIs requested by the calling client."""
    matched: list[str] = []

    if hasattr(context, "requested_extensions") and context.requested_extensions:
        for ext in context.requested_extensions:
            if isinstance(ext, str) and ext.startswith(A2UI_EXTENSION_PREFIX):
                matched.append(ext)

    if (
        hasattr(context, "message")
        and context.message
        and hasattr(context.message, "extensions")
        and context.message.extensions
    ):
        for ext in context.message.extensions:
            uri = getattr(ext, "uri", None)
            if uri and isinstance(uri, str) and uri.startswith(A2UI_EXTENSION_PREFIX):
                if uri not in matched:
                    matched.append(uri)

    return matched


def extract_supported_a2ui_extensions(agent_card: AgentCard | None) -> list[str]:
    """Extract all A2UI extension URIs supported by this agent."""
    if not agent_card or not hasattr(agent_card, "capabilities") or not agent_card.capabilities:
        return [A2UI_V09_EXTENSION_URI]

    supported: list[str] = []
    for ext in agent_card.capabilities.extensions:
        uri = getattr(ext, "uri", None)
        if uri and isinstance(uri, str) and uri.startswith(A2UI_EXTENSION_PREFIX):
            supported.append(uri)

    return supported or [A2UI_V09_EXTENSION_URI]


def resolve_a2ui_version(matched_uris: Sequence[str]) -> str | None:
    """Resolve the highest compatible A2UI version from matched extension URIs."""
    if not matched_uris:
        return None

    version_priority = {
        "v0.8": 1,
        "v0.9": 2,
    }

    best_version: str | None = None
    best_rank = 0

    for uri in matched_uris:
        version_str = uri.removeprefix(A2UI_EXTENSION_PREFIX).strip()
        rank = version_priority.get(version_str, 0)
        if rank > best_rank:
            best_rank = rank
            best_version = version_str

    if best_version is None and matched_uris:
        best_version = matched_uris[0].removeprefix(A2UI_EXTENSION_PREFIX).strip()

    return best_version


def try_activate_a2ui_extension(
    context: RequestContext,
    agent_card: AgentCard | None = None,
) -> str | None:
    """Negotiate and activate the A2UI extension for the current request turn."""
    requested = extract_requested_a2ui_extensions(context)
    if not requested:
        return None

    supported = extract_supported_a2ui_extensions(agent_card)
    matched = [uri for uri in requested if uri in supported]

    if not matched:
        return None

    version = resolve_a2ui_version(matched)
    return version


class A2uiNegotiatingExecutor(A2aAgentExecutor):
    """A2A Agent Executor that negotiates A2UI extension headers and saves state."""

    def __init__(self, runner: Any, config: Optional[A2aAgentExecutorConfig] = None) -> None:
        super().__init__(runner=runner, config=config)

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        agent_card = getattr(self, "_agent_card", None)
        active_version = try_activate_a2ui_extension(context, agent_card)
        if active_version:
            logger.info("A2UI Extension activated: %s", active_version)

        await super().execute(context, event_queue)
