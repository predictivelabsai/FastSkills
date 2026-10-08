"""Load the committed ``seed/`` tree into the database (idempotent).

Every seeded skill is a Markdown file with normalized YAML frontmatter:

    ---
    title: Cold email
    description: Write cold emails that get replies.
    category: Marketing
    author: Corey Haines
    tags: outbound, email
    license: MIT
    source: https://github.com/coreyhaines31/marketingskills
    ---
    <skill body>

Seeded skills are owned by SEED_OWNER and are public+published. Re-running
upserts by (owner, slug); a skill a user has taken over is never clobbered.

A seed file with ``kind: strategy`` becomes a leaderboard strategy. Its live
performance snapshot comes from ``seed/strategy_stats.json`` (keyed by slug;
regenerate from AlpaTrade with ``scripts/refresh_strategy_stats.py``). A snapshot
never overwrites a newer one already in the database.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

from . import db

SEED_OWNER = os.getenv("FASTSKILLS_SEED_OWNER", "kaljuvee@gmail.com")
SEED_OWNER_NAME = os.getenv("FASTSKILLS_SEED_OWNER_NAME", "Julian Kaljuvee")
SEED_DIR = Path(os.getenv("FASTSKILLS_SEED_DIR", Path(__file__).resolve().parent.parent / "seed"))

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _parse(text):
    m = _FRONTMATTER.match(text)
    if not m:
        return {}, text
    meta, body = {}, m.group(2)
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip().lower()] = value.strip().strip('"').strip("'")
    return meta, body


def _slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-") or "skill"


def _entries():
    entries = []
    for path in sorted(SEED_DIR.rglob("*.md")):
        meta, body = _parse(path.read_text(encoding="utf-8"))
        def _canon(name):
            name = (name or "").strip()
            return next((c for c in db.CATEGORIES if c.lower() == name.lower()), None)
        category = _canon(meta.get("category")) or _canon(path.parent.name)
        if not category:
            continue
        title = meta.get("title") or meta.get("name") or path.stem.replace("-", " ").title()
        entries.append({
            "slug": _slugify(meta.get("slug") or path.stem),
            "title": title,
            "description": meta.get("description", "")[:400],
            "category": category,
            "sub_label": (meta.get("sublabel") or meta.get("sub_label") or "").strip(),
            "author_label": meta.get("author", ""),
            "tags": meta.get("tags", ""),
            "markdown": body.strip(),
            "source_url": meta.get("source", ""),
            "license": meta.get("license", ""),
            "kind": (meta.get("kind") or "skill").strip().lower()
            if (meta.get("kind") or "skill").strip().lower() in db.KINDS else "skill",
        })
    return entries


def _fingerprint(entries):
    import hashlib
    h = hashlib.sha256()
    for e in sorted(entries, key=lambda e: e["slug"]):
        h.update(("|".join((e["slug"], e["title"], e["description"], e["category"],
                            e["sub_label"], e["author_label"], e["tags"],
                            e["markdown"], e.get("kind", "skill"))) + "\n").encode("utf-8"))
    return h.hexdigest()


def seed_strategy_stats():
    """Upsert the committed performance snapshots for seeded strategies."""
    path = SEED_DIR / "strategy_stats.json"
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for slug, stats in (data.get("strategies") or {}).items():
        found = db.find_skill(SEED_OWNER, slug)
        if found and db.upsert_strategy_stats(found["id"], stats):
            n += 1
    return n


def run(force=None):
    """Load seed/ into the DB. Idempotent and fast on reboot: if the catalog is
    already fully seeded it returns immediately without touching the DB. Set
    FASTSKILLS_FORCE_SEED=1 (or pass force=True) to re-upsert every entry."""
    db.init()  # ensure schema/tables exist (idempotent)
    if not SEED_DIR.is_dir():
        return 0
    if force is None:
        force = os.getenv("FASTSKILLS_FORCE_SEED", "").lower() in ("1", "true", "yes")
    entries = _entries()
    if not entries:
        return 0
    fp = _fingerprint(entries)
    # Re-seed when the seed content has changed (new skills, edited labels, …),
    # not merely when the row count matches; skip fast when nothing changed.
    if not force and db.count_seeded() >= len(entries) and db.get_meta("seed_fingerprint") == fp:
        seed_strategy_stats()
        return 0
    n = db.seed_bulk(SEED_OWNER, SEED_OWNER_NAME, entries)
    db.set_meta("seed_fingerprint", fp)
    seed_strategy_stats()
    return n


if __name__ == "__main__":
    print(f"Seeded {run()} skills from {SEED_DIR}")
