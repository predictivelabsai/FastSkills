"""Runs after test_smoke (it imports app, whose startup seeds the DB).

Mobile nav (kept from v0.2.1) and the v0.2.2 removal of the strategy Leaderboard
(moved to AlpaTrade: alpatrade.chat/leaderboard)."""
import os

os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("FASTSKILLS_DB", "data/test-fastskills.sqlite")

from fastskills import db, seed  # noqa: E402

db.init()


def _client():
    from starlette.testclient import TestClient
    import app as webapp
    return TestClient(webapp.app)


def test_hamburger_nav_on_landing():
    home = _client().get("/")
    assert home.status_code == 200
    assert 'class="navburger"' in home.text and 'aria-controls="fs-navlinks"' in home.text
    assert 'id="fs-navlinks"' in home.text
    assert "@media(max-width:760px)" in home.text


def test_leaderboard_and_strategy_routes_are_gone():
    c = _client()
    home = c.get("/").text
    assert 'href="/leaderboard"' not in home and "Leaderboard" not in home
    for path in ("/leaderboard", "/api/strategies", "/strategies/new", "/strategies/1/alpatrade-import"):
        assert c.get(path, follow_redirects=False).status_code in (404, 405, 303, 307), path
    assert c.get("/leaderboard", follow_redirects=False).status_code == 404


def test_retired_seed_strategy_is_soft_deleted():
    ts = db.now()
    db.execute("INSERT INTO skills(slug,title,description,category,owner_id,visibility,status,"
               "content_json,markdown,plain_text,seeded,created_at,updated_at) "
               "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",
               ("mag7-btd-live", "Mag-7 BTD", "d", "Trading", "seed@example.com", "public",
                "published", "{}", "x", "x", 1, ts, ts))
    seed.retire_seeds()
    r = db.row("SELECT deleted_at FROM skills WHERE slug='mag7-btd-live' AND seeded=1 "
               "ORDER BY id DESC LIMIT 1")
    assert r and r["deleted_at"]
