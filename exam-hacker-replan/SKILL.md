---
name: exam-hacker-replan
description: Update an existing Exam Hacker strategy from new mastery evidence or changed availability, then select the next one to three Sessions. Use after a drill or completed Session, or when the user's remaining capacity changes. Do not create the initial strategy or generate practice questions.
---

# Exam Hacker Replan

## Job

Consume new evidence, revise the strategy once, and choose the next executable slice. This Skill is the only specialist allowed to create strategy revision 2 or later.

## Required State

Read:

- `progress/strategy.json`;
- `progress/mastery-evidence.jsonl` when present;
- only evidence events after `loop_state.last_evidence_event_id`;
- explicit availability changes supplied by the user.

Before changing state, read [references/loop-state-contract.md](references/loop-state-contract.md) completely.

If no valid prior strategy exists, stop and route to `$exam-hacker-triage`.

## Workflow

### 1. Establish the revision boundary

Record:

- current strategy revision;
- current evidence cursor;
- new event IDs after the cursor;
- any explicit availability change;
- the Sessions and priorities potentially affected.

If there is neither new evidence nor a capacity change, do not rewrite the strategy.

### 2. Update mastery, not exam facts

Performance evidence may change:

- mastery level and confidence;
- error diagnosis;
- Session completion;
- learnability estimate;
- time allocation and next Sessions.

Performance evidence alone may not change:

- official exam scope or score weights;
- teacher emphasis;
- historical frequency;
- source identity.

Keep exam-value evidence and mastery evidence separate.

### 3. Resolve evidence strength

Prefer relevant recent demonstrated performance over self-report. Respect `supersedes_event_id`. Do not average incompatible events into fake precision.

When evidence conflicts, state the conflict and use the result that best matches the same topic, task type, and current conditions. Lower confidence if the conflict remains material.

### 4. Recalculate the next slice

Re-evaluate:

- the mastery gap;
- whether the previous Session met success criteria;
- learnability and remaining capacity;
- any abandonment risk;
- which one to three Sessions should be next.

Do not preserve a failed plan for aesthetic consistency. Do not erase completed work or delete stable IDs.

New Sessions require evidence-backed topics, verified inputs, capacity, observable success criteria, and stable IDs. Mark obsolete future Sessions `superseded` instead of deleting them.

### 5. Create exactly one new revision

Write a candidate to `progress/strategy.next.json`:

- increment `loop_state.strategy_revision` by exactly one;
- update `loop_state.updated_at`;
- advance `last_evidence_event_id` to the last consumed event;
- set one to three `next_session_ids`, unless the loop is complete;
- append one `revision_log` entry with consumed event IDs and concrete changes;
- recalculate capacity fields.

Preserve `source_materials` byte-for-byte as JSON data. New materials require a fresh triage audit, not silent insertion during replanning.

### 6. Validate before replacement

Run:

```powershell
python scripts/validate_replan.py progress/strategy.json progress/strategy.next.json --evidence-log progress/mastery-evidence.jsonl --course-root .
```

Only after both the full strategy validator and transition validator pass:

1. preserve the prior file as `progress/history/strategy-r<revision>.json`;
2. replace `progress/strategy.json` with the validated candidate;
3. report the new revision and consumed event IDs.

If validation fails, leave the prior strategy untouched.

## Output

Report only decision-changing information:

- new evidence consumed;
- mastery changes;
- Sessions completed, retained, added, or superseded;
- changed abandonment decisions;
- remaining capacity;
- next one to three Session IDs.

## Authority Boundary

- May create revisions 2+ only.
- May append a normalized `user_report` evidence event when performance arrives outside `$exam-hacker-drill`.
- May not modify raw sources or invent exam-value evidence.
- May not generate drill questions or expose answers.
- May not rewrite without new evidence or an explicit capacity change.

## Stop Conditions

- Stop after one validated revision.
- If evidence refers to unknown topics or Sessions, reject it instead of guessing the mapping.
- If the course root or source identities changed, route back to `$exam-hacker-triage`.
- If the next move is ready, hand off to `$exam-hacker-drill`.
