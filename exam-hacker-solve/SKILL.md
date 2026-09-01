---
name: exam-hacker-solve
description: Solve one algorithmic STEM problem completely as a source-grounded, reproducible chain with a verifiable endpoint. Use for the full worked answer or reverse engineering of one calculation, derivation, proof, or deterministic construction. Do not grade mastery or generate broad question banks.
---

# Exam Hacker Solve

## Job

Produce the complete answer to one algorithmic STEM problem while exposing a solution chain that another person can reproduce from the same inputs.

The full answer is visible by design. This is worked-example learning, not testing, so every result is `practice_only` and cannot become mastery evidence.

## Eligibility Gate

Proceed only when:

- the task has a numerical, symbolic, proof, construction, or deterministic decision endpoint;
- the endpoint can be checked against a reference result or by independent verification;
- the solution can be expressed as ordered operations with explicit inputs and outputs.

Reject open-ended essays, taste judgments, unconstrained design exploration, and questions whose missing data prevents a determinate answer. Do not manufacture assumptions merely to force a solution.

## Inputs

Use existing context before asking questions. Recover:

- the exact problem statement and givens;
- verified theory, examples, rubrics, and answer keys when present;
- the bound Session and expected output when `progress/strategy.json` exists;
- the endpoint requested by the problem;
- whether the same question is currently an unanswered `$exam-hacker-drill` task.

If essential givens are missing, identify the minimum missing variable or condition and stop. If the user explicitly authorizes an assumption, label it and show how the result depends on it.

If the problem, theory, answer, or rubric PDF has empty or sparse extracted text, render the exact relevant pages and inspect them with the available multimodal image capability. OCR may find the page, but the rendered page controls the problem statement, formula, diagram, answer, and scoring annotation. Use page-level anchors and expose any OCR-versus-page discrepancy.

Before writing an artifact, read [references/artifact-contract.md](references/artifact-contract.md) completely.

## Source Status

Use exactly one solution status:

- `reference_verified`: the final result is checked against a verified answer source;
- `agent_derived`: no verified answer exists, so the chain is checked by at least two independent methods;
- `partially_verified`: a complete chain is possible but only one independent check is available; expose the residual uncertainty.

Never describe an Agent-derived solution as an official answer.

## Solving Method

1. Restate the requested endpoint and its acceptance condition.
2. Translate the problem into initial knowledge nodes: givens, constraints, sign conventions, applicable models, and required result.
3. Build one ordered chain. Each step must name its trigger, available inputs, operation, new output, justification anchor, and local check.
4. Give the complete worked answer immediately. Do not withhold it behind a compulsory attempt.
5. Verify the endpoint. Use only checks that fit the task: reference match, substitution, dimensional consistency, equilibrium, boundary conditions, limiting behavior, or an independent method.
6. State branch conditions and failure boundaries so the chain is not mistaken for a universal recipe.
7. Add one changed-condition transfer problem with its answer hidden. `$exam-hacker-drill` owns the later attempt and grading.

If the user reports one named failed node rather than asking for the whole solution, route that repair to `$exam-hacker-compress` node mode.

## Outputs

Use stable paths:

```text
progress/artifacts/<artifact-id>.solve.json
progress/artifacts/<artifact-id>.md
```

The JSON file is the contract source of truth. The Markdown view must preserve the same artifact ID, endpoint statement, final answer, and step IDs.

When a matching Strategy output exists, reuse its `output_id` as `artifact_id`. Otherwise create one stable kebab-case ID. Do not edit `progress/strategy.json`.

Validate before finishing:

```powershell
python scripts/validate_solution.py progress/artifacts/<artifact-id>.solve.json --course-root .
```

When Strategy state exists:

```powershell
python scripts/validate_solution.py progress/artifacts/<artifact-id>.solve.json --strategy progress/strategy.json --course-root .
```

## Drill Collision

If this is the unanswered task from an active drill, say that showing the full solution exits assessment mode. Continue because the user explicitly asked to solve, but mark the artifact `practice_only`, append no mastery event, and require a fresh variant for later verification.

## Handoff

Report source status, final answer, endpoint checks, artifact paths, and validation result. Hand the hidden transfer problem to `$exam-hacker-drill`.

## Authority Boundary

- Never edit Strategy state, priority, Session order, or mastery.
- Never append `mastery-evidence.jsonl` from a visible solution.
- Never infer process marks without a verified rubric.
- Never generate a full-course bank or solve multiple unrelated problems in one invocation.
- Never bury a failed verification check. An invalid endpoint is not a completed solution.

## Stop Conditions

- Stop after one complete, validated problem chain.
- Stop before artifact creation when essential data or a defensible verification method is missing.
- Do not call a scanned answer or rubric unavailable until rendered-page inspection has been attempted; if vision or rendering is unavailable, keep the solution Agent-derived or partially verified as appropriate rather than promoting OCR to an official answer.
- If the user wants to attempt the problem without seeing the answer, route to `$exam-hacker-drill`.
- If the user names one failed knowledge node, route to `$exam-hacker-compress` node mode.
