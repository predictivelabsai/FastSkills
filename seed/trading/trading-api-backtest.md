---
title: Trading API Backtest
description: Runs a reproducible historical backtest from a start date, end date, and strategy concept, with documented assumptions and downloadable artifacts
category: Trading
sublabel: Backtesting
author: Predictive Labs
tags: 
license: 
source: 
---

# Trading API Backtest

Runs one specific, reproducible historical backtest from a date range and a strategy concept, making every assumption visible and producing auditable artifacts.

*For research and education only. This is a hypothetical historical simulation, not investment advice; backtested results do not guarantee future performance, and you execute any real trades yourself through your own broker.*

## When to use
- You want a single, well-documented historical backtest rather than a broad parameter sweep.
- You need reproducible artifacts (config, per-trade rows, equity curve, metrics) you can re-run.
- You want assumptions (fills, fees, slippage, calendar) stated explicitly before results.

## What to provide
- Start date, end date, and the strategy concept or explicit rules.
- Asset class, symbols or universe, and the timeframe (e.g. daily, hourly).
- Initial cash, position sizing, and a benchmark to compare against.
- Historical price data, or a market-data source you will pull it from yourself.

## How to work through it
1. Gather the required inputs, then infer and confirm the rest: sizing, execution assumptions, and benchmark.
2. Translate the idea into precise rules — data field, trigger, bounds, indicator variants and parameters, warmup, sizing, order type, and fill model — and confirm before running.
3. Resolve run considerations: fill timing, dividends and splits, fees, slippage, market hours, calendar handling, and look-ahead/survivorship/overfitting risks.
4. Keep signal timing separate from fill timing (e.g. signal on a bar's close, fill on the next open) and document the chosen fill model.
5. Simulate over the range, then record per-trade fills, an equity curve, and a benchmark equity curve.
6. Compute metrics: total and annualized return, max drawdown, Sharpe, win rate, profit factor, and fees paid; note if no trades occurred and why.
7. Save reproducible artifacts (assumptions notes, strategy spec, config, per-trade rows, equity, metrics) so the run can be repeated.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
