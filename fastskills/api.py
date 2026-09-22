"""Public read-only API (FastAPI sub-app mounted at /api), Fast* family style."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException

from . import db
from .version import VERSION

api = FastAPI(title="FastSkills API", version=VERSION,
              description="Read-only access to the public FastSkills catalog.")


def _public(item):
    return {k: item[k] for k in (
        "id", "slug", "title", "description", "category", "sub_label", "author_label",
        "tags", "source_url", "license", "version", "updated_at")}


@api.get("/skills")
def list_skills(category: str | None = None, q: str | None = None, author: str | None = None):
    return {"skills": [_public(i) for i in db.catalog(category, q, author)]}


@api.get("/categories")
def categories():
    counts = db.category_counts()
    return {"categories": [{"name": c, "count": counts.get(c, 0)} for c in db.CATEGORIES]}


@api.get("/skills/{sid}")
def get_skill(sid: int):
    item = db.skill(sid)
    if not item or not db.can_view(None, item):
        raise HTTPException(status_code=404, detail="Skill not found")
    return {**_public(item), "markdown": item["markdown"], "content_json": item["content_json"]}
