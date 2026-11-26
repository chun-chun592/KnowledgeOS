"""Host-neutral client for the synthetic KnowledgeOS Broker."""

import argparse
import json
from pathlib import Path
import sys


def broker_request(endpoint, request):
    import pywintypes
    from write_transport import OutcomeUnknown, call

    if endpoint is None:
        return {"code": "SECURE_WRITER_UNAVAILABLE"}
    try:
        return call(*endpoint, request)
    except OutcomeUnknown:
        return {"code": "OUTCOME_UNKNOWN"}
    except (OSError, pywintypes.error):
        return {"code": "SECURE_WRITER_UNAVAILABLE"}
    except ValueError:
        return {"code": "INVALID_REQUEST"}


def main():
    from write_transport import decode, process_sid

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--vault", type=Path, help="Vault for the scoped, read-only inspect command")
    parser.add_argument("operation", choices=("create", "update", "restore", "status", "ping",
                                               "delete", "delete_status", "restore_deleted", "sync_wiki", "audit", "inspect"))
    parser.add_argument("--key")
    parser.add_argument("--path")
    parser.add_argument("--expected-sha256")
    parser.add_argument("--expected-identity")
    parser.add_argument("--backup-transaction")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if args.operation == "inspect":
        if args.vault is None:
            parser.error("--vault is required for inspect")
        return inspect_wiki(args.vault)
    if args.config is None:
        parser.error("--config is required for Broker operations")
    config = decode(args.config.read_bytes())
    if process_sid() != config["agent_sid"]:
        print(json.dumps({"code": "DENIED"}))
        return 1
    request = {"operation": args.operation}
    if args.operation == "audit":
        request.update(offset=args.offset, limit=args.limit)
    elif args.operation not in {"ping", "sync_wiki"}:
        if not args.key:
            parser.error("--key is required")
        request["key"] = args.key
    if args.operation in {"create", "update", "restore", "delete", "restore_deleted"}:
        if not args.path:
            parser.error("--path is required; provide Markdown on standard input")
        if args.operation in {"restore", "restore_deleted"}:
            if not args.backup_transaction:
                parser.error("--backup-transaction is required for restore")
            request["backup_transaction"] = args.backup_transaction
        elif args.operation != "delete":
            payload = sys.stdin.buffer.read(256 * 1024 + 1)
            if not payload or len(payload) > 256 * 1024:
                parser.error("Markdown must be nonempty and within the request limit")
            request["markdown"] = payload.decode("utf-8")
        request.update(path=args.path,
                       expected_sha256=args.expected_sha256, expected_identity=args.expected_identity)
    result = broker_request((config["broker_pipe"], config["broker_sid"]), request)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("code") in {"AVAILABLE", "COMMITTED", "SYNCED", "AUDIT_PAGE"} else 1


def inspect_wiki(root):
    """Invoke the same Agent-scoped read tools from a CLI-only host."""
    from pydantic import ValidationError
    from mcp.server.fastmcp.exceptions import ToolError
    from server import Wiki, make_server

    tools = {"search_knowledge", "read_markdown", "note_metadata", "query_tags",
             "knowledge_links", "lint_knowledge"}
    try:
        payload = sys.stdin.buffer.read(16_385)
        if len(payload) > 16_384:
            raise ValueError("inspect request too large")
        request = json.loads(payload)
        if (not isinstance(request, dict) or request.get("tool") not in tools
                or not isinstance(request.get("arguments"), dict)):
            raise ValueError("expected a read-only tool and an arguments object")
        tool = make_server(Wiki(root))._tool_manager.get_tool(request["tool"])
        arguments = tool.fn_metadata.arg_model.model_validate(request["arguments"])
        result = tool.fn(**dict(arguments))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, ToolError, ValidationError, OSError) as exc:
        print(json.dumps({"code": "READ_UNAVAILABLE", "detail": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
