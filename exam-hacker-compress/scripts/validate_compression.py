#!/usr/bin/env python3
"""Validate one Exam Hacker compression artifact."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
NODE_ROLES = {"given", "concept", "formula", "constraint", "operation", "checkpoint", "result"}


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


def validate_refs(value: Any, path: str, known_materials: set[str] | None) -> set[str]:
    refs = arr(value, path)
    require(bool(refs), f"{path} must not be empty")
    seen: set[str] = set()
    for index, raw in enumerate(refs):
        ref = obj(raw, f"{path}[{index}]")
        material_id = stable_id(ref.get("material_id"), f"{path}[{index}].material_id")
        if known_materials is not None:
            require(material_id in known_materials, f"{path}[{index}] references unknown material {material_id!r}")
        text(ref.get("locator"), f"{path}[{index}].locator")
        text(ref.get("claim"), f"{path}[{index}].claim")
        seen.add(material_id)
    return seen


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
    require(outputs[output_id].get("type") == "concept_compression", "matching Strategy output is not concept_compression")
    session_topics = set(arr(sessions[session_id].get("knowledge_node_ids"), f"strategy Session {session_id}.knowledge_node_ids"))
    require(set(artifact["scope"]["target_node_ids"]).issubset(session_topics), "target nodes are outside the bound Session")
    require(set(artifact["scope"]["target_node_ids"]).issubset(topics), "target nodes do not resolve in strategy")
    return materials, topics


def validate_artifact(data: Any, strategy: dict[str, Any] | None, course_root: Path | None) -> dict[str, Any]:
    artifact = obj(data, "artifact")
    require(artifact.get("contract_version") == "exam-hacker-compress/v1", "contract_version is invalid")
    require(artifact.get("artifact_type") == "knowledge-chain-compression", "artifact_type is invalid")
    artifact_id = stable_id(artifact.get("artifact_id"), "artifact.artifact_id")
    stable_id(artifact.get("course_id"), "artifact.course_id")
    display_path = relative_path(artifact.get("display_path"), "artifact.display_path")

    for field in ("strategy_revision_observed", "session_id", "output_id"):
        value = artifact.get(field)
        if value is not None:
            if field == "strategy_revision_observed":
                require(isinstance(value, int) and value >= 1, f"artifact.{field} must be null or >=1")
            else:
                stable_id(value, f"artifact.{field}")

    scope = obj(artifact.get("scope"), "artifact.scope")
    mode = scope.get("mode")
    require(mode in {"chain", "node"}, "artifact.scope.mode must be chain or node")
    explicit = scope.get("explicit_node_problem")
    require(isinstance(explicit, bool), "artifact.scope.explicit_node_problem must be boolean")
    target_ids = [stable_id(item, "artifact.scope.target_node_ids[]") for item in arr(scope.get("target_node_ids"), "artifact.scope.target_node_ids")]
    require(len(target_ids) == len(set(target_ids)), "target_node_ids contains duplicates")
    if mode == "chain":
        require(not explicit, "chain mode cannot claim an explicit node problem")
        require(len(target_ids) >= 2, "chain mode needs at least two target nodes")
    else:
        require(explicit, "node mode requires an explicit user-reported node problem")
        require(len(target_ids) == 1, "node mode needs exactly one target node")

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
    validate_refs(artifact.get("source_refs"), "artifact.source_refs", known_materials)

    nodes = unique_objects(artifact.get("nodes"), "artifact.nodes")
    require(bool(nodes), "artifact.nodes must not be empty")
    require(set(target_ids).issubset(nodes), "target_node_ids must exist in artifact.nodes")
    if known_topics is not None:
        require(set(target_ids).issubset(known_topics), "target_node_ids must exist in strategy")
    for node_id, node in nodes.items():
        text(node.get("label"), f"artifact.nodes[{node_id}].label")
        require(node.get("role") in NODE_ROLES, f"artifact.nodes[{node_id}].role is invalid")
        text(node.get("minimum_recall"), f"artifact.nodes[{node_id}].minimum_recall")
        validate_refs(node.get("source_refs"), f"artifact.nodes[{node_id}].source_refs", known_materials)

    initial_ids = [stable_id(item, "artifact.initial_node_ids[]") for item in arr(artifact.get("initial_node_ids"), "artifact.initial_node_ids")]
    require(bool(initial_ids) and len(initial_ids) == len(set(initial_ids)), "initial_node_ids must be a non-empty unique array")
    require(set(initial_ids).issubset(nodes), "initial_node_ids contains an unknown node")
    available = set(initial_ids)

    steps = unique_objects(artifact.get("steps"), "artifact.steps")
    require(len(steps) >= (2 if mode == "chain" else 1), f"{mode} mode has too few ordered steps")
    for step_id, step in steps.items():
        inputs = [stable_id(item, f"artifact.steps[{step_id}].input_node_ids[]") for item in arr(step.get("input_node_ids"), f"artifact.steps[{step_id}].input_node_ids")]
        outputs = [stable_id(item, f"artifact.steps[{step_id}].output_node_ids[]") for item in arr(step.get("output_node_ids"), f"artifact.steps[{step_id}].output_node_ids")]
        require(bool(inputs), f"artifact.steps[{step_id}] needs input nodes")
        require(bool(outputs), f"artifact.steps[{step_id}] needs output nodes")
        require(set(inputs).issubset(available), f"artifact.steps[{step_id}] uses a node not yet available")
        require(set(outputs).issubset(nodes), f"artifact.steps[{step_id}] outputs an unknown node")
        require(bool(set(outputs) - available), f"artifact.steps[{step_id}] produces no new node")
        for field in ("trigger", "operation", "why", "check"):
            text(step.get(field), f"artifact.steps[{step_id}].{field}")
        validate_refs(step.get("source_refs"), f"artifact.steps[{step_id}].source_refs", known_materials)
        available.update(outputs)

    endpoint = obj(artifact.get("endpoint"), "artifact.endpoint")
    endpoint_id = stable_id(endpoint.get("node_id"), "artifact.endpoint.node_id")
    endpoint_statement = text(endpoint.get("statement"), "artifact.endpoint.statement")
    text(endpoint.get("verification_method"), "artifact.endpoint.verification_method")
    require(endpoint_id in available, "endpoint node is not produced by the ordered chain")
    require(endpoint_id in nodes, "endpoint node is unknown")

    applicability = obj(artifact.get("applicability"), "artifact.applicability")
    for field in ("conditions", "failure_boundaries"):
        values = arr(applicability.get(field), f"artifact.applicability.{field}")
        require(bool(values), f"artifact.applicability.{field} must not be empty")
        for index, value in enumerate(values):
            text(value, f"artifact.applicability.{field}[{index}]")

    losses = arr(artifact.get("compression_losses"), "artifact.compression_losses")
    require(bool(losses), "artifact.compression_losses must not be empty")
    for index, raw in enumerate(losses):
        loss = obj(raw, f"artifact.compression_losses[{index}]")
        text(loss.get("omitted"), f"artifact.compression_losses[{index}].omitted")
        text(loss.get("restore_when"), f"artifact.compression_losses[{index}].restore_when")

    probes = unique_objects(artifact.get("retrieval_probes"), "artifact.retrieval_probes")
    require(2 <= len(probes) <= 5, "artifact.retrieval_probes must contain two to five probes")
    for probe_id, probe in probes.items():
        text(probe.get("prompt"), f"artifact.retrieval_probes[{probe_id}].prompt")
        require(probe.get("answer_hidden") is True, f"artifact.retrieval_probes[{probe_id}] must hide the answer")
        probe_targets = [stable_id(item, f"artifact.retrieval_probes[{probe_id}].target_node_ids[]") for item in arr(probe.get("target_node_ids"), f"artifact.retrieval_probes[{probe_id}].target_node_ids")]
        require(bool(probe_targets) and set(probe_targets).issubset(nodes), f"artifact.retrieval_probes[{probe_id}] has unknown targets")

    if course_root is not None:
        resolved = (course_root / display_path).resolve()
        require(course_root == resolved or course_root in resolved.parents, "display_path escapes course root")
        require(resolved.is_file(), f"display_path does not exist: {display_path}")
        display = resolved.read_text(encoding="utf-8")
        require(artifact_id in display, "Markdown display is missing artifact_id")
        require(endpoint_statement in display, "Markdown display is missing the endpoint statement")
        for step_id in steps:
            require(step_id in display, f"Markdown display is missing step ID {step_id!r}")
    return artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Exam Hacker compression artifact")
    parser.add_argument("artifact", help="Path to .compress.json")
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
        "VALID COMPRESSION: "
        f"artifact={artifact['artifact_id']} "
        f"mode={artifact['scope']['mode']} "
        f"steps={len(artifact['steps'])} "
        f"endpoint={artifact['endpoint']['node_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
