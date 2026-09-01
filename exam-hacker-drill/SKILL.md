---
name: exam-hacker-drill
description: Execute one planned exam Session through source-grounded, answer-hidden active work, grade the user's response, and append mastery evidence. Use when a valid strategy exists and the user wants to start, practice, or verify the next Session. Do not create or modify strategy.json.
---

# Exam Hacker Drill

## Job

Turn one planned Session into observable performance evidence. This Skill owns execution and evidence capture, not priority decisions.

## Required State

Read:

- `progress/strategy.json`;
- the Session named by the user, or the first ID in `loop_state.next_session_ids`;
- only the verified source materials referenced by that Session.
- any validated `$exam-hacker-compress` or `$exam-hacker-solve` artifact explicitly bound to that Session.

If a required problem, answer, or rubric PDF has empty or sparse extracted text, render the exact relevant pages and inspect them with the available multimodal image capability before presenting or grading the task. OCR may locate pages but is not grading evidence. Preserve the 1-based page anchor used for every source-backed judgment.

Before acting, read [references/loop-state-contract.md](references/loop-state-contract.md) completely.

If no valid strategy or executable Session exists, stop and route to `$exam-hacker-triage` or `$exam-hacker-replan` as appropriate. Do not invent a detached Session.

## One-Session Workflow

### 1. Lock the Session

State:

- strategy revision observed;
- Session ID and objective;
- topic IDs;
- duration and success criteria;
- verified input materials.

Do not silently switch topics because another chapter looks interesting.

### 2. Choose the smallest active task

Use the Session kind:

- `study`: give only the minimum source-grounded launch scaffold, then require closed-book reconstruction or application;
- `drill`: present answer-hidden questions immediately;
- `micro_probe`: present one 2–5 minute representative task that can change a consequential skip decision.

A study scaffold may identify a formula, trigger, or method skeleton, but it must not become a long lecture. Active work must begin in the same turn.

When a compression artifact exists, use its answer-hidden retrieval probes. When a solved-problem artifact exists, use only its answer-hidden transfer problem; do not reuse the already visible worked problem as evidence.

### 3. Hide answers

Do not reveal answers, rubrics, worked steps, or hints before the user attempts the task unless the Session explicitly tests answer reading rather than recall.

If the user asks for an answer key up front, provide it only if requested, but mark the result `practice_only`; it cannot become mastery evidence.

### 4. Grade from evidence

After the user responds:

- compare with verified answers, rubrics, or source logic;
- cite the exact material anchor;
- separate mathematical or factual errors from presentation issues;
- never invent process marks;
- record whether success criteria were met.

Map demonstrated performance to the same `0–3` scale:

- `0`: no viable start or method recognition;
- `1`: progresses only with answer exposure or major hints;
- `2`: independently completes a standard task;
- `3`: completes a timed variant and explains conditions or transfer.

### 5. Append one evidence event

Create one event per topic actually observed. Validate it first:

```powershell
python scripts/append_mastery_event.py progress/mastery-evidence.jsonl event.json --strategy progress/strategy.json --dry-run
```

Then append:

```powershell
python scripts/append_mastery_event.py progress/mastery-evidence.jsonl event.json --strategy progress/strategy.json
```

Do not append evidence before the user performs. Do not record exposed-answer practice as demonstrated mastery.

### 6. Handoff

Report:

- what was observed;
- source-backed grading result;
- appended event IDs;
- whether the Session success criteria passed;
- the exact next transition: `$exam-hacker-replan`.

## File Outputs

Use stable paths when files are requested:

```text
progress/drills/<session-id>-questions.md
progress/drills/<session-id>-result.md
progress/mastery-evidence.jsonl
```

Question files do not count as mastery evidence. Only observed user performance creates an event.

Compression and solved-problem artifacts also do not count as mastery evidence. They are inputs to a fresh answer-hidden task.

## Authority Boundary

- Never edit `progress/strategy.json`.
- Never change priority, abandonment, capacity, or next Session order.
- Never fabricate a rubric or award imaginary process marks.
- Never generate a full-course question bank when one Session is active.
- Never append duplicate or malformed event IDs.

## Stop Conditions

- Stop after one Session produces evidence.
- If required source material remains missing or unreadable after rendered-page visual fallback, record no mastery event and route to triage for evidence repair.
- If strategy revision changed after the task began, record the observed revision and let replan resolve it; do not rewrite history.
