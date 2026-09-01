# Loop State Contract For Replan

Contract version: `exam-hacker-loop/v1`.

## Strategy Ownership

- Revision 1 is created by `exam-hacker-triage`.
- Revision 2 and later are created by `exam-hacker-replan`.
- `exam-hacker-drill` never modifies strategy.

`loop_state` contains contract version, integer strategy revision, status, one to three next Session IDs, the last consumed evidence event ID, and an offset-aware update timestamp.

`revision_log` is append-only. Every revision adds exactly one entry with revision number, timestamp, reason, consumed event IDs, and concrete changes.

## Evidence Cursor

`mastery-evidence.jsonl` is ordered by file position. Event IDs are unique. The cursor is `null` before any event is consumed.

To find new evidence:

1. parse every non-empty line;
2. locate the cursor event when non-null;
3. take later events in file order;
4. resolve corrections through `supersedes_event_id`;
5. consume a continuous ordered prefix of events relevant to the current course and known topics or Sessions;
6. set the new cursor to the final consumed event.

Unknown or malformed events block the revision. Do not skip an earlier event and advance the cursor past it; that would orphan evidence permanently.

## Immutable And Mutable State

Immutable during replan:

- `schema_version`;
- `course` facts;
- `source_outline`;
- `source_materials` as JSON data;
- `knowledge_graph` as JSON data;
- each priority's topic IDs and evidence references;
- prior `revision_log` entries;
- stable IDs of completed Sessions and observed topics.

Mutable with evidence or explicit user input:

- `mastery_snapshot`;
- Session state and ordering;
- priorities when the reason is mastery, learnability, or capacity rather than invented exam facts;
- abandonment when the evidence gate is re-evaluated;
- availability and capacity from explicit user changes;
- next Session IDs and loop status.

Obsolete future Sessions become `superseded`; they are not deleted. Completed Sessions remain present.

## Revision Transition

A valid transition:

- increments revision by exactly one;
- preserves all previous revision-log entries;
- appends exactly one new revision entry;
- consumes at least one new event, unless an explicit availability change is recorded;
- advances the evidence cursor consistently;
- leaves one to three executable next Sessions unless status is `complete`;
- passes the triage strategy validator.
