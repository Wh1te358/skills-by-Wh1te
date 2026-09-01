---
name: exam-hacker-compress
description: Compress one algorithmic STEM knowledge chain into a source-grounded, reproducible path with a verifiable endpoint. Use for calculation or derivation topics, and use node mode only when the user explicitly names that node as the failure point. Do not summarize whole courses or grade mastery.
---

# Exam Hacker Compress

## Job

Turn verified STEM material into the smallest knowledge chain the user can execute from an exam cue to a checkable endpoint.

Default to a chain of connected nodes. Use node mode only when the user explicitly says that a named node is where they fail. “Explain this chapter” is not permission to collapse the work into a node or expand it into a chapter summary.

This Skill creates a learning artifact. It does not prove mastery.

## Eligibility Gate

Proceed only when the task is algorithmic STEM:

- the task has a numerical, symbolic, proof, construction, or decision endpoint;
- correctness can be checked by a reference result or an independent test;
- the route can be expressed as reproducible operations with explicit inputs and outputs.

Do not force memorization-heavy, interpretive, open-ended essay, or taste-based work into this contract. State the mismatch and stop.

## Inputs

Use existing context before asking questions. Recover:

- the target course and verified source materials;
- the target Session and expected output when `progress/strategy.json` exists;
- the requested knowledge chain, or the exact failed node if the user named one;
- the endpoint that the chain must produce and how it can be checked.

If the endpoint or source basis is missing, ask only for the missing item that changes the artifact. Do not invent a chain from chapter titles alone.

If a required PDF has empty or sparse extracted text, render the exact relevant pages and inspect them with the available multimodal image capability before treating the source as unreadable. OCR and contact sheets may locate pages but cannot verify formulas, diagrams, or claims. Cite the 1-based PDF pages actually inspected; targeted inspection does not support whole-document claims.

Before writing an artifact, read [references/artifact-contract.md](references/artifact-contract.md) completely.

## Scope Decision

Choose exactly one mode:

- `chain`: the default. Retain at least two target nodes and the transitions needed to reach the endpoint.
- `node`: allowed only after an explicit user report such as “我在兼容方程这个节点卡住了”. Keep only the local inputs, operation, output, and boundary needed to repair that node.

Do not infer node mode merely because one node appears weak in `mastery_snapshot`.

## Compression Method

1. Lock the endpoint before compressing. State the final quantity, expression, proof condition, or decision and its verification method.
2. Extract only the source-backed nodes required to reach it.
3. Order steps topologically: every step may use only initial nodes or outputs produced by earlier steps.
4. For each step preserve its trigger, inputs, operation, output, justification anchor, and local check.
5. Preserve applicability conditions and failure boundaries. Conditional tools such as zero, limit, reverse, dimensional, or boundary tests enter only when they can actually validate this chain.
6. Record compression losses: what was intentionally removed and the condition that requires restoring it.
7. Add two to five answer-hidden retrieval probes. They are handoff material for `$exam-hacker-drill`, not evidence that the user passed.

The result should behave like an executable interface, not a smaller textbook.

## Outputs

Use stable paths:

```text
progress/artifacts/<artifact-id>.compress.json
progress/artifacts/<artifact-id>.md
```

The JSON file is the contract source of truth. The Markdown file is its human-readable view and must preserve the same artifact ID, endpoint statement, and step IDs.

When a matching Strategy output exists, reuse its `output_id` as `artifact_id`. Otherwise create one stable kebab-case ID. Do not edit `progress/strategy.json` merely to mark the artifact available.

Validate before finishing:

```powershell
python scripts/validate_compression.py progress/artifacts/<artifact-id>.compress.json --course-root .
```

When Strategy state exists, also bind the artifact to it:

```powershell
python scripts/validate_compression.py progress/artifacts/<artifact-id>.compress.json --strategy progress/strategy.json --course-root .
```

## Handoff

Report the mode, endpoint, retained chain, compression losses, artifact paths, and validation result. Then hand the retrieval probes to `$exam-hacker-drill`.

## Authority Boundary

- Never edit `strategy.json`, priorities, Session order, or mastery state.
- Never append `mastery-evidence.jsonl`.
- Never call an artifact “mastered” because it was generated or read.
- Never produce a whole-course summary, A4 sheet, generic knowledge map, or worked answer bank.
- Never invent source anchors, teacher emphasis, scoring rules, or process marks.

## Stop Conditions

- Stop after one chain or one explicitly requested failed node is compressed and validated.
- If a source-backed transition cannot be reproduced, record the missing link instead of bridging it with confident prose.
- If a scanned source page cannot be rendered and visually inspected, record the source gap instead of using OCR output as the missing transition.
- If the user supplies a specific problem and wants its complete solution, route to `$exam-hacker-solve`.
- If the user wants to demonstrate recall or transfer, route to `$exam-hacker-drill`.
