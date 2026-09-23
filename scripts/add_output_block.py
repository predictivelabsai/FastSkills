#!/usr/bin/env python3
"""Ensure every Finance/Trading seed skill mandates table + PDF/CSV output.

Appends a standard "## Presenting results" block to any seed/finance or
seed/trading skill that doesn't already contain one. Idempotent — files the
genericization agents already wrote (which include the block) are skipped.
"""
from __future__ import annotations
from pathlib import Path

SEED = Path(__file__).resolve().parents[1] / "seed"
MARKER = "## Presenting results"
BLOCK = """

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading.
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows), and generate them when asked.
- Never invent figures. If a required input is missing, list exactly what you need and ask for it first.
"""


def main():
    changed = 0
    for sub in ("finance", "trading"):
        d = SEED / sub
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            if MARKER in text:
                continue
            path.write_text(text.rstrip() + "\n" + BLOCK, encoding="utf-8")
            changed += 1
            print(f"+ output block -> {path.relative_to(SEED)}")
    print(f"updated {changed} file(s)")


if __name__ == "__main__":
    main()
