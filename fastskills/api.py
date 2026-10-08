"""Public read-only API (FastAPI sub-app mounted at /api), Fast* family style."""
from __future__ import annotations
from fastapi import FastAPI, HTTPException

from . import db, strategies
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


def _r(v, n=3):
    return None if v is None else round(v, n)


def _strategy(item):
    m = {k: (_r(v) if isinstance(v, float) else v) for k, v in strategies.metrics(item).items()}
    return {"id": item["id"], "slug": item["slug"], "name": item["title"],
            "user": item.get("owner_name") or "", "description": item.get("description") or "",
            "annualised_return_pct": m["annualised_pct"],
            "annualised_compound_pct": m["annualised_compound_pct"],
            "return_pct": m["return_pct"], "benchmark": m["benchmark"],
            "benchmark_return_pct": m["benchmark_return_pct"], "alpha_pct": m["alpha_pct"],
            "live_start": m["live_start"], "days_running": m["days_running"],
            "trading_days": m["trading_days"], "as_of": m["as_of"], "source": m["source"],
            "url": f"/skills/{item['id']}", "markdown_url": f"/skills/{item['id']}/download",
            "alpatrade_import_url": f"/strategies/{item['id']}/alpatrade-import"}


@api.get("/strategies")
def list_strategies():
    """Public strategies on the leaderboard (annualised = return × 252 / trading days)."""
    return {"strategies": [_strategy(i) for i in db.leaderboard()]}


@api.get("/strategies/{sid}")
def get_strategy(sid: int):
    item = next((i for i in db.leaderboard() if i["id"] == sid), None)
    if not item:
        raise HTTPException(status_code=404, detail="Strategy not found")
    full = db.skill(sid)
    return {**_strategy(item), "markdown": full["markdown"],
            "alpatrade_import": strategies.alpatrade_import(full)}
