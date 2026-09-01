#!/usr/bin/env python3
"""Validate Exam Hacker strategy schema v2 plus loop contract v1."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUBJECT_TYPES = {"math_logic", "memorization", "mixed"}
PRIORITY_LEVELS = {"must_win", "high_frequency", "supporting", "abandonable"}
NODE_TYPES = {"concept", "formula", "theorem", "method", "boundary_condition", "scoring_routine"}
NODE_MASTERY = {"must_know", "high_frequency", "abandonable", "supporting"}
EDGE_RELATIONS = {
    "causality", "derivation", "substitution", "boundary_constraint",
    "formula_chain", "unit_conversion", "graph_relation", "approximation_assumption",
}
MATERIAL_KINDS = {
    "textbook", "lecture", "review_sheet", "past_paper", "homework",
    "example", "answer_key", "teacher_hint", "user_notes", "other",
}
DOCUMENT_MODES = {"text", "mixed", "scan-likely", "no-readable-signal"}
INSPECTION_METHODS = {"embedded_text", "vision", "hybrid"}
INSPECTION_COVERAGE = {"targeted", "full"}
OCR_ROLES = {"none", "index_only"}
PAGE_LOCATOR_RE = re.compile(r"\bpp?\.\s*(\d+)(?:\s*[-\u2013\u2014]\s*(\d+))?", re.IGNORECASE)
SLIDE_LOCATOR_RE = re.compile(r"\bslide\s+(\d+)\b", re.IGNORECASE)
SESSION_KINDS = {"study", "drill", "micro_probe"}
SESSION_STATES = {"active", "queued", "completed", "superseded"}
EVIDENCE_TYPES = {"drill", "graded_work", "micro_probe", "session_receipt", "self_report", "user_report", "unknown"}
CONFIDENCE_LEVELS = {"high", "medium", "low", "unknown"}
OUTPUT_TYPES = {
    "practice_evidence", "concept_compression", "solution_chain", "paper_deconstruction", "error_sop",
    "formula_sheet", "knowledge_map", "a4_sheet", "other",
}


class ValidationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def obj(value: Any, path: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{path} must be an object")
    return value


def arr(value: Any, path: str) -> list[Any]:
    require(isinstance(value, list), f"{path} must be an array")
    return value


def text(value: Any, path: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{path} must be non-empty text")
    return value.strip()


def stable_id(value: Any, path: str) -> str:
    value = text(value, path)
    require(bool(ID_RE.fullmatch(value)), f"{path} must be stable kebab-case")
    return value


def timestamp(value: Any, path: str) -> datetime:
    raw = text(value, path)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{path} must be ISO 8601") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None, f"{path} must include UTC offset")
    return parsed


def unique(items: list[Any], path: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(items):
        item = obj(raw, f"{path}[{index}]")
        identifier = stable_id(item.get("id"), f"{path}[{index}].id")
        require(identifier not in result, f"duplicate ID {identifier!r} in {path}")
        result[identifier] = item
    return result


def no_days_left(value: Any, path: str = "strategy") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(key != "days_left", f"{path}.{key} is forbidden; use planning_context.exam_date")
            no_days_left(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            no_days_left(child, f"{path}[{index}]")


def validate_relative_path(raw: Any, path: str, course_root: Path | None, must_exist: bool) -> None:
    if raw is None:
        return
    relative = Path(text(raw, path))
    require(not relative.is_absolute(), f"{path} must be relative to course root")
    require(".." not in relative.parts, f"{path} may not escape course root")
    if course_root is not None and must_exist:
        resolved = (course_root / relative).resolve()
        require(course_root == resolved or course_root in resolved.parents, f"{path} escapes course root")
        require(resolved.exists(), f"{path} does not exist: {relative}")


def validate_inspection(raw: Any, path: str) -> dict[str, Any] | None:
    if raw is None:
        return None
    inspection = obj(raw, path)
    require(inspection.get("document_mode") in DOCUMENT_MODES, f"{path}.document_mode is invalid")
    method = inspection.get("method")
    require(method in INSPECTION_METHODS, f"{path}.method is invalid")
    pages_total = inspection.get("pages_total")
    require(
        isinstance(pages_total, int) and not isinstance(pages_total, bool) and pages_total > 0,
        f"{path}.pages_total must be a positive integer",
    )
    coverage = inspection.get("coverage")
    require(coverage in INSPECTION_COVERAGE, f"{path}.coverage is invalid")
    pages = arr(inspection.get("pages_inspected"), f"{path}.pages_inspected")
    require(
        all(isinstance(page, int) and not isinstance(page, bool) and 1 <= page <= pages_total for page in pages),
        f"{path}.pages_inspected contains an invalid page",
    )
    require(len(pages) == len(set(pages)), f"{path}.pages_inspected contains duplicates")
    require(pages == sorted(pages), f"{path}.pages_inspected must be sorted")
    require(inspection.get("ocr_role") in OCR_ROLES, f"{path}.ocr_role is invalid")
    if method in {"vision", "hybrid"}:
        require(bool(pages), f"{path}.pages_inspected must not be empty for visual inspection")
    if inspection.get("document_mode") == "scan-likely":
        require(method in {"vision", "hybrid"}, f"{path}.scan-likely material requires vision or hybrid inspection")
    if coverage == "full":
        require(pages == list(range(1, pages_total + 1)), f"{path}.full coverage requires every page")
    return inspection


def locator_pages(locator: str) -> set[int]:
    pages: set[int] = set()
    for match in PAGE_LOCATOR_RE.finditer(locator):
        start = int(match.group(1))
        end = int(match.group(2) or start)
        if end < start:
            start, end = end, start
        pages.update(range(start, end + 1))
    pages.update(int(match.group(1)) for match in SLIDE_LOCATOR_RE.finditer(locator))
    return pages


def validate_evidence_refs(raw_refs: Any, path: str, materials: dict[str, dict[str, Any]], required: bool = True) -> None:
    refs = arr(raw_refs, path)
    if required:
        require(bool(refs), f"{path} must not be empty")
    for index, raw in enumerate(refs):
        ref = obj(raw, f"{path}[{index}]")
        material_id = stable_id(ref.get("material_id"), f"{path}[{index}].material_id")
        require(material_id in materials, f"{path}[{index}] references unknown material {material_id!r}")
        locator = text(ref.get("locator"), f"{path}[{index}].locator")
        text(ref.get("claim"), f"{path}[{index}].claim")
        inspection = materials[material_id].get("inspection")
        if isinstance(inspection, dict) and inspection.get("method") in {"vision", "hybrid"}:
            referenced_pages = locator_pages(locator)
            require(bool(referenced_pages), f"{path}[{index}].locator needs a page or slide anchor for visual evidence")
            inspected_pages = set(inspection.get("pages_inspected", []))
            require(
                referenced_pages.issubset(inspected_pages),
                f"{path}[{index}] references a page not listed in {material_id!r} inspection",
            )


def validate_strategy(data: Any, course_root: Path | None) -> dict[str, Any]:
    strategy = obj(data, "strategy")
    require(strategy.get("schema_version") == 2, "schema_version must equal 2")
    no_days_left(strategy)

    course = obj(strategy.get("course"), "course")
    stable_id(course.get("id"), "course.id")
    text(course.get("name"), "course.name")
    require(course.get("language") in {"zh", "en"}, "course.language must be zh or en")
    require(course.get("subject_type") in SUBJECT_TYPES, "course.subject_type is invalid")
    score = course.get("target_score")
    require(isinstance(score, (int, float)) and not isinstance(score, bool) and 0 <= score <= 100, "course.target_score must be 0-100")

    context = obj(strategy.get("planning_context"), "planning_context")
    try:
        date.fromisoformat(text(context.get("exam_date"), "planning_context.exam_date"))
    except ValueError as exc:
        raise ValidationError("planning_context.exam_date must use YYYY-MM-DD") from exc
    timestamp(context.get("strategy_created_at"), "planning_context.strategy_created_at")
    text(context.get("timezone"), "planning_context.timezone")
    require(context.get("exam_date_source") in {"user_confirmed", "derived_from_relative_days", "inferred"}, "planning_context.exam_date_source is invalid")
    availability = obj(context.get("availability"), "planning_context.availability")
    hours = availability.get("hours_per_day")
    total_minutes = availability.get("total_minutes")
    require(isinstance(hours, (int, float)) and not isinstance(hours, bool) and 0 < hours <= 20, "availability.hours_per_day must be >0 and <=20")
    require(isinstance(total_minutes, int) and total_minutes > 0, "availability.total_minutes must be a positive integer")
    require(availability.get("source") in {"user_confirmed", "inferred"}, "availability.source is invalid")

    outline = obj(strategy.get("source_outline"), "source_outline")
    text(outline.get("label"), "source_outline.label")
    validate_relative_path(outline.get("path"), "source_outline.path", course_root, must_exist=course_root is not None)

    materials = unique(arr(strategy.get("source_materials"), "source_materials"), "source_materials")
    for material_id, material in materials.items():
        text(material.get("label"), f"source_materials[{material_id}].label")
        require(material.get("kind") in MATERIAL_KINDS, f"source_materials[{material_id}].kind is invalid")
        require(material.get("provenance") in {"user_provided", "pre_existing"}, f"source_materials[{material_id}].provenance is invalid")
        require(material.get("availability") == "available", f"source_materials[{material_id}].availability must be available")
        require(material.get("readability") == "verified", f"source_materials[{material_id}].readability must be verified")
        validate_relative_path(material.get("path"), f"source_materials[{material_id}].path", course_root, must_exist=course_root is not None)
        validate_inspection(material.get("inspection"), f"source_materials[{material_id}].inspection")

    graph = obj(strategy.get("knowledge_graph"), "knowledge_graph")
    nodes = unique(arr(graph.get("nodes"), "knowledge_graph.nodes"), "knowledge_graph.nodes")
    for node_id, node in nodes.items():
        text(node.get("label"), f"knowledge_graph.nodes[{node_id}].label")
        require(node.get("type") in NODE_TYPES, f"knowledge_graph.nodes[{node_id}].type is invalid")
        require(node.get("mastery") in NODE_MASTERY, f"knowledge_graph.nodes[{node_id}].mastery is invalid")
        validate_evidence_refs(node.get("source_refs"), f"knowledge_graph.nodes[{node_id}].source_refs", materials)

    for index, raw in enumerate(arr(graph.get("edges"), "knowledge_graph.edges")):
        edge = obj(raw, f"knowledge_graph.edges[{index}]")
        require(edge.get("from") in nodes and edge.get("to") in nodes, f"knowledge_graph.edges[{index}] has unknown node")
        require(edge.get("relation") in EDGE_RELATIONS, f"knowledge_graph.edges[{index}].relation is invalid")

    priorities = unique(arr(strategy.get("priorities"), "priorities"), "priorities")
    for priority_id, priority in priorities.items():
        require(isinstance(priority.get("rank"), int) and priority["rank"] >= 1, f"priorities[{priority_id}].rank is invalid")
        text(priority.get("title"), f"priorities[{priority_id}].title")
        require(priority.get("level") in PRIORITY_LEVELS, f"priorities[{priority_id}].level is invalid")
        text(priority.get("reason"), f"priorities[{priority_id}].reason")
        for node_id in arr(priority.get("knowledge_node_ids"), f"priorities[{priority_id}].knowledge_node_ids"):
            require(node_id in nodes, f"priority {priority_id!r} references unknown node {node_id!r}")
        validate_evidence_refs(priority.get("evidence_refs"), f"priorities[{priority_id}].evidence_refs", materials)

    snapshots = arr(strategy.get("mastery_snapshot"), "mastery_snapshot")
    snapshot_topics: set[str] = set()
    for index, raw in enumerate(snapshots):
        item = obj(raw, f"mastery_snapshot[{index}]")
        topic_id = stable_id(item.get("topic_id"), f"mastery_snapshot[{index}].topic_id")
        require(topic_id in nodes, f"mastery_snapshot[{index}] references unknown topic {topic_id!r}")
        require(topic_id not in snapshot_topics, f"duplicate mastery snapshot for {topic_id!r}")
        snapshot_topics.add(topic_id)
        level = item.get("level")
        require(level is None or (isinstance(level, int) and not isinstance(level, bool) and 0 <= level <= 3), f"mastery_snapshot[{index}].level must be 0-3 or null")
        require(item.get("evidence_type") in EVIDENCE_TYPES, f"mastery_snapshot[{index}].evidence_type is invalid")
        require(item.get("confidence") in CONFIDENCE_LEVELS, f"mastery_snapshot[{index}].confidence is invalid")
        text(item.get("evidence_ref"), f"mastery_snapshot[{index}].evidence_ref")
        timestamp(item.get("observed_at"), f"mastery_snapshot[{index}].observed_at")

    sessions = unique(arr(strategy.get("action_list"), "action_list"), "action_list")
    loop = obj(strategy.get("loop_state"), "loop_state")
    require(loop.get("contract_version") == "exam-hacker-loop/v1", "loop_state.contract_version is invalid")
    revision = loop.get("strategy_revision")
    require(isinstance(revision, int) and revision >= 1, "loop_state.strategy_revision must be >=1")
    require(loop.get("status") in {"active", "complete", "blocked"}, "loop_state.status is invalid")
    timestamp(loop.get("updated_at"), "loop_state.updated_at")
    cursor = loop.get("last_evidence_event_id")
    require(cursor is None or bool(ID_RE.fullmatch(text(cursor, "loop_state.last_evidence_event_id"))), "last_evidence_event_id must be null or stable kebab-case")
    if revision == 1:
        require(1 <= len(sessions) <= 3, "revision 1 must contain one to three Sessions")

    session_minutes = 0
    for session_id, session in sessions.items():
        for forbidden in ("steps", "guide", "source_refs"):
            require(forbidden not in session, f"action_list[{session_id}].{forbidden} is forbidden")
        require(session.get("kind") in SESSION_KINDS, f"action_list[{session_id}].kind is invalid")
        require(session.get("state") in SESSION_STATES, f"action_list[{session_id}].state is invalid")
        for field in ("phase", "title", "objective", "success_criteria"):
            text(session.get(field), f"action_list[{session_id}].{field}")
        duration = session.get("duration_minutes")
        require(isinstance(duration, int) and 5 <= duration <= 1200, f"action_list[{session_id}].duration_minutes must be 5-1200")
        if session.get("state") != "superseded":
            session_minutes += duration
        require(session.get("priority_id") in priorities, f"action_list[{session_id}] references unknown priority")
        for node_id in arr(session.get("knowledge_node_ids"), f"action_list[{session_id}].knowledge_node_ids"):
            require(node_id in nodes, f"action_list[{session_id}] references unknown topic {node_id!r}")
        for dependency_id in arr(session.get("depends_on"), f"action_list[{session_id}].depends_on"):
            require(dependency_id in sessions, f"action_list[{session_id}] depends on unknown Session {dependency_id!r}")
        for material_id in arr(session.get("input_material_ids"), f"action_list[{session_id}].input_material_ids"):
            require(material_id in materials, f"action_list[{session_id}] references unknown material {material_id!r}")
        arr(session.get("input_artifact_ids"), f"action_list[{session_id}].input_artifact_ids")
        for output_index, raw_output in enumerate(arr(session.get("expected_outputs"), f"action_list[{session_id}].expected_outputs")):
            output = obj(raw_output, f"action_list[{session_id}].expected_outputs[{output_index}]")
            stable_id(output.get("id"), f"action_list[{session_id}].expected_outputs[{output_index}].id")
            text(output.get("label"), f"action_list[{session_id}].expected_outputs[{output_index}].label")
            require(output.get("type") in OUTPUT_TYPES, f"action_list[{session_id}] output type is invalid")
            require(output.get("status") in {"planned", "available"}, f"action_list[{session_id}] output status is invalid")
            if output.get("status") == "available":
                require(bool(output.get("path") or output.get("href")), f"available output in {session_id!r} needs path or href")

    next_ids = arr(loop.get("next_session_ids"), "loop_state.next_session_ids")
    require(1 <= len(next_ids) <= 3 or loop.get("status") == "complete", "active loop needs one to three next_session_ids")
    require(len(next_ids) == len(set(next_ids)), "loop_state.next_session_ids contains duplicates")
    for session_id in next_ids:
        require(session_id in sessions, f"next_session_ids references unknown Session {session_id!r}")
        require(sessions[session_id].get("state") in {"active", "queued"}, f"next Session {session_id!r} is not executable")

    capacity = obj(strategy.get("capacity_summary"), "capacity_summary")
    require(capacity.get("available_minutes_at_generation") == total_minutes, "available capacity does not match availability.total_minutes")
    require(capacity.get("session_minutes") == session_minutes, "capacity_summary.session_minutes is inconsistent")
    require(capacity.get("deficit_minutes") == max(0, session_minutes - total_minutes), "capacity_summary.deficit_minutes is inconsistent")

    for index, raw in enumerate(arr(strategy.get("abandon"), "abandon")):
        item = obj(raw, f"abandon[{index}]")
        require(item.get("topic_id") in nodes, f"abandon[{index}] references unknown topic")
        require(item.get("decision") == "strategic_abandonment", f"abandon[{index}].decision is invalid")
        validate_evidence_refs(item.get("evidence_refs"), f"abandon[{index}].evidence_refs", materials)
        for field in ("capacity_reason", "risk_if_wrong", "reversal_condition"):
            text(item.get(field), f"abandon[{index}].{field}")
        require(isinstance(item.get("user_accepted_evidence_gap"), bool), f"abandon[{index}].user_accepted_evidence_gap must be boolean")

    gaps = unique(arr(strategy.get("material_gaps"), "material_gaps"), "material_gaps")
    for gap_id, gap in gaps.items():
        text(gap.get("description"), f"material_gaps[{gap_id}].description")
        text(gap.get("impact"), f"material_gaps[{gap_id}].impact")

    revisions = arr(strategy.get("revision_log"), "revision_log")
    require(bool(revisions), "revision_log must not be empty")
    seen_revisions: set[int] = set()
    for index, raw in enumerate(revisions):
        item = obj(raw, f"revision_log[{index}]")
        number = item.get("revision")
        require(isinstance(number, int) and number >= 1 and number not in seen_revisions, f"revision_log[{index}].revision is invalid")
        seen_revisions.add(number)
        timestamp(item.get("updated_at"), f"revision_log[{index}].updated_at")
        text(item.get("reason"), f"revision_log[{index}].reason")
        arr(item.get("consumed_event_ids"), f"revision_log[{index}].consumed_event_ids")
        arr(item.get("changes"), f"revision_log[{index}].changes")
    require(max(seen_revisions) == revision, "revision_log does not reach loop_state.strategy_revision")
    require(revision == 1 or set(range(1, revision + 1)).issubset(seen_revisions), "revision_log has a revision gap")
    return strategy


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Exam Hacker strategy and loop state")
    parser.add_argument("strategy", help="Path to strategy.json")
    parser.add_argument("--course-root", help="Optional course root for path existence checks")
    args = parser.parse_args()
    try:
        strategy_path = Path(args.strategy).resolve()
        course_root = Path(args.course_root).resolve() if args.course_root else None
        data = json.loads(strategy_path.read_text(encoding="utf-8"))
        strategy = validate_strategy(data, course_root)
    except (OSError, json.JSONDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(
        "VALID: "
        f"course={strategy['course']['id']} "
        f"revision={strategy['loop_state']['strategy_revision']} "
        f"sessions={len(strategy['action_list'])} "
        f"materials={len(strategy['source_materials'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
