---
title: Validator
description: Independently cross-checks recorded trades against market data for price, P&L, and trading-hours accuracy, iterating up to ten times
category: Trading
sublabel: Validation
author: Predictive Labs
tags: 
license: 
source: 
---

# Validator

Independently verifies backtest or paper-trading results against real market data, checking price accuracy, P&L math, and trading-hours compliance, and attempting self-correction before flagging what it cannot resolve.

*For research and education only. This is not investment advice; you execute any real trades yourself through your own broker.*

## When to use
- You want an independent sanity check on trades before trusting a result.
- You suspect mispriced fills, P&L math errors, or trades outside valid trading hours.
- You want anomalies auto-corrected where possible, with the rest escalated clearly.

## What to provide
- The trade records to check (entry/exit prices, quantities, timestamps, P&L, fees).
- A market-data source you will supply for the same symbols and timestamps.
- A price tolerance (e.g. 1%) and the market's regular and extended trading hours and calendar.

## How to work through it
1. Price tolerance: compare each recorded price to the actual bar at that timestamp; flag when the deviation exceeds tolerance.
2. P&L math: verify P&L equals (exit − entry) x quantity − fees, and that the percentage matches.
3. Trading hours: confirm entries and exits fall within valid hours; flag weekend and market-holiday trades.
4. Exit logic: confirm take-profit and stop-loss exits are consistent with the recorded prices, and that both cannot be hit on one trade.
5. Self-correction loop: when anomalies appear, attempt fixes (price rounding within tolerance, fee recalculation, P&L recomputation, or flagging stale data) and re-check, up to ten iterations.
6. Report status as passed, corrected, or failed, listing anomalies, corrections made, and suggested manual interventions for anything unresolved.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
