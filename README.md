# Exam Hacker

English | [简体中文](README.zh-CN.md)

An evidence-driven final-exam survival Skill collection for algorithmic STEM courses.

Exam Hacker is not a summary generator and does not pretend that every topic deserves equal attention. It turns real course materials, the user's current mastery, and the remaining time into a small executable study loop. Priorities, abandonment, grading, and replanning must all resolve to evidence.

## Why It Is A Collection

The former monolithic Skill mixed six different decisions. The current version gives each state transition one owner:

| Skill | Responsibility |
|---|---|
| `exam-hacker` | Read state, choose exactly one specialist, and hand off known inputs |
| `exam-hacker-triage` | Audit materials, collect a one-minute mastery snapshot, create strategy revision 1, and select the first 1–3 Sessions |
| `exam-hacker-compress` | Compress one algorithmic knowledge chain or one explicitly named failure node |
| `exam-hacker-solve` | Produce one complete, reproducible worked solution or reverse-engineered solution chain |
| `exam-hacker-drill` | Run one answer-hidden Session, grade observed work, and append mastery evidence |
| `exam-hacker-replan` | Consume new evidence or changed availability, create the next strategy revision, and choose the next 1–3 Sessions |

```text
triage -> [compress | solve] -> drill -> replan -> drill
```

`compress` and `solve` are optional preparation operators. Only `drill` can turn the user's observed performance into mastery evidence, and only `replan` can revise an existing strategy.

## Installation

### Complete collection for all detected Agents

Node.js and `npx` are required.

```bash
npx -y skills add Wh1te358/skills-by-Wh1te -g --all
```

This repository currently contains the six Exam Hacker Skills above. `--all` is intentional: installing only `exam-hacker` leaves the router without its five required specialists.

### Codex only

Use the explicit list if you only want a global Codex installation, or if this repository later contains unrelated Skills:

```bash
npx -y skills add Wh1te358/skills-by-Wh1te -g -y --agent codex --skill exam-hacker exam-hacker-triage exam-hacker-compress exam-hacker-solve exam-hacker-drill exam-hacker-replan
```

Preview what the installer detects without installing:

```bash
npx -y skills add Wh1te358/skills-by-Wh1te --list
```

### Codex Python fallback

If `npx` is unavailable but Codex's built-in Skill installer exists, install all six paths in one command. Do not install only the router.

```bash
python "$HOME/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py" --repo "Wh1te358/skills-by-Wh1te" --ref "codex/exam-hacker-skill" --path exam-hacker exam-hacker-triage exam-hacker-compress exam-hacker-solve exam-hacker-drill exam-hacker-replan
```

### From a local clone

Run this from the repository root:

```bash
npx -y skills add . -g --all
```

Restart or open a new Agent session after installation. Then invoke:

```text
$exam-hacker
```

The router performs a strict installed-specialist check before it reads course state. It will report missing, malformed, or conflicting installations instead of silently falling back to the retired monolith.

## Recommended Course Workspace

Keep raw evidence separate from generated state:

```text
course-root/
  reference/
    textbook/
    slides/
    review-sheet/
    homework/
    past-papers/
    answer-keys/
  progress/
    00_survival-outline.md
    strategy.json
    mastery-evidence.jsonl
    artifacts/
    drills/
    history/
```

- `reference/` contains only pre-existing source material.
- `progress/` contains Agent-generated strategy, artifacts, drills, and append-only evidence.
- A filename or existing PDF is not proof that the Agent has read it.

## Usage

Initial triage:

```text
$exam-hacker
I have five days before my structural mechanics final, a target of 80, and 18 usable study hours. My materials are under reference/. Audit the evidence, ask me for the one-minute mastery snapshot, and give me only the first executable Sessions.
```

Start the next Session:

```text
$exam-hacker
Start my next Session. Hide the answer until I submit my work.
```

Solve one problem directly:

```text
$exam-hacker-solve
Solve this indeterminate-beam problem as a complete reproducible chain. Cite the supplied problem, theory, and answer-key anchors, and distinguish reference-verified steps from Agent-derived steps.
```

Compress one chain:

```text
$exam-hacker-compress
Compress the force-method chain from redundancy selection to final internal forces. Keep every transition reproducible and end with an answer-hidden retrieval probe.
```

## Evidence Rules

- No evidence-backed exam value means no confident priority or strategic abandonment.
- Strategic abandonment requires direct evidence, insufficient capacity, a downside, and a reversal condition.
- The mastery snapshot is a fast `0–3` behavior-anchored self-report, not a compulsory long diagnostic.
- Exposed answers and worked examples are `practice_only`; they do not prove mastery.
- Only observed, answer-hidden user performance may enter `mastery-evidence.jsonl`.
- OCR and contact sheets may locate pages, but they are not authoritative evidence for formulas, diagrams, answers, or scoring annotations.
- Scanned or image-only PDFs trigger rendered-page visual inspection. Claims are restricted to the exact pages inspected; targeted inspection cannot masquerade as a full-document audit.

## Current Scope

The current collection is optimized for calculation, derivation, proof, and other deterministic STEM chains. Whole-course A4 sheets, generic knowledge maps, broad question banks, and non-algorithmic memorization-course compression are intentionally outside this version rather than being weakly simulated inside the router.

## Validation Included

The repository includes:

- structural-mechanics fixtures for triage, compression, solving, drilling, and replanning;
- validators for strategy state, compression artifacts, solved-problem artifacts, mastery events, and replan transitions;
- integration results for the closed loop;
- a PDF readability detector that distinguishes text, mixed, scan-like, and no-readable-signal documents.
