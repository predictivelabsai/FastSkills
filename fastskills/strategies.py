"""Strategy helpers: performance metrics, the machine-readable parameters block,
and the hand-off prompts (ChatGPT / Claude / AlpaTrade).

A *strategy* is a skill with ``kind='strategy'``. Its live track record lives in
``strategy_stats`` (one row per strategy skill), stored as a dated snapshot:
start date/equity/benchmark plus the as-of equity/benchmark and the number of
trading days. Annualised return follows AlpaTrade's convention
(``engine/reporting/annualize.py``): simple = return × 252 / trading days, with
the compounded figure shown only as an indicative tooltip because gains are not
reinvested immediately. Alpha = strategy return − SPY return over the same period.
"""
from __future__ import annotations
import json
import re
from datetime import date, datetime, timezone

TRADING_DAYS_PER_YEAR = 252
ALPATRADE_URL = "https://alpatrade.chat/"

_FENCE = re.compile(r"^```[^\n]*\n(.*?)^```", re.DOTALL | re.MULTILINE)


def _num(v):
    try:
        return None if v is None or v == "" else float(v)
    except (TypeError, ValueError):
        return None


def _date(v):
    if not v:
        return None
    try:
        return date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def annualise(return_pct, trading_days):
    """{'simple_pct','compound_pct'} — None when there is not enough data."""
    r, d = _num(return_pct), int(trading_days or 0)
    if r is None or d < 1:
        return {"simple_pct": None, "compound_pct": None}
    simple = r / 100.0 * TRADING_DAYS_PER_YEAR / d * 100
    try:
        compound = ((1 + r / 100.0) ** (TRADING_DAYS_PER_YEAR / d) - 1) * 100 if r > -100 else -100.0
    except OverflowError:
        compound = None
    return {"simple_pct": simple, "compound_pct": compound}


def metrics(stats, today=None):
    """Display metrics for one strategy from its stats row (or None)."""
    stats = stats or {}
    today = today or datetime.now(timezone.utc).date()
    start = _date(stats.get("live_start"))
    ret, bench = _num(stats.get("return_pct")), _num(stats.get("benchmark_return_pct"))
    days = int(stats.get("trading_days") or 0)
    ann = annualise(ret, days)
    return {
        "has_data": ret is not None and days > 0,
        "live_start": start.isoformat() if start else None,
        "days_running": (today - start).days if start else None,
        "trading_days": days or None,
        "as_of": stats.get("as_of"),
        "return_pct": ret,
        "benchmark": stats.get("benchmark") or "SPY",
        "benchmark_return_pct": bench,
        "alpha_pct": (ret - bench) if ret is not None and bench is not None else None,
        "annualised_pct": ann["simple_pct"],
        "annualised_compound_pct": ann["compound_pct"],
        "source": stats.get("source") or "",
    }


def pct(v, digits=2):
    return "—" if v is None else f"{v:+.{digits}f}%"


def fmt_day(v):
    d = _date(v)
    return d.strftime("%-d %b %Y") if d else "—"


def annualised_tooltip(m):
    if m.get("annualised_pct") is None:
        return "No live track record yet"
    return (f"Simple: return × 252 / trading days = {pct(m['return_pct'])} × 252 / "
            f"{m['trading_days']} = {pct(m['annualised_pct'])}; compounded (1+r)^(252/d)−1 = "
            f"{pct(m['annualised_compound_pct'])} (indicative only: gains aren't reinvested "
            f"immediately). As of {fmt_day(m['as_of'])}.")


def alpha_tooltip(m):
    if m.get("alpha_pct") is None:
        return "No live track record yet"
    return (f"Strategy {pct(m['return_pct'])} vs {m['benchmark']} {pct(m['benchmark_return_pct'])} "
            f"from {fmt_day(m['live_start'])} to {fmt_day(m['as_of'])} "
            f"({m['trading_days']} trading days).")


# ── parameters block ─────────────────────────────────────────────────────────
def extract_params(markdown):
    """The first fenced JSON block holding ``params`` (the machine-readable block).
    The editor drops the ``json`` info string on save, so any fence is accepted."""
    for m in _FENCE.finditer(markdown or ""):
        try:
            data = json.loads(m.group(1))
        except (ValueError, TypeError):
            continue
        if isinstance(data, dict) and isinstance(data.get("params"), dict):
            return data
    return None


def alpatrade_import(item):
    """Import payload shaped like an AlpaTrade ``strategy_configs`` row."""
    block = extract_params(item.get("markdown")) or {}
    return {
        "schema": block.get("schema", "alpatrade.strategy_config/v1"),
        "name": block.get("name") or item.get("slug"),
        "display_name": block.get("display_name") or item.get("title"),
        "description": item.get("description") or "",
        "params": block.get("params") or {},
        "execution": block.get("execution") or {},
        "source": {"app": "FastSkills", "skill_id": item.get("id"), "title": item.get("title"),
                   "author": item.get("owner_name") or item.get("author_label") or "",
                   "config_version": block.get("config_version")},
    }


# ── hand-off prompts ─────────────────────────────────────────────────────────
def assistant_prompt(item):
    return ("Please use the following trading-strategy skill. Read the rules and the "
            "machine-readable Parameters block, then help me with whatever I ask about it "
            "(explanation, backtest, code, risk review). Do not place any live orders.\n\n"
            f"# {item['title']}\n\n{item.get('markdown') or ''}\n\n"
            "— (strategy shared from FastSkills · fastskills.org/leaderboard)")


def alpatrade_prompt(item):
    payload = alpatrade_import(item)
    p = payload["params"]
    lines = [f"Clone this strategy from FastSkills into AlpaTrade: \"{payload['display_name']}\""
             + (f" by {payload['source']['author']}" if payload["source"]["author"] else "") + "."]
    if p:
        lines.append(
            "Start by backtesting it (paper only, no live orders) on "
            f"{', '.join(p.get('symbols') or [])} over the last 6 months against SPY: buy when "
            f"the price is {p.get('dip')}% or more below the {('20-day high' if p.get('ref') == 'high20' else 'previous close')}, "
            f"take profit {p.get('tp')}%, stop loss {p.get('sl')}%, hold {p.get('min_hold')}–{p.get('max_hold')} days, "
            f"position size {p.get('pos_frac')} of equity, cash only.")
    lines.append("Full strategy config (AlpaTrade strategy_configs shape):")
    lines.append("```json\n" + json.dumps({k: payload[k] for k in ("name", "display_name", "params", "execution")},
                                          indent=2) + "\n```")
    return "\n\n".join(lines)
