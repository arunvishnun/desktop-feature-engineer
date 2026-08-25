#!/usr/bin/env python3
"""Validate a Desktop Feature Engineer work graph without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


MODES = {"guided", "plan-only", "auto"}
KINDS = {
    "discovery", "contract", "domain", "runtime", "ipc", "persistence",
    "ui", "observability", "migration", "test", "packaging", "security", "review",
}
RISKS = {"low", "medium", "high"}
STATUSES = {
    "pending", "ready", "in_progress", "verified", "blocked", "failed", "skipped", "deferred",
}
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
NODE_KEYS = {
    "id", "title", "goal", "kind", "dependencies", "inputs", "outputs", "acceptance",
    "checks", "risk", "status", "attempts", "evidence", "blocker", "notes",
}
REQUIRED_NODE_KEYS = NODE_KEYS - {"blocker", "notes"}
ROOT_KEYS = {"version", "taskId", "goal", "mode", "acceptanceCriteria", "assumptions", "nodes"}
REQUIRED_ROOT_KEYS = ROOT_KEYS - {"assumptions"}


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def string_list(value: Any, *, nonempty: bool = False) -> bool:
    return (
        isinstance(value, list)
        and (not nonempty or bool(value))
        and all(nonempty_string(item) for item in value)
    )


def validate_graph(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root must be a JSON object"]

    missing_root = sorted(REQUIRED_ROOT_KEYS - data.keys())
    extra_root = sorted(data.keys() - ROOT_KEYS)
    if missing_root:
        errors.append(f"root missing keys: {', '.join(missing_root)}")
    if extra_root:
        errors.append(f"root has unsupported keys: {', '.join(extra_root)}")
    if data.get("version") != 1:
        errors.append("version must be 1")
    if not nonempty_string(data.get("taskId")):
        errors.append("taskId must be a non-empty string")
    if not nonempty_string(data.get("goal")):
        errors.append("goal must be a non-empty string")
    if data.get("mode") not in MODES:
        errors.append(f"mode must be one of: {', '.join(sorted(MODES))}")
    if not string_list(data.get("acceptanceCriteria"), nonempty=True):
        errors.append("acceptanceCriteria must contain non-empty strings")
    if "assumptions" in data and not string_list(data.get("assumptions")):
        errors.append("assumptions must be an array of non-empty strings")

    nodes = data.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("nodes must be a non-empty array")
        return errors

    ids: list[str] = []
    in_progress = 0
    for index, node in enumerate(nodes):
        label = f"nodes[{index}]"
        if not isinstance(node, dict):
            errors.append(f"{label} must be an object")
            continue

        missing = sorted(REQUIRED_NODE_KEYS - node.keys())
        extra = sorted(node.keys() - NODE_KEYS)
        if missing:
            errors.append(f"{label} missing keys: {', '.join(missing)}")
        if extra:
            errors.append(f"{label} has unsupported keys: {', '.join(extra)}")

        node_id = node.get("id")
        if not nonempty_string(node_id) or not ID_PATTERN.fullmatch(node_id):
            errors.append(f"{label}.id must use lowercase letters, digits, and hyphens")
        else:
            ids.append(node_id)

        for key in ("title", "goal"):
            if not nonempty_string(node.get(key)):
                errors.append(f"{label}.{key} must be a non-empty string")
        if node.get("kind") not in KINDS:
            errors.append(f"{label}.kind is invalid")
        if node.get("risk") not in RISKS:
            errors.append(f"{label}.risk is invalid")
        if node.get("status") not in STATUSES:
            errors.append(f"{label}.status is invalid")
        if node.get("status") == "in_progress":
            in_progress += 1
        attempts = node.get("attempts")
        if not isinstance(attempts, int) or isinstance(attempts, bool) or not 0 <= attempts <= 3:
            errors.append(f"{label}.attempts must be an integer from 0 to 3")

        for key in ("dependencies", "inputs", "evidence"):
            if not string_list(node.get(key)):
                errors.append(f"{label}.{key} must be an array of non-empty strings")
        for key in ("outputs", "acceptance", "checks"):
            if not string_list(node.get(key), nonempty=True):
                errors.append(f"{label}.{key} must contain non-empty strings")

        dependencies = node.get("dependencies")
        if string_list(dependencies) and len(dependencies) != len(set(dependencies)):
            errors.append(f"{label}.dependencies must be unique")
        if node.get("status") == "verified" and not node.get("evidence"):
            errors.append(f"{label} is verified but has no evidence")
        if node.get("status") == "blocked" and not nonempty_string(node.get("blocker")):
            errors.append(f"{label} is blocked but has no blocker")

    if len(ids) != len(set(ids)):
        errors.append("node ids must be unique")
    if in_progress > 1:
        errors.append("at most one node may be in_progress")

    id_set = set(ids)
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in id_set}
    for node in nodes:
        if not isinstance(node, dict) or node.get("id") not in id_set:
            continue
        node_id = node["id"]
        dependencies = node.get("dependencies")
        if not string_list(dependencies):
            continue
        for dependency in dependencies:
            if dependency == node_id:
                errors.append(f"node {node_id} depends on itself")
            elif dependency not in id_set:
                errors.append(f"node {node_id} depends on unknown node {dependency}")
            else:
                adjacency[node_id].append(dependency)

    state: dict[str, int] = {node_id: 0 for node_id in id_set}

    def visit(node_id: str, trail: list[str]) -> None:
        if state[node_id] == 1:
            start = trail.index(node_id) if node_id in trail else 0
            errors.append("dependency cycle: " + " -> ".join(trail[start:] + [node_id]))
            return
        if state[node_id] == 2:
            return
        state[node_id] = 1
        for dependency in adjacency[node_id]:
            visit(dependency, trail + [node_id])
        state[node_id] = 2

    for node_id in sorted(id_set):
        if state[node_id] == 0:
            visit(node_id, [])

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_work_graph.py <graph.json>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read valid JSON from {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate_graph(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"VALID: {path} contains {len(data['nodes'])} node(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
