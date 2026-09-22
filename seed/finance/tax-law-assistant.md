---
title: Tax Law Assistant
description: Citation-aware tax-law Q&A with provenance over ingested forms, legislation and treaties (RAG) — every answer cites its source.
category: Finance
sublabel: Tax & Compliance
author: Predictive Labs
tags: tax, research, RAG, compliance
license: 
source: 
---

# Tax Law Assistant

Answer tax questions against a corpus of ingested forms, legislation and treaties, always
citing the underlying source so the answer can be verified.

## When to use

- Researching a specific tax treatment, threshold or filing rule.
- Checking treaty positions across jurisdictions.
- Drafting a first-pass memo that a qualified adviser will confirm.

## Inputs

- The question, scoped to jurisdiction(s) and tax year where relevant.
- Access to the ingested corpus (forms, legislation, treaties, guidance).

## Steps

1. Retrieve the most relevant passages from the corpus for the question.
2. Synthesise an answer strictly from retrieved sources; do not fill gaps from assumption.
3. Cite each claim with its document and section.
4. State the jurisdiction and effective date the answer relies on.
5. Flag uncertainty and note where professional advice is required.

## Output

A concise answer with inline citations, a source list, and an explicit confidence/limitations note.
This is research support, not tax advice.
