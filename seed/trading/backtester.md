---
title: Backtester
description: Runs parameterized backtests, sweeping tickers, intervals, and strategy parameters to find and rank the best configurations
category: Trading
sublabel: Backtesting
author: Predictive Labs
tags: 
license: 
source: 
---

# Backtester

Turns a strategy concept into a systematic historical backtest. It sweeps portfolios, intervals, and strategy parameters, then ranks the resulting configurations by performance.

*For research and education only. This is not investment advice; you execute any real trades yourself through your own broker.*

## When to use
- You want to test a rules-based strategy against historical price data.
- You want to sweep parameters (thresholds, hold periods, sizing) to compare configurations.
- You need reproducible, ranked results before considering paper or live trading.

## What to provide
- Strategy concept or explicit rules (entry, exit, take-profit, stop-loss).
- Universe or ticker list, and the date range plus data interval (e.g. daily, hourly).
- Initial capital, position sizing, and any risk limits.
- Which parameter values to vary, and which metric to optimize (e.g. Sharpe, total return, win rate).
- Historical price data, or a market-data source you will pull it from yourself.

## How to work through it
1. Restate the strategy as precise rules and confirm any assumptions before running.
2. Build the parameter grid from the values to vary (e.g. dip threshold, take-profit, hold days, stop-loss, position size).
3. For each combination, simulate entries and exits bar by bar over the date range, keeping signal timing separate from fill timing.
4. Record per-trade fills and per-configuration metrics: total return, annualized return, max drawdown, Sharpe, win rate, and trade count.
5. Rank configurations by the chosen objective and flag the best one, noting overfitting risk when many variants are tested.
6. Recommend out-of-sample or walk-forward checks before trusting a tuned configuration.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
