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
  sub_label TEXT DEFAULT '',
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
CREATE TABLE IF NOT EXISTS app_meta(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS favourites(
  user_id TEXT NOT NULL, skill_id INTEGER NOT NULL, created_at TEXT,
  PRIMARY KEY(user_id, skill_id));
CREATE INDEX IF NOT EXISTS idx_favourites_user ON favourites(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category, visibility, status);
CREATE INDEX IF NOT EXISTS idx_skills_owner ON skills(owner_id, deleted_at)
"""

# Columns added after the initial schema shipped; applied idempotently on init.
_MIGRATIONS = [
    "ALTER TABLE skills ADD COLUMN sub_label TEXT DEFAULT ''",
    "ALTER TABLE skills ADD COLUMN forked_from INTEGER",
    "ALTER TABLE skills ADD COLUMN forked_from_title TEXT DEFAULT ''",
]


def init():
    init_schema(SCHEMA)
    for ddl in _MIGRATIONS:
        try:
            execute(ddl)  # each runs in its own tx; a duplicate-column error is fine
        except Exception:
            pass


def get_meta(key):
    r = row("SELECT value FROM app_meta WHERE key=?", (key,))
    return r["value"] if r else None


def set_meta(key, value):
    execute("INSERT INTO app_meta(key,value) VALUES(?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


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


def catalog(category=None, q=None, author=None, sub=None):
    where = ["visibility='public'", "status='published'", "deleted_at IS NULL"]
    args = []
    if category and category in CATEGORIES:
        where.append("category=?"); args.append(category)
    if sub:
        where.append("sub_label=?"); args.append(sub)
    if author:
        where.append("author_label=?"); args.append(author)
    if q:
        where.append("(title LIKE ? OR description LIKE ? OR tags LIKE ? OR plain_text LIKE ?)")
        like = f"%{q}%"; args += [like, like, like, like]
    return rows("SELECT s.*,u.name owner_name FROM skills s LEFT JOIN users u ON u.id=s.owner_id "
                f"WHERE {' AND '.join(where)} ORDER BY category,sub_label,title", args)


def sublabels(category):
    """Sub-labels present in a category (public+published), with counts."""
    return rows(
        "SELECT sub_label, count(*) n FROM skills "
        "WHERE category=? AND sub_label<>'' AND visibility='public' "
        "AND status='published' AND deleted_at IS NULL "
        "GROUP BY sub_label ORDER BY sub_label", (category,))


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


# ── favourites / bookmarks ───────────────────────────────────────────────────
def favourite_ids(who):
    if not who:
        return set()
    return {r["skill_id"] for r in
            rows("SELECT skill_id FROM favourites WHERE user_id=?", (who["sub"],))}


def is_favourite(who, sid):
    if not who:
        return False
    return bool(row("SELECT 1 FROM favourites WHERE user_id=? AND skill_id=?", (who["sub"], sid)))


def toggle_favourite(who, sid):
    """Add or remove a bookmark; returns the new state (True = favourited)."""
    if not who or not can_view(who, skill(sid)):
        return False
    if is_favourite(who, sid):
        execute("DELETE FROM favourites WHERE user_id=? AND skill_id=?", (who["sub"], sid))
        return False
    execute("INSERT INTO favourites(user_id,skill_id,created_at) VALUES(?,?,?) "
            "ON CONFLICT(user_id,skill_id) DO NOTHING", (who["sub"], sid, now()))
    return True


def _fav_visible():
    return "((s.visibility='public' AND s.status='published') OR s.owner_id=?)"


def favourites(who, category=None):
    where = ["f.user_id=?", "s.deleted_at IS NULL", _fav_visible()]
    args = [who["sub"], who["sub"]]
    if category in CATEGORIES:
        where.append("s.category=?"); args.append(category)
    return rows(
        "SELECT s.*,u.name owner_name FROM favourites f JOIN skills s ON s.id=f.skill_id "
        "LEFT JOIN users u ON u.id=s.owner_id "
        f"WHERE {' AND '.join(where)} ORDER BY f.created_at DESC", args)


def favourite_counts(who):
    found = rows(
        "SELECT s.category, count(*) n FROM favourites f JOIN skills s ON s.id=f.skill_id "
        f"WHERE f.user_id=? AND s.deleted_at IS NULL AND {_fav_visible()} GROUP BY s.category",
        (who["sub"], who["sub"]))
    return {r["category"]: r["n"] for r in found}


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
               description=None, category=None, sub_label=None, author_label=None,
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
    if sub_label is not None:
        fields["sub_label"] = sub_label
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


# ── clone / fork ─────────────────────────────────────────────────────────────
def clone_skill(who, source_id):
    """Fork any viewable skill into a fresh private draft owned by `who`.
    Returns the new skill id, or None if the source isn't viewable."""
    src = skill(source_id)
    if not can_view(who, src):
        return None
    base = _slugify((src["title"] or "skill") + "-copy")
    slug = _unique_slug(who["sub"], base)
    ts = now()
    return insert(
        "INSERT INTO skills(slug,title,description,category,sub_label,author_label,owner_id,"
        "visibility,status,tags,content_json,markdown,plain_text,source_url,license,seeded,"
        "forked_from,forked_from_title,created_by,updated_by,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,'private','draft',?,?,?,?,?,?,0,?,?,?,?,?,?)",
        (slug, src["title"], src["description"], src["category"], src["sub_label"],
         src["author_label"], who["sub"], src["tags"], src["content_json"], src["markdown"],
         src["plain_text"], src["source_url"], src["license"], source_id, src["title"],
         who["sub"], who["sub"], ts, ts))


# ── version history ──────────────────────────────────────────────────────────
def versions(sid):
    """History newest-first: the live row as the current version, then each
    prior snapshot recorded on save."""
    cur = skill(sid)
    if not cur:
        return []
    history = [{"version": cur["version"], "title": cur["title"],
                "created_at": cur["updated_at"], "created_by": cur["updated_by"],
                "current": True, "version_id": None}]
    for r in rows("SELECT id,version,title,created_at,created_by FROM skill_versions "
                  "WHERE skill_id=? ORDER BY version DESC", (sid,)):
        history.append({**r, "current": False, "version_id": r["id"]})
    return history


def version_snapshot(sid, version_id):
    return row("SELECT * FROM skill_versions WHERE id=? AND skill_id=?", (version_id, sid))


def restore_version(who, sid, version_id):
    cur = skill(sid)
    if not can_edit(who, cur):
        return None
    snap = version_snapshot(sid, version_id)
    if not snap:
        return None
    return save_skill(who, sid, title=snap["title"], content_json=snap["content_json"],
                      markdown=snap["markdown"], version=cur["version"])


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


def count_seeded():
    r = row("SELECT count(*) n FROM skills WHERE seeded=1 AND deleted_at IS NULL")
    return (r["n"] if r else 0) or 0


def seed_bulk(owner_id, owner_name, entries):
    """Upsert all seed entries over a SINGLE connection/transaction.

    Per-query connections make remote-Postgres seeding of 100+ rows very slow;
    doing it in one transaction keeps startup fast. A skill a user has taken
    over (seeded=0) is never clobbered.
    """
    ts = now()
    n = 0
    with tx() as s:
        s.execute(
            "INSERT INTO users(id,email,name,created_at) VALUES(?,?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET email=excluded.email,name=excluded.name",
            (owner_id, owner_id, owner_name or owner_id.split("@")[0], ts))
        for entry in entries:
            doc = markdown_to_doc(entry["markdown"])
            content_json = json.dumps(doc)
            text = plain_text(doc)
            existing = s.fetchone(
                "SELECT id,seeded FROM skills WHERE owner_id=? AND slug=?",
                (owner_id, entry["slug"]))
            if existing:
                if not existing["seeded"]:
                    continue
                s.execute(
                    "UPDATE skills SET title=?,description=?,category=?,sub_label=?,author_label=?,"
                    "tags=?,content_json=?,markdown=?,plain_text=?,source_url=?,license=?,updated_at=? "
                    "WHERE id=?",
                    (entry["title"], entry["description"], entry["category"],
                     entry.get("sub_label", ""), entry["author_label"], entry["tags"],
                     content_json, entry["markdown"], text, entry.get("source_url", ""),
                     entry.get("license", ""), ts, existing["id"]))
            else:
                s.execute(
                    "INSERT INTO skills(slug,title,description,category,sub_label,author_label,"
                    "owner_id,visibility,status,tags,content_json,markdown,plain_text,source_url,"
                    "license,seeded,created_by,updated_by,created_at,updated_at) "
                    "VALUES(?,?,?,?,?,?,?,'public','published',?,?,?,?,?,?,1,?,?,?,?)",
                    (entry["slug"], entry["title"], entry["description"], entry["category"],
                     entry.get("sub_label", ""), entry["author_label"], owner_id, entry["tags"],
                     content_json, entry["markdown"], text, entry.get("source_url", ""),
                     entry.get("license", ""), owner_id, owner_id, ts, ts))
            n += 1
    return n

# NOTE: init() is intentionally NOT called at import time. Importing this module
# must never touch the database (a slow/unreachable Postgres would block the web
# server from binding its port). Startup runs init() in a background thread.
