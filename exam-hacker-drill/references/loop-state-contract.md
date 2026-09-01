# Loop State Contract For Drill

Contract version: `exam-hacker-loop/v1`.

## Strategy Fields Read By Drill

`progress/strategy.json` must contain:

- `course.id`;
- `source_materials` with verified IDs and paths or identities;
- `knowledge_graph.nodes` with stable topic IDs;
- `action_list` with stable Session IDs, kinds, states, success criteria, topic IDs, and input material IDs;
- `loop_state.strategy_revision`;
- `loop_state.next_session_ids`.

Drill may execute only a Session whose state is `active` or `queued`. It reads but never modifies strategy state.

## Preparation Artifacts

Drill may consume:

- `exam-hacker-compress/v1` artifacts bound to the same course, revision, Session, and topic IDs;
- `exam-hacker-solve/v1` artifacts bound to the same course, revision, Session, and topic IDs.

The compression artifact contributes answer-hidden `retrieval_probes`. The solved artifact contributes only its answer-hidden `transfer_problem`; its visible worked answer is `practice_only` and cannot be graded as a new attempt.

## Evidence Log

`progress/mastery-evidence.jsonl` is append-only UTF-8 JSON Lines. Each non-empty line is one object:

```json
{
  "contract_version": "exam-hacker-loop/v1",
  "event_id": "event-force-method-001",
  "course_id": "structural-mechanics-final",
  "strategy_revision_observed": 1,
  "observed_at": "2026-08-31T10:30:00+08:00",
  "source_skill": "exam-hacker-drill",
  "session_id": "session-force-method-01",
  "topic_id": "force-method",
  "evidence_type": "drill",
  "result": {
    "success": false,
    "level_observed": 1,
    "score_earned": 3,
    "score_possible": 10,
    "error_tags": ["compatibility-equation-missing"],
    "notes": "Recognized the method but could not write the compatibility equation."
  },
  "source_refs": [
    {
      "material_id": "review-sheet",
      "locator": "section 3",
      "claim": "Force method is in scope"
    }
  ]
}
```

Required evidence types: `drill`, `micro_probe`, `graded_work`, `session_receipt`, or `user_report`.

`level_observed` is `0`–`3`. Score fields are optional but, when present, must be numeric, non-negative, and earned must not exceed possible. `error_tags` is an array of stable kebab-case labels.

The event must match the current course, an existing Session, a topic used by that Session, and the strategy revision observed when work began.

Event IDs are immutable and unique. Never edit prior lines. Corrections use a new event with `supersedes_event_id`.

## Evidence Strength

Answer-hidden, source-graded performance can update mastery. Exposed-answer practice cannot. A self-report remains weaker than demonstrated performance.
