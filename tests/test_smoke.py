"""Smoke tests — run against SQLite in a temp dir so no external DB is needed.

    DB_TYPE=sqlite FASTSKILLS_DB=/tmp/t.sqlite pytest -q
"""
import json
import os

os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("FASTSKILLS_DB", "data/test-fastskills.sqlite")

from fastskills import db, seed, mdconvert  # noqa: E402


def _who(email="tester@example.com"):
    who = {"sub": email, "email": email, "name": "Tester"}
    db.provision(who)
    return who


def test_markdown_roundtrip():
    doc = mdconvert.markdown_to_doc("# Title\n\nHello **world**\n\n- a\n- b")
    assert doc["type"] == "doc"
    assert "world" in mdconvert.plain_text(doc)


def test_seed_and_catalog():
    n = seed.run()
    assert n > 0
    counts = db.category_counts()
    for c in db.CATEGORIES:
        assert c in counts and counts[c] > 0


def test_create_edit_publish_and_visibility():
    who = _who()
    sid = db.create_skill(who, "Unit Test Skill", "Trading")
    # a fresh skill is private+draft and not in the public catalog
    assert all(s["id"] != sid for s in db.catalog())
    doc = json.dumps({"type": "doc", "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "hi"}]}]})
    saved = db.save_skill(who, sid, title="Unit Test Skill", content_json=doc,
                          markdown="hi", version=1, visibility="public")
    assert saved["version"] == 2
    # stale version conflicts
    conflict = db.save_skill(who, sid, title="x", content_json="{}", markdown="x", version=1)
    assert conflict["conflict"] is True
    db.set_status(who, sid, "published")
    assert any(s["id"] == sid for s in db.catalog("Trading"))
    # access control: a stranger cannot edit
    other = _who("stranger@example.com")
    assert db.can_edit(other, db.skill(sid)) is False
    db.trash(who, sid)
