---
title: Reconciler
description: Compares your recorded positions, trades, and P&L against your account's actual holdings to surface discrepancies
category: Trading
sublabel: Reconciliation
author: Predictive Labs
tags: 
license: 
source: 
---

# Reconciler

Compares the positions, trades, and P&L you recorded against what your brokerage or paper account actually reports for a time window, and surfaces any discrepancies.

*For research and education only. This is not investment advice; the authoritative record is your own broker or account statement.*

## When to use
- You want to confirm your tracked positions match your account's actual holdings.
- You suspect a missing, extra, or mismatched trade over a recent window.
- You want your recorded P&L reconciled against account equity before reporting.

## What to provide
- The time window to reconcile.
- Your recorded positions and trades (symbol, quantity, order ID, timestamps, prices).
- Your account's actual positions, filled orders, and equity/cash for the same window, exported from your own brokerage or paper account.

## How to work through it
1. Confirm the window and gather both sides: your records and your account export.
2. Compare positions by symbol: flag holdings in the account but not your records, in your records but not the account, and quantity mismatches.
3. Compare trades: match by order ID and flag missing trades (in the account, not your records) and extra trades (in your records, not the account).
4. Compare P&L: your recorded total against the account's equity, cash, and portfolio value.
5. Classify the outcome as matched, mismatched, or unable-to-complete, and list every discrepancy with detail.
6. Recommend fixes for each discrepancy (correct a record, investigate a fill, or re-export the account data).

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading (e.g. trades, per-parameter results, P&L, metrics).
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows/trades), and generate them when asked.
- Never invent figures or fills. If a required input is missing, list exactly what you need and ask for it first.
