#!/usr/bin/env python3
"""Refresh the leaderboard snapshot for seeded strategies from AlpaTrade live data.

Reads (SELECT only, read-only transaction) the live run row in the AlpaTrade DB
(``alpatrade.runs``, ``mode='live'``, matched by ``strategy_slug``) and takes the
latest *completed-session* daily snapshot in ``results.daily`` — the same numbers
the AlpaTrade dashboard and daily LIVE email use. Trading days are counted with
AlpaTrade's own ``engine.reporting.annualize.trading_days_between`` (NYSE calendar,
start day inclusive), so the leaderboard's annualised return matches AlpaTrade's.

Writes ``seed/strategy_stats.json`` (commit + push → deploy re-seeds it on boot).
``--write-db`` also upserts it into the FastSkills DB configured in this repo's env.

    python scripts/refresh_strategy_stats.py --alpatrade-dir ~/dev/plai/alpatrade

The AlpaTrade DSN comes from $ALPATRADE_DATABASE_URL, else DATABASE_URL in
<alpatrade-dir>/.env. It is never printed. Nothing in AlpaTrade is modified.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "seed" / "strategy_stats.json"

# FastSkills seed slug -> AlpaTrade live runner strategy_slug
STRATEGIES = {"mag7-btd-live": "buy_the_dip_mag7_minhold_live"}


def _dotenv_value(path: Path, key: str) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:]
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _alpatrade_calendar(at: Path):
    """AlpaTrade's own NYSE trading-day counter. If the local checkout predates
    engine/reporting/annualize.py (e.g. a live-runner machine that isn't pulled
    mid-session), load that one file from the fetched origin/main instead of
    touching the checkout."""
    sys.path.insert(0, str(at))
    try:
        from engine.reporting.annualize import trading_days_between
        return trading_days_between
    except ImportError:
        import subprocess, types
        src = subprocess.run(["git", "-C", str(at), "show", "origin/main:engine/reporting/annualize.py"],
                             capture_output=True, text=True, check=True).stdout
        mod = types.ModuleType("alpatrade_annualize")
        exec(compile(src, "alpatrade:engine/reporting/annualize.py", "exec"), mod.__dict__)
        return mod.trading_days_between


def snapshot(cur, at_slug: str, trading_days_between) -> dict:
    cur.execute("SELECT run_id, config, results FROM alpatrade.runs WHERE mode='live' "
                "AND strategy_slug=%s ORDER BY started_at DESC LIMIT 1", (at_slug,))
    r = cur.fetchone()
    if not r:
        raise SystemExit(f"no live run for {at_slug}")
    run_id, cfg, res = r
    cfg, res = cfg or {}, res or {}
    daily = res.get("daily") or {}
    if not daily:
        raise SystemExit(f"no daily snapshots yet for {at_slug}")
    as_of = max(daily)
    snap = daily[as_of]
    start = date.fromisoformat(str(cfg["started"])[:10])
    start_eq, start_spy = float(cfg["start_equity"]), float(cfg["start_spy"])
    equity, spy = float(snap["equity"]), float(snap["spy"])
    return {
        "live_start": start.isoformat(),
        "start_equity": start_eq,
        "benchmark": "SPY",
        "start_benchmark": start_spy,
        "as_of": as_of,
        "equity": equity,
        "benchmark_value": spy,
        "return_pct": round((equity / start_eq - 1) * 100, 3),
        "benchmark_return_pct": round((spy / start_spy - 1) * 100, 3),
        "trading_days": trading_days_between(start, date.fromisoformat(as_of)),
        "source": (f"AlpaTrade live run (Alpaca live account), daily snapshot at the "
                   f"{as_of} session close; account return vs SPY since {start.isoformat()}"),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--alpatrade-dir", default=os.getenv("ALPATRADE_DIR",
                                                         str(Path.home() / "dev/plai/alpatrade")))
    ap.add_argument("--write-db", action="store_true", help="also upsert into the FastSkills DB")
    ap.add_argument("--dry-run", action="store_true", help="print, don't write the JSON")
    a = ap.parse_args()
    at = Path(a.alpatrade_dir).expanduser()
    trading_days_between = _alpatrade_calendar(at)

    dsn = os.getenv("ALPATRADE_DATABASE_URL") or _dotenv_value(at / ".env", "DATABASE_URL")
    if not dsn:
        raise SystemExit("set ALPATRADE_DATABASE_URL or DATABASE_URL in <alpatrade-dir>/.env")
    if dsn.startswith("postgres://"):
        dsn = "postgresql://" + dsn[len("postgres://"):]
    import psycopg
    out = {}
    with psycopg.connect(dsn, connect_timeout=15) as conn:
        conn.read_only = True
        with conn.cursor() as cur:
            for slug, at_slug in STRATEGIES.items():
                out[slug] = snapshot(cur, at_slug, trading_days_between)
    doc = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
           "generated_by": "scripts/refresh_strategy_stats.py", "strategies": out}
    print(json.dumps(doc, indent=2))
    if a.dry_run:
        return
    STATS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {STATS.relative_to(ROOT)}")
    if a.write_db:
        sys.path.insert(0, str(ROOT))
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
        from fastskills import seed
        seed.run()
        print(f"upserted {seed.seed_strategy_stats()} snapshot(s) into the FastSkills DB")


if __name__ == "__main__":
    main()
