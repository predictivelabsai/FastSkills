---
title: Cross-Sell Recommender
description: Generate explainable service-gap and cross-sell recommendations for a family-office relationship, with every recommendation traceable to a rule.
category: Finance
sublabel: Investor CRM
author: Predictive Labs
tags: cross-sell, family office, recommendations, revenue
license: 
source: 
---

# Cross-Sell Recommender

Surface the next-best services to offer a family-office relationship, combining a
deterministic rule layer with an AI re-ranking pass — so every recommendation is
explainable and auditable.

## When to use

- Reviewing a relationship for white space and revenue opportunities.
- Preparing an account plan or QBR.
- Feeding a proposal drafting step ([[proposal-generator]]).

## Inputs

- A current [[family-office-profile]] (structure, asset mix, jurisdictions, pain points).
- The catalogue of services you can offer and their eligibility criteria.
- Existing services already in place for the relationship.

## Steps

1. Run the rule set against the profile to find eligible-but-unused services; each hit
   carries a `rule_id` and the profile facts that triggered it.
2. Score candidates by fit, urgency and estimated value.
3. Re-rank with an AI pass that weighs qualitative context (stated mandates, timing).
4. Attach a plain-language rationale to each recommendation citing the triggering facts.
5. Drop any recommendation that cannot be traced back to a rule or profile fact.

## Output

A ranked list of recommendations, each with: service, rationale, `rule_id`/source,
estimated value and suggested next action.
