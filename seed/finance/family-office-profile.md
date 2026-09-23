---
title: Family Office Profile
description: Build and maintain a structured single-family-office relationship profile — principals, advisers, jurisdictions, asset mix and pain points.
category: Finance
sublabel: Family Office
author: Predictive Labs
tags: family office, wealth, crm, onboarding
license: 
source: 
---

# Family Office Profile

Build and retrieve a structured relationship profile for a single-family office (SFO), so outreach and service recommendations are grounded in an accurate picture of the relationship.

## When to use

- Onboarding a new family-office relationship into the book.
- Preparing for a meeting and needing a one-page brief.
- Before running cross-sell or coverage analysis, which depend on an up-to-date profile.

## Inputs

- Family / entity name and the operating structure (SFO, MFO, holdco, trust).
- Principals and their roles; key advisers (tax, legal, investment).
- Jurisdictions of residence, domicile and material assets.
- Approximate asset mix (public markets, private equity, real estate, operating businesses, cash).
- Known pain points, mandates and constraints.

## Steps

1. Capture the entity and its legal/operating structure.
2. Record each principal and adviser with role and contact ownership.
3. Map jurisdictions and flag any that trigger reporting obligations (FATCA/CRS, W-8).
4. Summarise the asset mix as rough percentages and note concentration risks.
5. Log stated pain points and mandates verbatim, with the source and date.
6. Produce a one-page brief: who they are, what they hold, what they need next.

## Output

A normalized profile record plus a shareable one-page brief that downstream skills
([[cross-sell-recommender]], [[service-coverage-matrix]]) can consume.


## Presenting results
- Present every result as one or more clear Markdown **tables** — one per section, each with a short heading.
- Keep prose minimal; put the substance in the tables.
- Offer the user a downloadable **PDF** (formatted) and **CSV** (the underlying rows), and generate them when asked.
- Never invent figures. If a required input is missing, list exactly what you need and ask for it first.
