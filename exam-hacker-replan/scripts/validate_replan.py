#!/usr/bin/env python3
"""Validate one Exam Hacker strategy revision transition."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ReplanError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplanError(message)


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path} must contain an object")
    return data


def load_events(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    events: list[dict[str, Any]] = []
    ids: set[str] = set()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReplanError(f"evidence log line {number} is invalid JSON") from exc
        require(isinstance(event, dict), f"evidence log line {number} must be an object")
        event_id = event.get("event_id")
        require(isinstance(event_id, str) and bool(ID_RE.fullmatch(event_id)), f"evidence log line {number} has invalid event_id")
        require(event_id not in ids, f"duplicate evidence event {event_id!r}")
        ids.add(event_id)
        events.append(event)
    return events


def event_ids_after(events: list[dict[str, Any]], cursor: Any) -> list[str]:
    ids = [event["event_id"] for event in events]
    if cursor is None:
        return ids
    require(cursor in ids, f"prior evidence cursor {cursor!r} is absent from the log")
    return ids[ids.index(cursor) + 1 :]


def find_triage_validator() -> Path:
    repo_or_skills_root = Path(__file__).resolve().parents[2]
    validator = repo_or_skills_root / "exam-hacker-triage" / "scripts" / "validate_strategy.py"
    require(validator.is_file(), f"required triage validator is missing: {validator}")
    return validator


def run_full_validator(validator: Path, strategy: Path, course_root: Path | None) -> None:
    command = [sys.executable, str(validator), str(strategy)]
    if course_root is not None:
        command.extend(["--course-root", str(course_root)])
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    detail = result.stderr.strip() or result.stdout.strip()
    require(result.returncode == 0, f"full strategy validation failed: {detail}")


def session_index(strategy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sessions = strategy.get("action_list")
    require(isinstance(sessions, list), "action_list must be an array")
    result: dict[str, dict[str, Any]] = {}
    for item in sessions:
        require(isinstance(item, dict) and isinstance(item.get("id"), str), "every Session needs an ID")
        result[item["id"]] = item
    return result


def priority_basis(strategy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    priorities = strategy.get("priorities")
    require(isinstance(priorities, list), "priorities must be an array")
    result: dict[str, dict[str, Any]] = {}
    for item in priorities:
        require(isinstance(item, dict) and isinstance(item.get("id"), str), "every priority needs an ID")
        result[item["id"]] = {
            "knowledge_node_ids": item.get("knowledge_node_ids"),
            "evidence_refs": item.get("evidence_refs"),
        }
    return result


def validate_transition(before: dict[str, Any], after: dict[str, Any], events: list[dict[str, Any]]) -> None:
    require(before.get("schema_version") == after.get("schema_version"), "schema_version changed")
    require(before.get("course") == after.get("course"), "course facts changed during replan")
    require(before.get("source_outline") == after.get("source_outline"), "source_outline changed during replan")
    require(before.get("source_materials") == after.get("source_materials"), "source_materials changed during replan")
    require(before.get("knowledge_graph") == after.get("knowledge_graph"), "knowledge_graph changed during replan")
    require(priority_basis(before) == priority_basis(after), "priority evidence basis changed during replan")

    before_loop = before.get("loop_state")
    after_loop = after.get("loop_state")
    require(isinstance(before_loop, dict) and isinstance(after_loop, dict), "both strategies need loop_state")
    before_revision = before_loop.get("strategy_revision")
    after_revision = after_loop.get("strategy_revision")
    require(isinstance(before_revision, int) and after_revision == before_revision + 1, "strategy revision must increment by exactly one")

    before_log = before.get("revision_log")
    after_log = after.get("revision_log")
    require(isinstance(before_log, list) and isinstance(after_log, list), "revision_log must be an array")
    require(len(after_log) == len(before_log) + 1, "exactly one revision_log entry must be appended")
    require(after_log[:-1] == before_log, "prior revision_log entries changed")
    entry = after_log[-1]
    require(isinstance(entry, dict) and entry.get("revision") == after_revision, "new revision_log entry does not match revision")
    consumed = entry.get("consumed_event_ids")
    require(isinstance(consumed, list), "consumed_event_ids must be an array")
    require(
        all(isinstance(event_id, str) and bool(ID_RE.fullmatch(event_id)) for event_id in consumed),
        "consumed_event_ids must contain stable event IDs",
    )
    require(len(consumed) == len(set(consumed)), "consumed_event_ids must be unique")

    new_ids = event_ids_after(events, before_loop.get("last_evidence_event_id"))
    event_index = {event["event_id"]: event for event in events}
    before_sessions = session_index(before)
    topics = {
        item.get("id")
        for item in before.get("knowledge_graph", {}).get("nodes", [])
        if isinstance(item, dict)
    }
    for event_id in new_ids:
        event = event_index[event_id]
        require(event.get("contract_version") == "exam-hacker-loop/v1", f"event {event_id!r} has an invalid contract")
        require(event.get("course_id") == before["course"]["id"], f"event {event_id!r} belongs to another course")
        observed_revision = event.get("strategy_revision_observed")
        require(
            isinstance(observed_revision, int) and 1 <= observed_revision <= before_revision,
            f"event {event_id!r} has an invalid observed revision",
        )
        require(event.get("session_id") in before_sessions, f"event {event_id!r} references an unknown Session")
        require(event.get("topic_id") in topics, f"event {event_id!r} references an unknown topic")

    availability_changed = before.get("planning_context", {}).get("availability") != after.get("planning_context", {}).get("availability")
    require(bool(consumed) or availability_changed, "revision has neither consumed evidence nor an availability change")
    require(consumed == new_ids[: len(consumed)], "consumed evidence must be the ordered prefix after the cursor")
    expected_cursor = consumed[-1] if consumed else before_loop.get("last_evidence_event_id")
    require(after_loop.get("last_evidence_event_id") == expected_cursor, "evidence cursor does not match consumed events")

    after_sessions = session_index(after)
    for session_id, session in before_sessions.items():
        if session.get("state") == "completed":
            require(session_id in after_sessions, f"completed Session {session_id!r} was deleted")
            require(after_sessions[session_id].get("state") == "completed", f"completed Session {session_id!r} was reopened")
    next_ids = after_loop.get("next_session_ids")
    require(isinstance(next_ids, list), "after next_session_ids must be an array")
    if after_loop.get("status") != "complete":
        require(1 <= len(next_ids) <= 3, "active revision needs one to three next Sessions")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate one Exam Hacker replan transition")
    parser.add_argument("before", help="Current strategy.json")
    parser.add_argument("after", help="Candidate strategy.next.json")
    parser.add_argument("--evidence-log", help="Optional mastery-evidence.jsonl")
    parser.add_argument("--course-root", help="Optional course root for path checks")
    args = parser.parse_args()
    try:
        before_path = Path(args.before).resolve()
        after_path = Path(args.after).resolve()
        course_root = Path(args.course_root).resolve() if args.course_root else None
        validator = find_triage_validator()
        run_full_validator(validator, before_path, course_root)
        run_full_validator(validator, after_path, course_root)
        before = load_json(before_path)
        after = load_json(after_path)
        events = load_events(Path(args.evidence_log).resolve() if args.evidence_log else None)
        validate_transition(before, after, events)
    except (OSError, json.JSONDecodeError, ReplanError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(
        "VALID REPLAN: "
        f"course={after['course']['id']} "
        f"revision={before['loop_state']['strategy_revision']}->{after['loop_state']['strategy_revision']} "
        f"cursor={after['loop_state']['last_evidence_event_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
