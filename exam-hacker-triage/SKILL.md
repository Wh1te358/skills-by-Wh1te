---
name: exam-hacker-triage
description: Create the initial evidence-backed final-exam strategy, mastery snapshot, and first one to three executable Sessions. Use when no usable strategy.json exists or the user asks what to study, defer, or abandon. Do not generate drills or revise a strategy after performance evidence exists.
---

# Exam Hacker Triage

## Job

Decide what the user should attack first under real evidence, current mastery, and remaining capacity. Produce revision 1 of the shared loop state.

This Skill owns initial strategy creation. It does not execute a Session, grade answers, or replan from later performance.

## Inputs

Use existing context before asking questions. Recover:

1. course and subject type;
2. target score;
3. absolute exam date and timezone;
4. realistic total available minutes;
5. course materials and their readability;
6. current mastery.

Keep raw evidence and generated state separate:

```text
course-root/
  reference/
  progress/
    00_survival-outline.md
    strategy.json
    mastery-evidence.jsonl   # may not exist until a drill produces evidence
```

## Required References

Before prioritizing, read [references/evidence-contract.md](references/evidence-contract.md) completely.

When any PDF has empty or sparse extracted text, read [references/scanned-pdf-protocol.md](references/scanned-pdf-protocol.md) completely before deciding that the source is unreadable.

Before collecting current mastery, read [references/mastery-snapshot.md](references/mastery-snapshot.md) completely.

Before writing machine state, read [references/strategy-contract.md](references/strategy-contract.md) completely.

## Workflow

### 1. Audit materials

Enumerate only real inputs. Give every readable source a stable ID and resolvable anchors. Record missing or unreadable evidence as `material_gaps`; never turn it into a low-frequency claim.

For every PDF, first run `scripts/inspect_pdf_readability.py`. If `visual_followup_required` is true, including `mixed`, `scan-likely`, and `no-readable-signal`, do not equate failed text extraction with failed reading: render relevant pages to images and inspect them with the available multimodal image capability. OCR may locate candidate pages, but OCR text and contact sheets are navigation aids, not verified evidence. Record the inspection method, coverage, and exact 1-based pages inspected in `source_materials[].inspection`.

When three days or less remain, visually inspect only pages capable of changing scope, scoring, priority, abandonment, or a bound Session unless the user requests a full audit. A targeted inspection verifies only its recorded pages; it cannot support whole-document absence or frequency claims.

### 2. Collect the one-minute mastery snapshot

Extract the topic list from verified materials. Let the user reply with behavior-anchored `0–3` levels. Do not make the user reconstruct the syllabus or complete a separate diagnostic when three days or less remain.

If the user declines, use `unknown`. A self-report measures current ability, not exam value.

### 3. Build the decision model

Keep four axes visible:

| Axis | Question | Evidence |
|---|---|---|
| Exam value | What marks or prerequisites can this control? | Scope, rubric, review sheet, papers, answers |
| Mastery gap | What can the user currently do unaided? | Graded work, micro-probe, self-report |
| Learnability | Can the gap move before the exam? | Representative task complexity and prerequisite chain |
| Time cost | What will it displace? | User-confirmed capacity and Session estimate |

Use ordinal judgments. Do not fabricate precise expected-score percentages.

### 4. Apply the abandonment gate

Strategic abandonment requires direct evidence, insufficient capacity, a stated downside, and a reversal condition. If the gate fails, use `defer` or `provisional`.

### 5. Generate only the first executable slice

Create one to three Sessions, not a ceremonial full-course calendar. Each Session must fit available capacity and contain:

- one objective;
- duration;
- source and topic IDs;
- observable success criteria;
- expected evidence or artifact;
- dependencies.

The first slice should produce evidence quickly enough for `$exam-hacker-replan` to change the next move.

### 6. Write both outputs

Write:

- `progress/00_survival-outline.md` for the user;
- `progress/strategy.json` as revision 1 and machine source of truth.

The outline must show material gaps, mastery snapshot, decision table, target feasibility, first Sessions, and any evidence-backed abandonment.

Initialize:

- `loop_state.contract_version` as `exam-hacker-loop/v1`;
- `loop_state.strategy_revision` as `1`;
- one to three `next_session_ids`;
- `loop_state.last_evidence_event_id` as `null`;
- revision 1 in `revision_log`.

Do not create fake mastery events merely to make `mastery-evidence.jsonl` exist.

### 7. Validate

Run:

```powershell
python scripts/validate_strategy.py progress/strategy.json --course-root .
```

Do not finish while validation fails.

## Authority Boundary

- Triage may create strategy revision 1 only.
- It may not grade a user response.
- It may not rewrite a later valid revision; route that work to `$exam-hacker-replan`.
- It may not generate question banks, concept-compression notes, A4 sheets, or knowledge maps.
- It may not put minute-by-minute Guide steps inside `strategy.json`.

## Stop Conditions

- If no material supports exam-value claims, produce a provisional route and no strategic abandonment.
- If PDF text extraction fails, attempt the scanned-PDF visual fallback before marking the source unreadable. If rendering or multimodal inspection is unavailable, record the exact failure as a material gap.
- If exam date or capacity is missing and cannot be safely derived, ask only for that decision-bearing input.
- If a later strategy revision already exists, stop and route to `$exam-hacker-replan`.
- If the user wants to start a Session, stop and route to `$exam-hacker-drill`.
