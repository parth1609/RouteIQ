import os
import sys
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Ensure we can import sibling modules when running as a script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

# Load env
load_dotenv()

try:
    from zammad.zammad_integration import initialize_zammad_client
except Exception as e:
    # Fallback absolute import if running from project root
    from backend.zammad.zammad_integration import initialize_zammad_client  # type: ignore


def _iter_groups(client) -> List[Dict[str, Any]]:
    """Return a flat list of all group dicts using zammad_py pagination shape."""
    try:
        resp = client.group.all()
        items = resp.get("_items") if isinstance(resp, dict) else resp
        return list(items) if items else []
    except Exception:
        # Some clients may return an iterator
        try:
            return list(client.group.all())
        except Exception as e:
            raise RuntimeError(f"Failed to fetch groups: {e}")


def get_group_by_name(client, name: str) -> Optional[Dict[str, Any]]:
    """Case-insensitive search for a group by name."""
    target = (name or "").strip().lower()
    if not target:
        return None
    for g in _iter_groups(client):
        gname = str(g.get("name", "")).strip().lower()
        if gname == target:
            return g
    return None


essential_group_defaults = {
    # Provide minimal safe defaults; override via params
    "active": True,
    "follow_up_possible": "new_ticket",
    "follow_up_assignment": False,
}


def create_group(client, name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a group with provided name and optional params. Only includes keys provided,
    so you can pass signature_id/email_address_id when you know them.
    """
    if not name or not name.strip():
        raise ValueError("Group name is required")

    payload: Dict[str, Any] = {"name": name.strip()}
    payload.update(essential_group_defaults)
    if params:
        # Only include non-None keys
        for k, v in params.items():
            if v is not None:
                payload[k] = v

    created = client.group.create(params=payload)
    # Some clients return created dict directly
    return created


def find_or_create_group(client, name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return existing group (by name) or create it with params."""
    existing = get_group_by_name(client, name)
    if existing:
        return existing
    return create_group(client, name, params)


def ensure_group(client=None, name: str = "", params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Public helper: initialize client if not provided, then find or create group by name.
    """
    if not client:
        client = initialize_zammad_client()
    return find_or_create_group(client, name, params)


__all__ = [
    "get_group_by_name",
    "create_group",
    "find_or_create_group",
    "ensure_group",
]

