---
title: Trading Workbench
description: End-to-end trading research: backtest a strategy, save the best candidates, inspect prior runs, and forward-test them as paper trades
category: Trading
sublabel: Portfolio Management
author: Predictive Labs
tags: 
license: 
source: 
---

# Trading Workbench

A single entry point for strategy research: backtest an idea, save the best-performing candidates, inspect past runs, and forward-test a chosen candidate as paper trades.

*For research and education only. This is not investment advice; you execute any real trades yourself through your own broker.*

## When to use
- You want to backtest and optimize a strategy, then keep the strongest configurations.
- You want to revisit a saved candidate or an earlier run and review its metrics.
- You want to forward-test a saved candidate as paper trades before considering live use.

## What to provide
- Strategy concept or rules, and the universe or ticker list.
- Lookback or date range and interval, and the metric to optimize (e.g. Sharpe).
- For a paper forward-test, the duration and which paper/market-data account you will use yourself.

## How to work through it
1. Confirm the strategy, symbols, lookback, and objective before running anything.
2. Backtest across the parameter space and rank the results by the chosen objective.
3. Save the best configurations as named candidates, each with its metrics and settings recorded.
4. On request, list saved candidates and inspect a prior run, summarizing its key metrics.
5. To forward-test, take a chosen candidate and simulate it as paper trades over the requested duration, tracking positions and P&L.
6. Never place live orders on the user's behalf; the user runs any real trades themselves through their own broker.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
