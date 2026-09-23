"""A2UI v0.9 lifecycle message builders for Gemini Enterprise chat surfaces.

Builds 'createSurface', 'updateComponents', and 'updateDataModel' messages adhering strictly
to the Gemini Enterprise v0.9 composite catalog schema.
"""

from typing import Any, List, Dict
from app.contracts import A2uiCatalogVersion, A2uiMessage, DEFAULT_GE_CATALOG_ID


def build_create_surface(
    surface_id: str,
    catalog_id: str = DEFAULT_GE_CATALOG_ID
) -> A2uiMessage:
    """Build a 'createSurface' message to initialize a new visual surface in chat."""
    if not surface_id:
        raise ValueError("surface_id cannot be empty when creating a surface.")

    return A2uiMessage(
        message_type="createSurface",
        surface_id=surface_id,
        payload={
            "catalogId": catalog_id,
        },
        catalog_version=A2uiCatalogVersion.V0_9,
    )


def build_update_components(
    surface_id: str,
    components: List[Dict[str, Any]]
) -> A2uiMessage:
    """Build an 'updateComponents' message to declare or replace the UI hierarchy.
    
    In A2UI v0.9, components is a list of declarative component dictionaries.
    One component MUST have id="root".
    """
    if not surface_id:
        raise ValueError("surface_id cannot be empty when updating components.")
    if not components:
        raise ValueError("components list cannot be empty in updateComponents.")

    return A2uiMessage(
        message_type="updateComponents",
        surface_id=surface_id,
        payload={
            "components": components,
        },
        catalog_version=A2uiCatalogVersion.V0_9,
    )


def build_update_data_model(
    surface_id: str,
    value: Dict[str, Any],
    path: str | None = None,
) -> A2uiMessage:
    """Build an 'updateDataModel' message to bind data to the surface.
    
    The payload key MUST be 'value' per A2UI v0.9 specification.
    """
    if not surface_id:
        raise ValueError("surface_id cannot be empty when updating data model.")
    if not isinstance(value, dict):
        raise TypeError(f"value must be a dictionary, got {type(value).__name__}.")

    payload: Dict[str, Any] = {"value": value}
    if path:
        payload["path"] = path

    return A2uiMessage(
        message_type="updateDataModel",
        surface_id=surface_id,
        payload=payload,
        catalog_version=A2uiCatalogVersion.V0_9,
    )
