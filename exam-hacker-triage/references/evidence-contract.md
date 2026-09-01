# Evidence Contract

Apply this contract to every priority, frequency, scoring, or abandonment claim.

## Source Inventory

Assign stable source IDs and record:

| Source ID | File or statement | Type | Readability | Authority | Usable anchors | Notes |
|---|---|---|---|---|---|---|

States:

- `verified`: relevant content was read through embedded text or rendered-page vision and its anchor resolves;
- `user-confirmed`: the user explicitly supplied the fact;
- `unreadable`: the source exists but relevant content could not be inspected;
- `missing`: needed evidence was not provided.

Generated notes and planned outputs are not raw evidence. A filename alone does not make an image or scanned PDF verified.

## Scanned And Mixed PDFs

Empty or sparse text extraction is a detection signal, not proof that a PDF is unreadable. When rendering and multimodal inspection are available, use this order:

1. detect text, image, and empty-page signals;
2. use OCR or contact sheets only to locate candidate pages;
3. render the relevant pages at readable resolution;
4. visually inspect each page used by a claim;
5. record a page-level inspection receipt.

For scanned or mixed PDFs, `source_materials[].inspection` contains:

```json
{
  "document_mode": "scan-likely",
  "method": "vision",
  "pages_total": 60,
  "coverage": "targeted",
  "pages_inspected": [1, 12, 27],
  "ocr_role": "index_only"
}
```

Allowed methods are `embedded_text`, `vision`, and `hybrid`. Coverage is `targeted` or `full`. OCR role is `none` or `index_only`; OCR output is never a verified source by itself.

Every reference to a `vision` or `hybrid` source must contain a 1-based PDF page or slide anchor, and every referenced page must appear in `pages_inspected`. A targeted inspection supports claims only about those pages. A whole-document absence, distribution, or frequency claim requires `coverage: "full"` with every page inspected.

## Evidence References

Use the narrowest real locator:

- `S01:p.12`;
- `S02:slide 8`;
- `S03:Q4`;
- `S04:heading "Virtual Work" + keyword "unit load"`;
- `U01:user-confirmed`.

Never invent page numbers, questions, teacher emphasis, scoring rules, or source identities.

## Claim Classes

| Class | Meaning | Can independently justify abandonment? |
|---|---|---|
| `verified-source` | Readable course source with a resolvable anchor | Yes, subject to the gate |
| `user-confirmed` | Explicit user statement | Only with its stated limitation |
| `inference` | Agent-derived pattern or prerequisite judgment | No |
| `unknown` | Missing, unreadable, or conflicting evidence | No |

The mastery snapshot is user-confirmed evidence about current ability only. It is not evidence of exam frequency or score weight.

## Claims Requiring Evidence

Attach evidence to:

- scope and score weights;
- teacher emphasis and likely tested content;
- high or low frequency;
- scoring keywords and process marks;
- must-win or abandonable status;
- expected exam return used to rank topics.

Absence from a limited sample is not low-frequency evidence.

## Decision Record

| Topic | Decision | Exam-value refs | Mastery evidence | Inference | Confidence | Risk if wrong | Reversal condition |
|---|---|---|---|---|---|---|---|

Allowed decisions: `must-win`, `high-priority`, `provisional`, `defer`, `strategic-abandonment`.

## Strategic-Abandonment Gate

Use `strategic-abandonment` only when all conditions hold:

1. Capacity cannot cover every candidate topic.
2. Retained topics have stronger evidence-backed return or prerequisite value.
3. The abandoned topic has direct exclusion or low-weight evidence, or the user explicitly accepts the documented gap.
4. The risk if wrong is stated.
5. A concrete reversal condition is stated.

If any condition fails, use `provisional` or `defer`.

## Conflicts And Completion

Show source conflicts. Prefer course-specific official scope or rubric, then instructor review material, then verified papers and answers, then textbook or homework, then senior notes; authority order does not erase unresolved conflict.

Before finishing:

- every source ID resolves or is explicitly user-confirmed;
- high-stakes claims have evidence references;
- inference is visible;
- exam value and mastery remain separate;
- every abandonment passes all five conditions;
- unreadable and missing sources remain visible gaps.
- every vision-backed claim resolves to a visually inspected page, and targeted coverage is not presented as a full-document audit.
