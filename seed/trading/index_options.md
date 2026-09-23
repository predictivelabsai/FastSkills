---
title: Index Options
description: Structures and evaluates index-option trades with expiry-aware, defined-risk controls before you place them yourself
category: Trading
sublabel: Options
author: Predictive Labs
tags: 
license: 
source: 
---

# Index Options

Helps design and evaluate index-option trades on cash-settled indices (e.g. SPX, VIX, XSP), with expiry-aware risk controls and a preference for defined-risk structures.

*For research and education only. This is not investment advice; you place and manage any real trades yourself through your own broker.*

## When to use
- You want to translate a directional or volatility thesis into an index-option structure.
- You need expiry-aware risk framing (0DTE, weeklies, settlement style) before committing capital.
- You want maximum loss laid out clearly for a single leg or a multi-leg spread.

## What to provide
- The index, your directional or volatility thesis, and the expiry horizon.
- Your maximum acceptable loss and preferred risk profile.
- Which brokerage or paper-trading account you will use to place the trade yourself.

## How to work through it
1. Confirm the index, thesis, max loss, and expiry horizon before proposing anything.
2. Explain settlement mechanics: cash-settled, European-style exercise, and AM- vs PM-settled expiries, and highlight expiry cutoffs.
3. Prefer defined-risk structures. For any multi-leg idea, present the complete proposed structure and its maximum loss before discussing sizing.
4. Default to whole contracts, quantity one, unless you specify otherwise.
5. Treat 0DTE and naked short options as high risk; prefer smaller-notional indices and defined-risk spreads for short-premium ideas.
6. Summarize each proposed contract, side, quantity, and price type so you can enter it yourself.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
