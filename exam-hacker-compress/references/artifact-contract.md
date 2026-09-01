# Compression Artifact Contract

Contract version: `exam-hacker-compress/v1`.

The canonical artifact is UTF-8 JSON. It describes a source-grounded executable knowledge chain; Markdown is a display derived from the same data.

## Identity And Binding

Required top-level fields:

- `contract_version`: `exam-hacker-compress/v1`;
- `artifact_type`: `knowledge-chain-compression`;
- stable `artifact_id` and `course_id`;
- `strategy_revision_observed`, `session_id`, and `output_id`, each nullable only for standalone work;
- relative `display_path` ending in `.md`;
- non-empty `source_refs`.

When Strategy state is supplied, course, revision, Session, expected output, source IDs, and target topic IDs must resolve. The expected output type is `concept_compression`.

## Scope

`scope.mode` is `chain` or `node`.

- Chain mode is the default, uses `explicit_node_problem: false`, and has at least two `target_node_ids`.
- Node mode requires `explicit_node_problem: true` and exactly one target node.

Both modes still preserve the minimum surrounding inputs and outputs needed to execute the chain.

## Reproducible Chain

`nodes` is a unique catalog. Each node requires ID, label, role, `minimum_recall`, and source references. Roles are `given`, `concept`, `formula`, `constraint`, `operation`, `checkpoint`, or `result`.

`initial_node_ids` names information available before execution.

Each ordered step requires:

- stable `id`;
- `input_node_ids` already available at that point;
- one or more `output_node_ids` defined in the node catalog;
- operation, reason, check, and source references.

At least one output from every step must be new. After each step its outputs become available. The endpoint node must therefore be produced by the ordered chain, not merely mentioned.

`endpoint` contains the final node ID, a user-facing statement, and a concrete verification method.

## Loss And Retrieval

`applicability.conditions` and `applicability.failure_boundaries` are non-empty.

`compression_losses` records omitted material and `restore_when`. This prevents a short artifact from pretending to be universally sufficient.

`retrieval_probes` contains two to five prompts. Every probe has a stable ID, `answer_hidden: true`, and one or more known target nodes. A probe is not mastery evidence.

## Display Contract

The Markdown display must contain:

- the artifact ID;
- the exact endpoint statement;
- every ordered step ID.

This is a minimum synchronization check, not proof that prose quality is good.
