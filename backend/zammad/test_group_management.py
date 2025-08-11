import os
import sys
import json
import argparse
from typing import Any, Dict
from dotenv import load_dotenv

# Ensure local imports work when run directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

load_dotenv()

try:
    from zammad.zammad_integration import initialize_zammad_client
except Exception:
    from backend.zammad.zammad_integration import initialize_zammad_client  # type: ignore

from zammad.group_tools import (
    get_group_by_name,
    create_group,
    find_or_create_group,
)


def pretty(obj: Any) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False)


def cmd_list(args):
    client = initialize_zammad_client()
    groups = client.group.all()
    items = groups.get("_items") if isinstance(groups, dict) else list(groups)
    print(pretty(items or []))


def cmd_find(args):
    client = initialize_zammad_client()
    grp = get_group_by_name(client, args.name)
    if grp:
        print(pretty(grp))
    else:
        print("{}")


def cmd_create(args):
    client = initialize_zammad_client()
    params: Dict[str, Any] = {}
    if args.signature_id is not None:
        params["signature_id"] = args.signature_id
    if args.email_address_id is not None:
        params["email_address_id"] = args.email_address_id
    created = create_group(client, args.name, params=params)
    print(pretty(created))


def cmd_ensure(args):
    client = initialize_zammad_client()
    created = find_or_create_group(client, args.name)
    print(pretty(created))


def cmd_rename(args):
    client = initialize_zammad_client()
    grp = get_group_by_name(client, args.old)
    if not grp:
        raise SystemExit(f"Group not found: {args.old}")
    updated = client.group.update(grp["id"], params={"name": args.new})
    print(pretty(updated))


def main():
    parser = argparse.ArgumentParser(description="Test Zammad group management helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List all groups")
    p_list.set_defaults(func=cmd_list)

    p_find = sub.add_parser("find", help="Find group by name")
    p_find.add_argument("name", help="Group name")
    p_find.set_defaults(func=cmd_find)

    p_create = sub.add_parser("create", help="Create group by name")
    p_create.add_argument("name", help="Group name")
    p_create.add_argument("--signature-id", type=int, default=None)
    p_create.add_argument("--email-address-id", type=int, default=None)
    p_create.set_defaults(func=cmd_create)

    p_ensure = sub.add_parser("ensure", help="Find or create group by name")
    p_ensure.add_argument("name", help="Group name")
    p_ensure.set_defaults(func=cmd_ensure)

    p_rename = sub.add_parser("rename", help="Rename a group")
    p_rename.add_argument("old", help="Existing group name")
    p_rename.add_argument("new", help="New group name")
    p_rename.set_defaults(func=cmd_rename)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
