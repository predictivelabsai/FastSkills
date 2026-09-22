"""FastSkills domain data layer (backend-agnostic via .database)."""
from __future__ import annotations
import json, re
from datetime import datetime, timezone

from .database import rows, row, execute, insert, tx, init_schema
from .mdconvert import markdown_to_doc, plain_text

CATEGORIES = ("Finance", "Trading", "Legal", "Marketing")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
  id TEXT PRIMARY KEY, email TEXT NOT NULL, name TEXT NOT NULL,
  is_admin INTEGER DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS skills(
  id {PK},
  slug TEXT NOT NULL,
  title TEXT NOT NULL,
  description TEXT DEFAULT '',
  category TEXT NOT NULL,
  author_label TEXT DEFAULT '',
  owner_id TEXT NOT NULL,
  visibility TEXT DEFAULT 'public',
  status TEXT DEFAULT 'published',
  tags TEXT DEFAULT '',
  content_json TEXT NOT NULL,
  markdown TEXT DEFAULT '',
  plain_text TEXT DEFAULT '',
  source_url TEXT DEFAULT '',
  license TEXT DEFAULT '',
  version INTEGER DEFAULT 1,
  seeded INTEGER DEFAULT 0,
  created_by TEXT, updated_by TEXT,
  created_at TEXT, updated_at TEXT, deleted_at TEXT,
  UNIQUE(owner_id, slug));
CREATE TABLE IF NOT EXISTS skill_versions(
  id {PK}, skill_id INTEGER, version INTEGER,
  title TEXT, content_json TEXT, markdown TEXT, created_by TEXT, created_at TEXT);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category, visibility, status);
CREATE INDEX IF NOT EXISTS idx_skills_owner ON skills(owner_id, deleted_at)
"""


def init():
    init_schema(SCHEMA)


# ── users ────────────────────────────────────────────────────────────────────
def provision(who: dict):
    execute(
        "INSERT INTO users(id,email,name,created_at) VALUES(?,?,?,?) "
        "ON CONFLICT(id) DO UPDATE SET email=excluded.email,name=excluded.name",
        (who["sub"], who["email"], who.get("name") or who["email"].split("@")[0], now()))


def get_user(uid):
    return row("SELECT * FROM users WHERE id=?", (uid,))


def is_admin(who):
    if not who:
        return False
    u = get_user(who["sub"])
    return bool(u and u.get("is_admin"))


# ── helpers ──────────────────────────────────────────────────────────────────
def _slugify(value):
    return re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-") or "skill"


def _unique_slug(owner_id, base, skill_id=None):
    slug, i = base, 2
    while True:
        clash = row("SELECT id FROM skills WHERE owner_id=? AND slug=?", (owner_id, slug))
        if not clash or (skill_id and clash["id"] == skill_id):
            return slug
        slug = f"{base}-{i}"; i += 1


def can_view(who, item):
    if not item or item["deleted_at"]:
        return False
    if item["visibility"] == "public" and item["status"] == "published":
        return True
    return bool(who and (item["owner_id"] == who["sub"] or is_admin(who)))


def can_edit(who, item):
    return bool(who and item and not item["deleted_at"]
                and (item["owner_id"] == who["sub"] or is_admin(who)))


# ── reads ────────────────────────────────────────────────────────────────────
def skill(sid):
    return row("SELECT s.*,u.name owner_name FROM skills s "
               "LEFT JOIN users u ON u.id=s.owner_id WHERE s.id=?", (sid,))


def visible_skill(who, sid):
    item = skill(sid)
    return item if can_view(who, item) else None


def catalog(category=None, q=None, author=None):
    where = ["visibility='public'", "status='published'", "deleted_at IS NULL"]
    args = []
    if category and category in CATEGORIES:
        where.append("category=?"); args.append(category)
    if author:
        where.append("author_label=?"); args.append(author)
    if q:
        where.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR plain_text LIKE ?)")
        like = f"%{q}%"; args += [like, like, like, like]
    return rows("SELECT s.*,u.name owner_name FROM skills s LEFT JOIN users u ON u.id=s.owner_id "
                f"WHERE {' AND '.join(where)} ORDER BY category,title", args)


def category_counts():
    found = rows("SELECT category,count(*) n FROM skills "
                 "WHERE visibility='public' AND status='published' AND deleted_at IS NULL "
                 "GROUP BY category")
    return {r["category"]: r["n"] for r in found}


def authors():
    return [r["author_label"] for r in rows(
        "SELECT DISTINCT author_label FROM skills WHERE author_label<>'' "
        "AND visibility='public' AND status='published' AND deleted_at IS NULL "
        "ORDER BY author_label")]


def mine(who):
    return rows("SELECT s.*,u.name owner_name FROM skills s LEFT JOIN users u ON u.id=s.owner_id "
                "WHERE s.owner_id=? AND s.deleted_at IS NULL ORDER BY s.updated_at DESC",
                (who["sub"],))


# ── writes ───────────────────────────────────────────────────────────────────
def create_skill(who, title="Untitled skill", category="Finance"):
    if category not in CATEGORIES:
        category = "Finance"
    slug = _unique_slug(who["sub"], _slugify(title))
    doc = json.dumps({"type": "doc", "content": [{"type": "paragraph"}]})
    ts = now()
    return insert(
        "INSERT INTO skills(slug,title,category,owner_id,visibility,status,content_json,"
        "created_by,updated_by,created_at,updated_at) "
        "VALUES(?,?,?,?,'private','draft',?,?,?,?,?)",
        (slug, title, category, who["sub"], doc, who["sub"], who["sub"], ts, ts))


def save_skill(who, sid, *, title, content_json, markdown, version,
               description=None, category=None, author_label=None,
               tags=None, visibility=None):
    current = skill(sid)
    if not current or not can_edit(who, current):
        return None
    if current["version"] != version:
        return {"conflict": True, "version": current["version"]}
    try:
        parsed = json.loads(content_json)
    except json.JSONDecodeError:
        raise ValueError("content_json")
    fields = {
        "title": title,
        "content_json": json.dumps(parsed),
        "markdown": markdown,
        "plain_text": plain_text(parsed),
    }
    if description is not None:
        fields["description"] = description
    if category in CATEGORIES:
        fields["category"] = category
    if author_label is not None:
        fields["author_label"] = author_label
    if tags is not None:
        fields["tags"] = tags
    if visibility in ("public", "private"):
        fields["visibility"] = visibility
    with tx() as s:
        s.execute(
            "INSERT INTO skill_versions(skill_id,version,title,content_json,markdown,created_by,created_at) "
            "VALUES(?,?,?,?,?,?,?)",
            (sid, current["version"], current["title"], current["content_json"],
             current["markdown"], who["sub"], now()))
        assignments = ",".join(f"{k}=?" for k in fields)
        s.execute(
            f"UPDATE skills SET {assignments},version=version+1,updated_by=?,updated_at=? "
            "WHERE id=? AND version=?",
            (*fields.values(), who["sub"], now(), sid, version))
    return skill(sid)


def set_status(who, sid, status):
    if status not in ("draft", "published"):
        raise ValueError("status")
    if not can_edit(who, skill(sid)):
        return False
    execute("UPDATE skills SET status=?,updated_by=?,updated_at=? WHERE id=?",
            (status, who["sub"], now(), sid))
    return True


def set_visibility(who, sid, visibility):
    if visibility not in ("public", "private"):
        raise ValueError("visibility")
    if not can_edit(who, skill(sid)):
        return False
    execute("UPDATE skills SET visibility=?,updated_by=?,updated_at=? WHERE id=?",
            (visibility, who["sub"], now(), sid))
    return True


def trash(who, sid):
    if can_edit(who, skill(sid)):
        execute("UPDATE skills SET deleted_at=? WHERE id=?", (now(), sid))
        return True
    return False


# ── seeding (idempotent upsert keyed on owner+slug) ──────────────────────────
def upsert_seed(owner_id, entry):
    slug = entry["slug"]
    doc = markdown_to_doc(entry["markdown"])
    content_json = json.dumps(doc)
    text = plain_text(doc)
    ts = now()
    existing = row("SELECT id,seeded FROM skills WHERE owner_id=? AND slug=?", (owner_id, slug))
    if existing:
        if not existing["seeded"]:
            return existing["id"]  # user has taken it over; don't clobber
        execute(
            "UPDATE skills SET title=?,description=?,category=?,author_label=?,tags=?,"
            "content_json=?,markdown=?,plain_text=?,source_url=?,license=?,updated_at=? "
            "WHERE id=?",
            (entry["title"], entry["description"], entry["category"], entry["author_label"],
             entry["tags"], content_json, entry["markdown"], text, entry.get("source_url", ""),
             entry.get("license", ""), ts, existing["id"]))
        return existing["id"]
    return insert(
        "INSERT INTO skills(slug,title,description,category,author_label,owner_id,visibility,"
        "status,tags,content_json,markdown,plain_text,source_url,license,seeded,"
        "created_by,updated_by,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,'public','published',?,?,?,?,?,?,1,?,?,?,?)",
        (slug, entry["title"], entry["description"], entry["category"], entry["author_label"],
         owner_id, entry["tags"], content_json, entry["markdown"], text,
         entry.get("source_url", ""), entry.get("license", ""), owner_id, owner_id, ts, ts))


init()
