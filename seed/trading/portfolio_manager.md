---
title: Portfolio Manager
description: Coordinates the full research loop across backtesting, validation, paper trading, and reporting into one consolidated view
category: Trading
sublabel: Portfolio Management
author: Predictive Labs
tags: 
license: 
source: 
---

# Portfolio Manager

Coordinates the end-to-end research loop: backtest a strategy, validate the results, forward-test the best parameters as paper trades, then consolidate everything into a single report.

*For research and education only. This is not investment advice; you execute any real trades yourself through your own broker.*

## When to use
- You want to run a full strategy study from idea to consolidated results in one pass.
- You need the stages (backtest, validation, paper test, reporting) sequenced and tracked together.
- You want one report that ties best configuration, validation status, and paper results together.

## What to provide
- Strategy concept or rules, and the universe or ticker list.
- Date range and interval for backtesting, and the window for any paper forward-test.
- Initial capital, position sizing, and risk limits.
- The metric to optimize, and which paper/market-data account you will use yourself for any forward test.

## How to work through it
1. Confirm scope: strategy, universe, date range, capital, risk limits, and objective.
2. Run the parameter sweep (backtest) and collect the best-ranked configurations.
3. Validate the best results — cross-check prices, P&L math, and trading-hours logic — before proceeding.
4. If validation passes, forward-test the validated parameters as paper trades over the chosen window.
5. Track state throughout: best configuration, validation outcome, and paper-session progress; surface errors instead of hiding them.
6. Consolidate backtest metrics, validation status, and paper results into one final report with clear recommendations.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
