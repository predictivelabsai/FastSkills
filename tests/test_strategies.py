"""Strategies + leaderboard — SQLite, no network."""
import json
import os

os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("FASTSKILLS_DB", "data/test-fastskills.sqlite")

from pathlib import Path  # noqa: E402

from fastskills import db, seed, strategies  # noqa: E402

db.init()
SEED_MD = Path(__file__).resolve().parent.parent / "seed" / "trading" / "mag7-btd-live.md"
STATS = Path(__file__).resolve().parent.parent / "seed" / "strategy_stats.json"


def _who(email):
    who = {"sub": email, "email": email, "name": email.split("@")[0].title()}
    db.provision(who)
    return who


def test_annualise_matches_alpatrade_convention():
    a = strategies.annualise(2.946, 10)
    assert round(a["simple_pct"], 2) == 74.24          # 2.946 × 252 / 10
    assert a["compound_pct"] > a["simple_pct"]
    assert strategies.annualise(None, 10)["simple_pct"] is None
    assert strategies.annualise(1.0, 0)["simple_pct"] is None


def test_metrics_alpha_and_days_running():
    from datetime import date
    m = strategies.metrics({"live_start": "2026-09-24", "as_of": "2026-10-07", "return_pct": 2.946,
                            "benchmark_return_pct": 1.305, "trading_days": 10},
                           today=date(2026, 10, 8))
    assert round(m["alpha_pct"], 3) == 1.641
    assert m["days_running"] == 14
    assert strategies.metrics(None)["has_data"] is False


def test_seed_skill_params_block_matches_alpatrade_v2():
    meta, body = seed._parse(SEED_MD.read_text(encoding="utf-8"))
    assert meta["kind"] == "strategy" and meta["category"] == "Trading"
    block = strategies.extract_params(body)
    p, e = block["params"], block["execution"]
    assert block["config_version"] == 2
    assert p["symbols"] == ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA"]
    assert (p["dip"], p["ref"], p["tp"], p["sl"]) == (3.0, "high20", 8.0, 1.5)
    assert (p["min_hold"], p["max_hold"], p["pos_frac"]) == (3, 3, 0.142857)
    assert (p["entry_window"], p["close_window"], p["max_exposure"]) == ("15-5", "15-2", 0.0)
    x = e["extended_hours_exit"]
    assert x["enabled"] is True and x["discount_bps"] == 15 and x["max_reprices"] == 2
    assert x["fallback"] == "market_day_at_regular_open"
    # the editor drops the ```json info string on save — still parses
    assert strategies.extract_params(body.replace("```json", "```"))["params"] == p


def test_seeded_strategy_is_public_on_leaderboard_with_snapshot():
    seed.run(force=True)
    board = db.leaderboard()
    row = next(r for r in board if r["slug"] == "mag7-btd-live")
    assert row["owner_name"] == seed.SEED_OWNER_NAME
    snap = json.loads(STATS.read_text())["strategies"]["mag7-btd-live"]
    assert row["as_of"] == snap["as_of"] and row["return_pct"] == snap["return_pct"]
    # an older snapshot never overwrites a newer one
    assert db.upsert_strategy_stats(row["id"], {**snap, "as_of": "2000-01-01"}) is False


def test_multiple_strategies_visibility_toggle():
    owner, other = _who("quant@example.com"), _who("viewer@example.com")
    a, b = db.create_strategy(owner, "Alpha One"), db.create_strategy(owner, "Beta Two")
    assert {r["id"] for r in db.my_strategies(owner)} >= {a, b}
    board_ids = lambda: {r["id"] for r in db.leaderboard()}  # noqa: E731
    assert a not in board_ids() and b not in board_ids()       # new strategies start private drafts
    db.set_strategy_visibility(owner, a, "public")
    assert a in board_ids() and b not in board_ids()            # public also publishes
    assert db.set_strategy_visibility(other, a, "private") is False  # only the owner can toggle
    db.set_strategy_visibility(owner, a, "private")
    assert a not in board_ids()
    # a plain skill can be turned into a strategy through save_skill(kind=...)
    sid = db.create_skill(owner, "Plain skill", "Trading")
    db.save_skill(owner, sid, title="Plain skill", content_json='{"type":"doc"}', markdown="x",
                  version=1, kind="strategy")
    assert db.skill(sid)["kind"] == "strategy"
    for x in (a, b, sid):
        db.trash(owner, x)


def test_routes_render():
    from starlette.testclient import TestClient
    import app as webapp
    seed.run(force=True)
    c = TestClient(webapp.app)
    r = c.get("/leaderboard")
    assert r.status_code == 200
    assert "Mag-7 Buy-the-Dip" in r.text and "Copy for ChatGPT" in r.text
    assert "Clone to AlpaTrade" in r.text and "Alpha vs SPY" in r.text
    assert 'href="/leaderboard"' in c.get("/").text
    sid = next(r["id"] for r in db.leaderboard() if r["slug"] == "mag7-btd-live")
    imp = c.get(f"/strategies/{sid}/alpatrade-import")
    assert imp.status_code == 200 and imp.json()["params"]["tp"] == 8.0
    assert "Do not place any live orders" in c.get(f"/skills/{sid}/prompt").text
    api = c.get("/api/strategies").json()["strategies"]
    assert any(s["id"] == sid and s["alpha_pct"] is not None for s in api)
    assert c.get(f"/skills/{sid}").status_code == 200
