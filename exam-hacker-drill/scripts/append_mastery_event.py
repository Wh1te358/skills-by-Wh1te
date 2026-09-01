#!/usr/bin/env python3
"""Validate and append one Exam Hacker mastery-evidence event."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EVIDENCE_TYPES = {"drill", "micro_probe", "graded_work", "session_receipt", "user_report"}


class EventError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise EventError(message)


def text(value: Any, path: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{path} must be non-empty text")
    return value.strip()


def stable_id(value: Any, path: str) -> str:
    value = text(value, path)
    require(bool(ID_RE.fullmatch(value)), f"{path} must be stable kebab-case")
    return value


def timestamp(value: Any, path: str) -> None:
    raw = text(value, path)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EventError(f"{path} must be ISO 8601") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, f"{path} must include UTC offset")


def load_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise EventError(f"existing log line {number} is invalid JSON") from exc
        require(isinstance(event, dict), f"existing log line {number} must be an object")
        events.append(event)
    return events


def validate_event(event: Any, strategy: Any, existing: list[dict[str, Any]]) -> dict[str, Any]:
    require(isinstance(event, dict), "event must be an object")
    require(isinstance(strategy, dict), "strategy must be an object")
    require(event.get("contract_version") == "exam-hacker-loop/v1", "event contract_version is invalid")
    event_id = stable_id(event.get("event_id"), "event.event_id")
    existing_ids = {stable_id(item.get("event_id"), "existing.event_id") for item in existing}
    require(event_id not in existing_ids, f"duplicate event_id {event_id!r}")

    course = strategy.get("course")
    require(isinstance(course, dict), "strategy.course must be an object")
    course_id = stable_id(event.get("course_id"), "event.course_id")
    require(course_id == course.get("id"), "event.course_id does not match strategy")

    loop = strategy.get("loop_state")
    require(isinstance(loop, dict), "strategy.loop_state must be an object")
    revision = event.get("strategy_revision_observed")
    require(isinstance(revision, int) and revision >= 1, "strategy_revision_observed must be >=1")
    require(revision == loop.get("strategy_revision"), "event revision does not match current strategy")
    timestamp(event.get("observed_at"), "event.observed_at")
    require(event.get("source_skill") in {"exam-hacker-drill", "exam-hacker-replan"}, "event.source_skill is invalid")

    sessions_raw = strategy.get("action_list")
    require(isinstance(sessions_raw, list), "strategy.action_list must be an array")
    sessions = {stable_id(item.get("id"), "session.id"): item for item in sessions_raw if isinstance(item, dict)}
    session_id = stable_id(event.get("session_id"), "event.session_id")
    require(session_id in sessions, f"event references unknown Session {session_id!r}")

    nodes_raw = strategy.get("knowledge_graph", {}).get("nodes")
    require(isinstance(nodes_raw, list), "strategy.knowledge_graph.nodes must be an array")
    node_ids = {stable_id(item.get("id"), "node.id") for item in nodes_raw if isinstance(item, dict)}
    topic_id = stable_id(event.get("topic_id"), "event.topic_id")
    require(topic_id in node_ids, f"event references unknown topic {topic_id!r}")
    require(topic_id in sessions[session_id].get("knowledge_node_ids", []), "event topic is not part of the Session")
    require(event.get("evidence_type") in EVIDENCE_TYPES, "event.evidence_type is invalid")

    result = event.get("result")
    require(isinstance(result, dict), "event.result must be an object")
    require(isinstance(result.get("success"), bool), "event.result.success must be boolean")
    level = result.get("level_observed")
    require(isinstance(level, int) and not isinstance(level, bool) and 0 <= level <= 3, "level_observed must be 0-3")
    earned = result.get("score_earned")
    possible = result.get("score_possible")
    if earned is not None or possible is not None:
        require(isinstance(earned, (int, float)) and not isinstance(earned, bool) and earned >= 0, "score_earned is invalid")
        require(isinstance(possible, (int, float)) and not isinstance(possible, bool) and possible > 0, "score_possible is invalid")
        require(earned <= possible, "score_earned cannot exceed score_possible")
    tags = result.get("error_tags")
    require(isinstance(tags, list), "event.result.error_tags must be an array")
    for index, tag in enumerate(tags):
        stable_id(tag, f"event.result.error_tags[{index}]")
    text(result.get("notes"), "event.result.notes")

    refs = event.get("source_refs")
    require(isinstance(refs, list) and bool(refs), "event.source_refs must be a non-empty array")
    material_ids = {item.get("id") for item in strategy.get("source_materials", []) if isinstance(item, dict)}
    for index, ref in enumerate(refs):
        require(isinstance(ref, dict), f"event.source_refs[{index}] must be an object")
        require(stable_id(ref.get("material_id"), f"event.source_refs[{index}].material_id") in material_ids, f"event.source_refs[{index}] has unknown material")
        text(ref.get("locator"), f"event.source_refs[{index}].locator")
        text(ref.get("claim"), f"event.source_refs[{index}].claim")

    supersedes = event.get("supersedes_event_id")
    if supersedes is not None:
        supersedes = stable_id(supersedes, "event.supersedes_event_id")
        require(supersedes in existing_ids, "supersedes_event_id is unknown")
    return event


def main() -> int:
    parser = argparse.ArgumentParser(description="Append one validated mastery event")
    parser.add_argument("log", help="Path to mastery-evidence.jsonl")
    parser.add_argument("event", help="Path to one event JSON object")
    parser.add_argument("--strategy", required=True, help="Path to strategy.json")
    parser.add_argument("--dry-run", action="store_true", help="Validate without appending")
    args = parser.parse_args()
    try:
        log_path = Path(args.log)
        event = json.loads(Path(args.event).read_text(encoding="utf-8"))
        strategy = json.loads(Path(args.strategy).read_text(encoding="utf-8"))
        existing = load_log(log_path)
        validated = validate_event(event, strategy, existing)
        if not args.dry_run:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(validated, ensure_ascii=False, separators=(",", ":")) + "\n")
    except (OSError, json.JSONDecodeError, EventError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    action = "VALID" if args.dry_run else "APPENDED"
    print(f"{action}: event={validated['event_id']} log={log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
