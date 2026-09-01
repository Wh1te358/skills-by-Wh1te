# Exam Hacker Loop Strategy Contract

Write UTF-8 JSON. Keep property names in English and user-facing values in the course language.

## Required Top-Level Shape

```json
{
  "schema_version": 2,
  "course": {},
  "planning_context": {},
  "capacity_summary": {},
  "source_outline": {},
  "source_materials": [],
  "priorities": [],
  "knowledge_graph": {"nodes": [], "edges": []},
  "action_list": [],
  "abandon": [],
  "material_gaps": [],
  "mastery_snapshot": [],
  "loop_state": {},
  "revision_log": []
}
```

`days_left` is forbidden. Store an absolute `planning_context.exam_date` and timezone-aware `strategy_created_at`.

`planning_context.availability` contains:

- `hours_per_day`: compatibility average;
- `total_minutes`: exact user-confirmed capacity available before the exam;
- `source`: `user_confirmed` or `inferred`.

`capacity_summary.available_minutes_at_generation` must equal `total_minutes`. `session_minutes` is the sum of non-superseded Session durations. `deficit_minutes` is `max(0, session_minutes - available minutes)`.

## Sources And Evidence

`source_materials` contains only verified pre-existing evidence. Each item requires stable `id`, `label`, `kind`, `provenance`, `availability: "available"`, and `readability: "verified"`. A path is optional, but when present it must resolve under the course root.

For scanned or mixed PDFs, add an `inspection` receipt:

```json
{
  "document_mode": "scan-likely",
  "method": "vision",
  "pages_total": 60,
  "coverage": "targeted",
  "pages_inspected": [3, 14, 38],
  "ocr_role": "index_only"
}
```

`document_mode` is `text`, `mixed`, `scan-likely`, or `no-readable-signal`. `method` is `embedded_text`, `vision`, or `hybrid`. `coverage` is `targeted` or `full`; full coverage requires every page number. `ocr_role` is `none` or `index_only`. Vision and hybrid sources require page-level evidence locators within `pages_inspected`.

Every priority requires `id`, rank, title, level, reason, `knowledge_node_ids`, and `evidence_refs`. Allowed levels: `must_win`, `high_frequency`, `supporting`, `abandonable`.

Each evidence reference contains `material_id`, a real `locator`, and `claim`. Every material ID must resolve.

## Topics And Mastery

Knowledge nodes are stable topic IDs. Each node requires `id`, label, type, mastery requirement, and `source_refs`. Allowed node types: `concept`, `formula`, `theorem`, `method`, `boundary_condition`, `scoring_routine`.

`mastery_snapshot` items contain:

```json
{
  "topic_id": "force-method",
  "level": 1,
  "evidence_type": "self_report",
  "evidence_ref": "U01:user-confirmed",
  "confidence": "medium",
  "observed_at": "2026-08-31T10:00:00+08:00",
  "notes": "看答案能懂，闭卷不会启动"
}
```

Level is `0`–`3` or `null`. Allowed evidence types: `drill`, `graded_work`, `micro_probe`, `session_receipt`, `self_report`, `user_report`, `unknown`. Confidence: `high`, `medium`, `low`, `unknown`.

## Sessions

Initial `action_list` contains one to three Sessions. Each requires:

- stable `id`;
- `kind`: `study`, `drill`, or `micro_probe`;
- `state`: `active` or `queued` initially;
- phase, title, objective, and observable success criteria;
- duration between 5 and 1200 minutes and within total capacity;
- priority and topic references;
- dependencies and verified input material IDs;
- expected outputs.

Do not put `steps`, `guide`, or minute-by-minute instructions in strategy state.

Expected output types include `practice_evidence`, `concept_compression`, `solution_chain`, `paper_deconstruction`, `error_sop`, `formula_sheet`, `knowledge_map`, `a4_sheet`, and `other`. Initial status is `planned`; an `available` output needs a real path or href.

Use `concept_compression` for an `$exam-hacker-compress` artifact and `solution_chain` for an `$exam-hacker-solve` artifact. Artifact generation does not prove mastery and does not itself change Session state.

## Loop State

Revision 1 uses:

```json
{
  "contract_version": "exam-hacker-loop/v1",
  "strategy_revision": 1,
  "status": "active",
  "next_session_ids": ["session-force-method"],
  "last_evidence_event_id": null,
  "updated_at": "2026-08-31T10:00:00+08:00"
}
```

`next_session_ids` contains one to three existing, non-completed Sessions.

`revision_log` begins with one entry containing revision `1`, timestamp, reason `initial_triage`, empty `consumed_event_ids`, and a concise changes list.

## Abandonment

Every `abandon` item requires topic ID, decision `strategic_abandonment`, evidence references, capacity reason, risk if wrong, reversal condition, and whether the user explicitly accepted an evidence gap.

If the evidence gate fails, do not create an `abandon` item. Represent the topic as supporting, provisional, or deferred in the human outline.

## Material Gaps

Each gap requires stable ID, description, impact, and optional resolution. Missing evidence never enters `source_materials`.
