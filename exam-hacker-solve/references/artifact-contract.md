# Solution Artifact Contract

Contract version: `exam-hacker-solve/v1`.

The canonical artifact is UTF-8 JSON. It contains a full worked answer plus a reproducible and verified solution chain. Markdown is its human-readable display.

## Identity And Binding

Required top-level fields:

- `contract_version`: `exam-hacker-solve/v1`;
- `artifact_type`: `solved-problem-chain`;
- stable `artifact_id` and `course_id`;
- `strategy_revision_observed`, `session_id`, and `output_id`, nullable only for standalone work;
- relative `display_path` ending in `.md`;
- `answer_policy: "full_solution"`;
- `practice_status: "practice_only"`.

When Strategy state is supplied, course, revision, Session, expected output, source IDs, and topic IDs must resolve. The expected output type is `solution_chain` or the compatibility type `paper_deconstruction`.

## Problem And Source Status

`problem` requires stable ID, complete statement, target topic IDs, and source references. Source reference roles are `problem`, `theory`, `answer`, or `rubric`.

`solution_status` is:

- `reference_verified` when a verified answer source is present and a `reference_match` check passes;
- `agent_derived` when no verified answer is available and at least two different independent check types pass;
- `partially_verified` when only one independent check can be completed and `residual_uncertainty` is explicit.

## Reproducible Chain

`nodes` is a unique catalog with ID, label, role, mathematical meaning, and source references. Roles are `given`, `concept`, `formula`, `constraint`, `operation`, `checkpoint`, or `result`.

`initial_node_ids` identifies information available before solving.

Each ordered step requires:

- stable ID;
- input nodes already available at that point;
- at least one new output node;
- trigger, operation, equation or rule, reason, local check, and source references.

The endpoint node must be produced by the chain. It cannot be inserted as an unexplained final answer.

## Endpoint And Verification

`endpoint` requires node ID, requested statement, complete `final_answer`, units or `dimensionless`, and acceptance condition.

`verification_checks` contains passed checks only. Allowed types:

- `reference_match`;
- `substitution`;
- `dimensional`;
- `equilibrium`;
- `boundary`;
- `limit`;
- `independent_method`;
- `logical_completion`.

Every check requires ID, procedure, observed result, and `passed: true`. Failed checks block completion and must be resolved rather than hidden.

`branch_conditions` and `failure_boundaries` are non-empty. They define when the chain changes or stops applying.

## Transfer Problem

`transfer_problem` contains a new prompt, at least one changed condition, `answer_hidden: true`, and target topic IDs. It is input for `$exam-hacker-drill`, not evidence.

## Display Contract

The Markdown display must contain the artifact ID, exact endpoint statement, complete final answer, and every step ID.
