#!/usr/bin/env python3
"""Validate one Exam Hacker solved-problem artifact."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NODE_ROLES = {"given", "concept", "formula", "constraint", "operation", "checkpoint", "result"}
REF_ROLES = {"problem", "theory", "answer", "rubric"}
CHECK_TYPES = {
    "reference_match", "substitution", "dimensional", "equilibrium",
    "boundary", "limit", "independent_method", "logical_completion",
}
INDEPENDENT_CHECK_TYPES = CHECK_TYPES - {"reference_match"}


class ArtifactError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


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


def unique_objects(value: Any, path: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(arr(value, path)):
        item = obj(raw, f"{path}[{index}]")
        item_id = stable_id(item.get("id"), f"{path}[{index}].id")
        require(item_id not in result, f"duplicate ID {item_id!r} in {path}")
        result[item_id] = item
    return result


def validate_refs(value: Any, path: str, known_materials: set[str] | None) -> list[dict[str, Any]]:
    refs = arr(value, path)
    require(bool(refs), f"{path} must not be empty")
    result: list[dict[str, Any]] = []
    for index, raw in enumerate(refs):
        ref = obj(raw, f"{path}[{index}]")
        material_id = stable_id(ref.get("material_id"), f"{path}[{index}].material_id")
        if known_materials is not None:
            require(material_id in known_materials, f"{path}[{index}] references unknown material {material_id!r}")
        require(ref.get("role") in REF_ROLES, f"{path}[{index}].role is invalid")
        text(ref.get("locator"), f"{path}[{index}].locator")
        text(ref.get("claim"), f"{path}[{index}].claim")
        result.append(ref)
    return result


def relative_path(value: Any, path: str) -> Path:
    candidate = Path(text(value, path))
    require(not candidate.is_absolute(), f"{path} must be relative")
    require(".." not in candidate.parts, f"{path} may not escape course root")
    require(candidate.suffix.lower() == ".md", f"{path} must end in .md")
    return candidate


def strategy_binding(strategy: dict[str, Any], artifact: dict[str, Any]) -> tuple[set[str], set[str]]:
    course = obj(strategy.get("course"), "strategy.course")
    require(artifact.get("course_id") == course.get("id"), "artifact course_id does not match strategy")
    loop = obj(strategy.get("loop_state"), "strategy.loop_state")
    require(artifact.get("strategy_revision_observed") == loop.get("strategy_revision"), "artifact revision does not match strategy")
    materials = {
        item.get("id")
        for item in arr(strategy.get("source_materials"), "strategy.source_materials")
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    topics = {
        item.get("id")
        for item in arr(obj(strategy.get("knowledge_graph"), "strategy.knowledge_graph").get("nodes"), "strategy.knowledge_graph.nodes")
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    sessions = {
        item.get("id"): item
        for item in arr(strategy.get("action_list"), "strategy.action_list")
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    session_id = artifact.get("session_id")
    output_id = artifact.get("output_id")
    require(session_id in sessions, "artifact session_id does not resolve")
    outputs = {
        item.get("id"): item
        for item in arr(sessions[session_id].get("expected_outputs"), f"strategy Session {session_id}.expected_outputs")
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    require(output_id in outputs, "artifact output_id does not resolve")
    require(outputs[output_id].get("type") in {"solution_chain", "paper_deconstruction"}, "matching Strategy output is not a solution chain")
    problem_topics = set(artifact["problem"]["target_node_ids"])
    session_topics = set(arr(sessions[session_id].get("knowledge_node_ids"), f"strategy Session {session_id}.knowledge_node_ids"))
    require(problem_topics.issubset(session_topics), "problem topics are outside the bound Session")
    require(problem_topics.issubset(topics), "problem topics do not resolve in strategy")
    return materials, topics


def forbid_score_claims(value: Any, path: str = "artifact") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            require(key not in {"process_marks", "score_marks", "mastery_event"}, f"{path}.{key} is forbidden")
            forbid_score_claims(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            forbid_score_claims(child, f"{path}[{index}]")


def validate_artifact(data: Any, strategy: dict[str, Any] | None, course_root: Path | None) -> dict[str, Any]:
    artifact = obj(data, "artifact")
    forbid_score_claims(artifact)
    require(artifact.get("contract_version") == "exam-hacker-solve/v1", "contract_version is invalid")
    require(artifact.get("artifact_type") == "solved-problem-chain", "artifact_type is invalid")
    artifact_id = stable_id(artifact.get("artifact_id"), "artifact.artifact_id")
    stable_id(artifact.get("course_id"), "artifact.course_id")
    display_path = relative_path(artifact.get("display_path"), "artifact.display_path")
    require(artifact.get("answer_policy") == "full_solution", "answer_policy must be full_solution")
    require(artifact.get("practice_status") == "practice_only", "visible solution must be practice_only")

    for field in ("strategy_revision_observed", "session_id", "output_id"):
        value = artifact.get(field)
        if value is not None:
            if field == "strategy_revision_observed":
                require(isinstance(value, int) and value >= 1, f"artifact.{field} must be null or >=1")
            else:
                stable_id(value, f"artifact.{field}")

    problem = obj(artifact.get("problem"), "artifact.problem")
    stable_id(problem.get("id"), "artifact.problem.id")
    text(problem.get("statement"), "artifact.problem.statement")
    target_ids = [stable_id(item, "artifact.problem.target_node_ids[]") for item in arr(problem.get("target_node_ids"), "artifact.problem.target_node_ids")]
    require(bool(target_ids) and len(target_ids) == len(set(target_ids)), "problem target_node_ids must be a non-empty unique array")

    known_materials: set[str] | None = None
    known_topics: set[str] | None = None
    if strategy is not None:
        known_materials, known_topics = strategy_binding(strategy, artifact)
    else:
        require(
            artifact.get("strategy_revision_observed") is None
            and artifact.get("session_id") is None
            and artifact.get("output_id") is None,
            "standalone artifact binding fields must all be null",
        )
    problem_refs = validate_refs(problem.get("source_refs"), "artifact.problem.source_refs", known_materials)
    if known_topics is not None:
        require(set(target_ids).issubset(known_topics), "problem target nodes do not exist in strategy")

    nodes = unique_objects(artifact.get("nodes"), "artifact.nodes")
    require(bool(nodes), "artifact.nodes must not be empty")
    for node_id, node in nodes.items():
        text(node.get("label"), f"artifact.nodes[{node_id}].label")
        require(node.get("role") in NODE_ROLES, f"artifact.nodes[{node_id}].role is invalid")
        text(node.get("mathematical_meaning"), f"artifact.nodes[{node_id}].mathematical_meaning")
        validate_refs(node.get("source_refs"), f"artifact.nodes[{node_id}].source_refs", known_materials)

    initial_ids = [stable_id(item, "artifact.initial_node_ids[]") for item in arr(artifact.get("initial_node_ids"), "artifact.initial_node_ids")]
    require(bool(initial_ids) and len(initial_ids) == len(set(initial_ids)), "initial_node_ids must be a non-empty unique array")
    require(set(initial_ids).issubset(nodes), "initial_node_ids contains an unknown node")
    available = set(initial_ids)

    steps = unique_objects(artifact.get("steps"), "artifact.steps")
    require(bool(steps), "artifact.steps must not be empty")
    for step_id, step in steps.items():
        inputs = [stable_id(item, f"artifact.steps[{step_id}].input_node_ids[]") for item in arr(step.get("input_node_ids"), f"artifact.steps[{step_id}].input_node_ids")]
        outputs = [stable_id(item, f"artifact.steps[{step_id}].output_node_ids[]") for item in arr(step.get("output_node_ids"), f"artifact.steps[{step_id}].output_node_ids")]
        require(bool(inputs), f"artifact.steps[{step_id}] needs input nodes")
        require(bool(outputs), f"artifact.steps[{step_id}] needs output nodes")
        require(set(inputs).issubset(available), f"artifact.steps[{step_id}] uses a node not yet available")
        require(set(outputs).issubset(nodes), f"artifact.steps[{step_id}] outputs an unknown node")
        require(bool(set(outputs) - available), f"artifact.steps[{step_id}] produces no new node")
        for field in ("trigger", "operation", "equation_or_rule", "why", "check"):
            text(step.get(field), f"artifact.steps[{step_id}].{field}")
        validate_refs(step.get("source_refs"), f"artifact.steps[{step_id}].source_refs", known_materials)
        available.update(outputs)

    endpoint = obj(artifact.get("endpoint"), "artifact.endpoint")
    endpoint_id = stable_id(endpoint.get("node_id"), "artifact.endpoint.node_id")
    endpoint_statement = text(endpoint.get("statement"), "artifact.endpoint.statement")
    final_answer = text(endpoint.get("final_answer"), "artifact.endpoint.final_answer")
    text(endpoint.get("units"), "artifact.endpoint.units")
    text(endpoint.get("acceptance_condition"), "artifact.endpoint.acceptance_condition")
    require(endpoint_id in available, "endpoint node is not produced by the ordered chain")
    require(endpoint_id in nodes, "endpoint node is unknown")

    checks = unique_objects(artifact.get("verification_checks"), "artifact.verification_checks")
    require(bool(checks), "verification_checks must not be empty")
    check_types: set[str] = set()
    for check_id, check in checks.items():
        check_type = check.get("type")
        require(check_type in CHECK_TYPES, f"verification_checks[{check_id}].type is invalid")
        check_types.add(check_type)
        text(check.get("procedure"), f"verification_checks[{check_id}].procedure")
        text(check.get("observed_result"), f"verification_checks[{check_id}].observed_result")
        require(check.get("passed") is True, f"verification_checks[{check_id}] did not pass")

    status = artifact.get("solution_status")
    require(status in {"reference_verified", "agent_derived", "partially_verified"}, "solution_status is invalid")
    has_answer_ref = any(ref.get("role") == "answer" for ref in problem_refs)
    independent_types = check_types & INDEPENDENT_CHECK_TYPES
    if status == "reference_verified":
        require(has_answer_ref, "reference_verified solution needs an answer source")
        require("reference_match" in check_types, "reference_verified solution needs a reference_match check")
        require(artifact.get("residual_uncertainty") is None, "reference_verified solution must not claim residual uncertainty")
    elif status == "agent_derived":
        require(not has_answer_ref, "agent_derived solution cannot include an answer source")
        require(len(independent_types) >= 2, "agent_derived solution needs two different independent check types")
        require(artifact.get("residual_uncertainty") is None, "agent_derived solution must resolve residual uncertainty")
    else:
        require(len(independent_types) >= 1, "partially_verified solution needs one independent check")
        text(artifact.get("residual_uncertainty"), "artifact.residual_uncertainty")

    for field in ("branch_conditions", "failure_boundaries"):
        values = arr(artifact.get(field), f"artifact.{field}")
        require(bool(values), f"artifact.{field} must not be empty")
        for index, value in enumerate(values):
            text(value, f"artifact.{field}[{index}]")

    transfer = obj(artifact.get("transfer_problem"), "artifact.transfer_problem")
    text(transfer.get("prompt"), "artifact.transfer_problem.prompt")
    changed = arr(transfer.get("changed_conditions"), "artifact.transfer_problem.changed_conditions")
    require(bool(changed), "transfer_problem.changed_conditions must not be empty")
    for index, value in enumerate(changed):
        text(value, f"artifact.transfer_problem.changed_conditions[{index}]")
    require(transfer.get("answer_hidden") is True, "transfer_problem must hide the answer")
    transfer_targets = [stable_id(item, "artifact.transfer_problem.target_node_ids[]") for item in arr(transfer.get("target_node_ids"), "artifact.transfer_problem.target_node_ids")]
    require(bool(transfer_targets) and set(transfer_targets).issubset(nodes), "transfer_problem has unknown target nodes")

    if course_root is not None:
        resolved = (course_root / display_path).resolve()
        require(course_root == resolved or course_root in resolved.parents, "display_path escapes course root")
        require(resolved.is_file(), f"display_path does not exist: {display_path}")
        display = resolved.read_text(encoding="utf-8")
        require(artifact_id in display, "Markdown display is missing artifact_id")
        require(endpoint_statement in display, "Markdown display is missing the endpoint statement")
        require(final_answer in display, "Markdown display is missing the final answer")
        for step_id in steps:
            require(step_id in display, f"Markdown display is missing step ID {step_id!r}")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Exam Hacker solved-problem artifact")
    parser.add_argument("artifact", help="Path to .solve.json")
    parser.add_argument("--strategy", help="Optional strategy.json used to verify bindings")
    parser.add_argument("--course-root", help="Optional course root used to verify display_path")
    args = parser.parse_args()
    try:
        artifact_path = Path(args.artifact).resolve()
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        strategy = json.loads(Path(args.strategy).read_text(encoding="utf-8")) if args.strategy else None
        course_root = Path(args.course_root).resolve() if args.course_root else None
        artifact = validate_artifact(data, strategy, course_root)
    except (OSError, json.JSONDecodeError, ArtifactError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print(
        "VALID SOLUTION: "
        f"artifact={artifact['artifact_id']} "
        f"status={artifact['solution_status']} "
        f"steps={len(artifact['steps'])} "
        f"endpoint={artifact['endpoint']['node_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
