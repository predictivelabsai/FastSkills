---
title: Reporter
description: Summarizes trading-run performance in three modes: recent-run summary, single-run deep dive, and top-strategy ranking
category: Trading
sublabel: Reporting
author: Predictive Labs
tags: 
license: 
source: 
---

# Reporter

Turns your backtest and paper-trading records into readable performance summaries, in three modes: an overview of recent runs, a deep dive on one run, and a ranking of top strategies.

*For research and education only. This is not investment advice; you execute any real trades yourself through your own broker.*

## When to use
- You want a quick overview of your recent runs and their key metrics.
- You want a full performance breakdown of one specific run.
- You want strategies ranked by average performance to compare approaches.

## What to provide
- Your run records or trade history (with run IDs, strategy names, dates, and per-trade rows).
- Which mode you want: overview, single-run detail, or top-strategy ranking.
- Any filters: run type (backtest vs paper), a run ID, a strategy prefix, or a row limit.

## How to work through it
1. Confirm the mode and any filters before compiling.
2. Overview mode: list recent runs with key metrics — total P&L, total and annualized return, Sharpe, and trade count.
3. Detail mode: for one run, add final capital, max drawdown, win rate, and winning/losing trade counts.
4. Top-strategy mode: group by strategy and rank by average annualized return, showing average Sharpe, return, win rate, drawdown, and P&L.
5. Compute all metrics only from the provided rows; note any run with missing data rather than filling gaps.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
