---
name: exam-hacker
description: Discover, select, and invoke one installed Exam Hacker specialist for an exam-cram request. Use when the user invokes exam-hacker, asks what to do next, wants one algorithmic STEM chain compressed, one problem solved, or a final-exam survival task. Do not perform specialist work inside the router.
---

# Exam Hacker Router

## Purpose

Select exactly one next operator in the Exam Hacker system:

```text
triage -> [compress | solve] -> drill -> replan -> drill
```

`compress` and `solve` are optional preparation operators. They create artifacts but do not prove mastery or edit loop state.

The router reduces choice. It does not analyze course content, generate study artifacts, grade answers, or edit loop state.

## Installed Specialist Check

Before reading course state or choosing a route, locate this `SKILL.md` directory and run:

```powershell
python scripts/list-specialists.py --strict
```

The script is the authority for the five downstream specialists currently installed for Codex. It checks `~/.codex/skills` and `~/.agents/skills`, validates each `SKILL.md` frontmatter name, and rejects duplicate installations that could create ambiguous routing.

- Route only to a specialist returned by the script.
- If a specialist is missing, malformed, or installed in both roots, stop and report the exact missing or conflicting name and searched roots.
- Do not fall back to legacy monolithic behavior and do not pretend an unavailable specialist was invoked.
- Preserve the script result for this turn; do not repeatedly rescan after choosing.

## Specialist Roster

| Specialist | Use when | Owns |
|---|---|---|
| `$exam-hacker-triage` | No usable `progress/strategy.json` exists, or the user asks what to study, defer, or abandon | Initial strategy, source inventory, mastery snapshot, first 1–3 Sessions |
| `$exam-hacker-compress` | The user wants one algorithmic STEM knowledge chain compressed, or explicitly reports failure at one named node | One validated chain or explicit-node compression artifact |
| `$exam-hacker-solve` | The user wants the complete worked answer or reverse engineering of one algorithmic STEM problem | One validated, practice-only solved-problem chain |
| `$exam-hacker-drill` | A strategy exists and the user wants to start the next Session, practice, verify mastery, or submit answers | One answer-hidden Session and append-only mastery evidence |
| `$exam-hacker-replan` | New performance evidence exists, a Session finished, availability changed, or the user asks what should change | A new strategy revision and the next 1–3 Sessions |

## Routing Order

Respect an explicitly named specialist. Otherwise apply the first matching rule:

1. If the user submits raw answers to an active Session or asks for those answers to be graded and recorded, select `$exam-hacker-drill`. Raw work is not evidence until drill grades it.
2. If a new evidence event already exists after the strategy cursor, or the user reports an already-graded result, completed Session, or changed availability, select `$exam-hacker-replan`.
3. If the user asks for the complete answer, worked solution, or reverse engineering of one eligible algorithmic STEM problem, select `$exam-hacker-solve`. If it is an unanswered drill task, carry forward that the result must be `practice_only`.
4. If the user asks to compress an eligible algorithmic STEM knowledge chain, select `$exam-hacker-compress`. Carry an explicit named-node failure as node mode; otherwise carry chain mode.
5. If the user asks to start, practice, be tested, verify mastery, or continue the next Session and a strategy exists, select `$exam-hacker-drill`.
6. If no usable strategy exists, or the user asks for initial priorities, target feasibility, or strategic abandonment, select `$exam-hacker-triage`.
7. If the request asks for whole-course A4 sheets, generic knowledge maps, broad question banks, or non-algorithmic compression without one of the transitions above, state that it is outside the current collection. Do not smuggle the legacy monolith back into the router.

When filesystem access is available, inspect only the expected state files needed for routing:

- `progress/strategy.json`;
- `progress/mastery-evidence.jsonl`.

Do not scan course content merely to choose a specialist.

## Handoff

State the selected specialist in one line and preserve already-known inputs:

```text
Selected: $exam-hacker-triage
Reason: no usable strategy exists.
Carry forward: exam date, target score, availability, material location.
```

If the selected specialist passed the installed check, apply that specialist in the same turn. Read its `SKILL.md` and required references, then continue with the preserved handoff. If the runtime still cannot load the verified path, stop with the exact invocation, verified path, and compact handoff. Do not make the user repeat facts already present in the request or state files.

## State Ownership

- Router: reads state only.
- Triage: creates `strategy.json` revision 1 and may initialize the evidence log.
- Compress: creates one compression artifact; it never edits strategy or evidence.
- Solve: creates one solved-problem artifact marked `practice_only`; it never edits strategy or evidence.
- Drill: never edits `strategy.json`; it may append mastery evidence only after observing user performance.
- Replan: creates later strategy revisions and advances the evidence cursor.

## Stop Conditions

- Route to one specialist only.
- Never select a specialist before the installed check passes.
- Do not generate a generic study plan as a fallback.
- Do not invoke triage merely because the user says “期末”; use the actual state transition.
- If state files are malformed, route to the specialist that owns repair: triage for missing or unusable initial strategy, replan for a valid prior strategy with inconsistent later evidence.
