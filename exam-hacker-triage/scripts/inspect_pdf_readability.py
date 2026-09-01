#!/usr/bin/env python3
"""Detect whether a PDF is text-readable, mixed, or scan-like."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover - depends on host runtime
    raise SystemExit(
        "MISSING DEPENDENCY: install pypdf or use the host's native PDF inspection capability"
    ) from exc


CONTRACT_VERSION = "exam-hacker-pdf-inspection/v1"


def page_image_count(page: Any) -> int:
    try:
        return len(page.images)
    except Exception:
        return 0


def inspect_pdf(path: Path, minimum_text_chars: int) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"PDF does not exist: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {path}")

    reader = PdfReader(path)
    if reader.is_encrypted and reader.decrypt("") == 0:
        raise ValueError("PDF is encrypted and cannot be opened without a password")

    pages: list[dict[str, Any]] = []
    for page_number, page in enumerate(reader.pages, start=1):
        extraction_error = None
        try:
            extracted = page.extract_text() or ""
        except Exception as exc:
            extracted = ""
            extraction_error = type(exc).__name__
        text_chars = len("".join(extracted.split()))
        images = page_image_count(page)

        if text_chars >= minimum_text_chars:
            signal = "text"
        elif images > 0:
            signal = "scan-like"
        elif text_chars > 0:
            signal = "sparse-text"
        else:
            signal = "no-readable-signal"

        page_result: dict[str, Any] = {
            "page": page_number,
            "text_chars": text_chars,
            "image_count": images,
            "signal": signal,
        }
        if extraction_error:
            page_result["extraction_error"] = extraction_error
        pages.append(page_result)

    page_total = len(pages)
    if page_total == 0:
        raise ValueError("PDF has no pages")

    text_pages = [item["page"] for item in pages if item["signal"] == "text"]
    scan_pages = [item["page"] for item in pages if item["signal"] == "scan-like"]
    sparse_pages = [item["page"] for item in pages if item["signal"] == "sparse-text"]
    no_signal_pages = [item["page"] for item in pages if item["signal"] == "no-readable-signal"]

    scan_ratio = len(scan_pages) / page_total
    non_text_pages = scan_pages + sparse_pages + no_signal_pages
    if scan_ratio >= 0.8:
        classification = "scan-likely"
    elif scan_pages or (text_pages and non_text_pages):
        classification = "mixed"
    elif len(text_pages) == page_total:
        classification = "text"
    else:
        classification = "no-readable-signal"

    text_counts = [item["text_chars"] for item in pages]
    return {
        "contract_version": CONTRACT_VERSION,
        "path": str(path.resolve()),
        "pages_total": page_total,
        "classification": classification,
        "minimum_text_chars": minimum_text_chars,
        "summary": {
            "text_pages": len(text_pages),
            "scan_like_pages": len(scan_pages),
            "sparse_text_pages": len(sparse_pages),
            "no_readable_signal_pages": len(no_signal_pages),
            "scan_like_ratio": round(scan_ratio, 4),
            "median_text_chars": statistics.median(text_counts),
            "total_text_chars": sum(text_counts),
        },
        "page_groups": {
            "text": text_pages,
            "scan_like": scan_pages,
            "sparse_text": sparse_pages,
            "no_readable_signal": no_signal_pages,
        },
        # Only an all-text document is safe to treat as text-readable without
        # looking at rendered pages. Empty/sparse extraction is itself a reason
        # to attempt visual inspection, even when the parser sees no image XObject.
        "visual_followup_required": classification != "text",
        "pages": pages,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path, help="PDF to inspect")
    parser.add_argument(
        "--minimum-text-chars",
        type=int,
        default=80,
        help="Minimum non-whitespace characters for a page to count as text-readable",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Omit per-page details while keeping page groups",
    )
    args = parser.parse_args()

    if args.minimum_text_chars < 1:
        print("INVALID: --minimum-text-chars must be positive", file=sys.stderr)
        return 2

    try:
        result = inspect_pdf(args.pdf.resolve(), args.minimum_text_chars)
    except Exception as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1

    if args.summary_only:
        result.pop("pages", None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
