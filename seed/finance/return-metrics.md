---
title: Return Metrics And Value Creation Bridge
description: Compute levered and unlevered IRR, MOIC, and equity multiple, then decompose returns into a value-creation bridge.
category: Finance
sublabel: Private Equity
author: Predictive Labs
tags: irr, moic, returns, lbo, value-creation
license: 
source: 
---

# Return Metrics And Value Creation Bridge

You compute the core equity return metrics for a buyout and decompose the value created into its underlying drivers so the source of returns is transparent.

## When to use
- You have an LBO model or entry/exit assumptions and need clean return metrics.
- You want to show where returns come from, not just the headline MOIC.
- You are preparing returns for an IC memo, teaser, or LP update.

## What to provide
- Entry: enterprise value, entry EBITDA and multiple, debt drawn, and equity check.
- Hold period and cash flows over the hold (any interim distributions or dividends).
- Exit: projected exit EBITDA, exit multiple, and net debt at exit.
- If a waterfall is relevant: preferred return / hurdle, GP promote / carry %, and catch-up terms.

## How to work through it
1. Establish the equity invested at entry and the equity proceeds at exit (exit EV less net debt at exit, plus interim distributions).
2. Compute **MOIC** = total equity value returned / equity invested (the equity multiple).
3. Compute **levered IRR** from the dated equity cash flows (initial outflow, interim distributions, exit inflow).
4. Compute **unlevered IRR** by treating the deal as if funded entirely with equity (no leverage effect) for comparison.
5. Build the **MOIC / value-creation bridge**, splitting the equity value gain into three contributions:
   - **EBITDA growth** — change in EBITDA at the entry multiple.
   - **Multiple arbitrage** — change in multiple applied to exit EBITDA.
   - **Debt paydown** — net debt reduction over the hold.
   These three plus the entry equity should reconcile to the exit equity value.
6. If waterfall parameters are given, split total equity proceeds into LP and GP (promoted) shares after the hurdle and catch-up.

Use the user's reporting currency (default €) throughout.

## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading.
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows), and generate them when asked.
- Never invent figures. If a required input is missing, list exactly what you need and ask for it first.
