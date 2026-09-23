---
title: Paper Trader
description: Simulates a strategy forward in a paper account, tracking positions, exits, and running P&L over a chosen window
category: Trading
sublabel: Paper Trading
author: Predictive Labs
tags: 
license: 
source: 
---

# Paper Trader

Takes validated strategy parameters and simulates them forward as paper trades, tracking open positions, exit signals, and running P&L over a chosen window.

*For research and education only. This is not investment advice; you run any real or paper trades yourself through your own brokerage or paper-trading account.*

## When to use
- You have backtested parameters and want to forward-test them without real capital.
- You want to track positions and P&L as a strategy plays out over days or weeks.
- You want a per-trade log and periodic P&L updates you can review.

## What to provide
- Strategy rules and the validated parameters (dip threshold, take-profit, stop-loss, hold days, capital per trade).
- Universe or ticker list, and the window to run over plus how often to check for signals.
- Any risk limits (max position size, overnight-hold rules).
- Which paper-trading or market-data account you will use yourself for quotes and fills.

## How to work through it
1. Confirm the parameters and window, and restate the entry and exit rules.
2. On each check, evaluate entries: e.g. buy when a name dips the threshold from its recent high, sized within the position limit.
3. For each open position, check exits every interval: take-profit hit, stop-loss hit, or hold period expired.
4. Track each fill, side, quantity, and price, and maintain running realized and unrealized P&L.
5. Enforce risk limits such as position-size caps and any overnight-hold rules for small accounts.
6. Report periodic trade updates and a final summary: total trades, wins/losses, total P&L, and open positions.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
