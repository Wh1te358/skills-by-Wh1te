# Scanned PDF Evidence Protocol

Use this protocol only when a PDF has sparse or empty extracted text, visible page images, or mixed text-and-scan pages.

## Capability Ladder

1. Run `scripts/inspect_pdf_readability.py <file.pdf>`.
2. For `text`, continue with ordinary extraction while preserving page anchors.
3. When `visual_followup_required` is true, use OCR or low-resolution contact sheets only to locate candidate pages. This includes `mixed`, `scan-likely`, and `no-readable-signal`; the last state means the parser found no trustworthy signal, not that the rendered page is blank.
4. Render every page used by a claim to a readable PNG with Poppler or an equivalent renderer.
5. Inspect those rendered pages with the available multimodal image capability.
6. Record `inspection` metadata and page-level evidence anchors.

Do not hardcode one vendor-specific vision tool. Use the host's available PDF rendering and image-inspection capability. If either is unavailable, record the source as a material gap rather than pretending that OCR completed the audit.

## Evidence Boundary

- OCR is an index, never the final authority for formulas, tables, diagrams, handwritten work, symbols, or scoring annotations.
- A contact sheet may identify a candidate page but is too lossy to verify small text or equations.
- `coverage: "targeted"` supports only inspected-page claims.
- `coverage: "full"` requires every 1-based PDF page in `pages_inspected`.
- Absence and frequency claims require full coverage; a search miss is not evidence of absence.
- Preserve discrepancies between embedded text, OCR, and the rendered page. The rendered page controls what the source visibly states.

## Time-Critical Selection

When three days or less remain, select pages that can change a decision:

- table of contents or question index;
- teacher review scope and scoring statements;
- problems and answer pages bound to the next Session;
- pages needed to validate a proposed abandonment or repair a missing solution link.

Do not visually transcribe an entire answer book merely to mark it "read". Expand coverage only when the next decision requires it or the user requests a full audit.

## Temporary Files

Render into an isolated temporary directory. Never mix page PNGs, OCR text, or contact sheets into raw course evidence. Delete scratch renders after the claims and anchors have been checked.
