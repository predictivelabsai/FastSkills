#!/usr/bin/env python3
"""Apply the skill-labeller taxonomy (prompts/skill-labeller.md) to the seed tree.

Writes a `sublabel:` line into each seed/*/*.md frontmatter. Assignment order:
explicit per-skill map -> per-category keyword rules -> per-category default.

    python scripts/label_skills.py            # label all
    python scripts/label_skills.py --check     # print assignments, write nothing
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

SEED = Path(__file__).resolve().parents[1] / "seed"

DEFAULT = {"finance": "Fund Management", "trading": "Portfolio Management",
           "legal": "Legal Research", "marketing": "Strategy"}

# Explicit per-skill assignments (keyed by file stem / slug).
OVERRIDE = {
    # Finance
    "family-office-profile": "Family Office", "service-coverage-matrix": "Family Office",
    "cross-sell-recommender": "Investor CRM", "proposal-generator": "Investor CRM",
    "outreach-pipeline-monitor": "Investor CRM",
    "multi-jurisdiction-tax-filing": "Tax & Compliance", "tax-law-assistant": "Tax & Compliance",
    "ma-buyer-sourcing": "M&A", "ma-seller-positioning": "M&A",
    "ipo-readiness": "IPO & ECM",
    "pe-deal-screening": "Private Equity", "sector-taxonomy": "Private Equity",
    "vc-round-modelling": "Venture Capital",
    "private-credit-underwriting": "Private Credit",
    # Trading
    "backtester": "Backtesting", "trading-api-backtest": "Backtesting",
    "index-options": "Options", "paper-trader": "Paper Trading",
    "portfolio-manager": "Portfolio Management", "alpatrade": "Portfolio Management",
    "reconciler": "Reconciliation", "reporter": "Reporting", "validator": "Validation",
    # Marketing
    "ab-testing": "Growth & CRO", "ad-creative": "Paid Ads", "ads": "Paid Ads",
    "ai-seo": "SEO", "analytics": "Analytics", "aso": "SEO", "attribution": "Analytics",
    "churn-prevention": "Growth & CRO", "co-marketing": "Strategy",
    "cold-email": "Sales & Outbound", "community-marketing": "Community & Influencer",
    "competitor-profiling": "Research", "competitors": "Research",
    "content-strategy": "Content", "copy-editing": "Content", "copywriting": "Content",
    "cro": "Growth & CRO", "customer-research": "Research",
    "directory-submissions": "SEO", "emails": "Email & SMS", "events": "Brand & PR",
    "free-tools": "Growth & CRO", "image": "Content",
    "influencer-marketing": "Community & Influencer", "launch": "Product Marketing",
    "lead-magnets": "Growth & CRO", "marketing-council": "Strategy",
    "marketing-ideas": "Strategy", "marketing-loops": "Growth & CRO",
    "marketing-plan": "Strategy", "marketing-psychology": "Strategy",
    "offers": "Pricing & Offers", "onboarding": "Growth & CRO", "paywalls": "Pricing & Offers",
    "popups": "Growth & CRO", "pricing": "Pricing & Offers",
    "product-marketing": "Product Marketing", "programmatic-seo": "SEO",
    "prospecting": "Sales & Outbound", "public-relations": "Brand & PR",
    "referrals": "Growth & CRO", "revops": "Sales & Outbound",
    "sales-enablement": "Sales & Outbound", "schema": "SEO", "seo-audit": "SEO",
    "signup": "Growth & CRO", "site-architecture": "SEO", "sms": "Email & SMS",
    "social": "Social", "video": "Content",
    # Legal
    "action-items-from-client-alert": "Document Review", "adversarial-qc": "Document Review",
    "ai-act-quick": "AI Governance", "bart-statutory-reference-checker": "Legal Research",
    "building-chronologies": "Litigation", "california-property-tax": "Tax",
    "case-file-analyzer": "Litigation", "classify-ccp": "Litigation",
    "collating-reviewer-feedback": "Document Review", "comms-improver": "Document Review",
    "contract-qa": "Contracts", "coquill": "Legal Research",
    "corporate-registry-investigation": "Corporate & Governance",
    "customs-trade-law": "Regulatory & Compliance", "dpa-art28": "Privacy & Data Protection",
    "dpa-checklist-review": "Privacy & Data Protection", "enhance-prompt": "Document Review",
    "foreign-law-research": "Legal Research", "legal-claim-economics": "Litigation",
    "legal-translation": "Legal Research", "license-comply": "IP & Licensing",
    "local-first-legal-workspace": "Legal Research",
    "lq-board-document-review": "Corporate & Governance",
    "lq-governance-playbook-benchmark": "Corporate & Governance",
    "msa-review-commercial-purchase": "Contracts", "msa-review-saas": "Contracts",
    "nda-review": "Contracts", "nis2-navigator": "Regulatory & Compliance",
    "nist-ai-rmf": "AI Governance", "office-word-diff": "Document Review",
    "privacy-notice-eu": "Privacy & Data Protection", "proposition-checking": "Document Review",
    "redfern-schedule": "Litigation", "redlines": "Contracts", "sgcite": "Legal Research",
    "statutory-analysis": "Legal Research", "superdoc-redlines": "Contracts",
    "text-provenance": "Document Review", "uk-citation-verification": "Legal Research",
    "uk-court-of-appeal-judicial-preference-check": "Litigation",
    "uk-disclosure-list-review": "Litigation", "uk-particulars-of-claim-review": "Litigation",
    "uk-witness-statement-review": "Litigation",
    "us-state-privacy-navigator": "Privacy & Data Protection",
    "vendor-privacy-policy-first-pass": "Privacy & Data Protection",
    "vibe-legal-batch-redliner": "Contracts", "skill-creator": "Document Review",
}

# Keyword fallback per category: first matching (sub_label, keywords) wins.
KEYWORDS = {
    "marketing": [
        ("SEO", ["seo", "schema", "sitemap", "serp", "directory", "aso"]),
        ("Paid Ads", ["ad", "ads", "ppc", "campaign"]),
        ("Email & SMS", ["email", "sms", "newsletter"]),
        ("Sales & Outbound", ["cold", "prospect", "outbound", "sales", "revops"]),
        ("Content", ["content", "copy", "video", "image", "blog"]),
        ("Social", ["social"]),
        ("Analytics", ["analytic", "attribution", "measure"]),
        ("Pricing & Offers", ["pricing", "offer", "paywall"]),
        ("Brand & PR", ["pr", "public relations", "event", "brand"]),
        ("Community & Influencer", ["community", "influencer", "referral"]),
        ("Product Marketing", ["launch", "product marketing", "positioning"]),
        ("Research", ["research", "competitor", "customer"]),
        ("Growth & CRO", ["cro", "conversion", "onboard", "retention", "growth", "popup", "signup"]),
    ],
    "legal": [
        ("Privacy & Data Protection", ["privacy", "gdpr", "dpa", "data protection"]),
        ("Contracts", ["contract", "nda", "msa", "redline", "agreement", "saas"]),
        ("AI Governance", ["ai act", "ai rmf", "ai governance"]),
        ("Litigation", ["litigation", "witness", "disclosure", "chronolog", "claim", "court", "pleading", "case"]),
        ("Corporate & Governance", ["board", "governance", "registry", "corporate"]),
        ("Regulatory & Compliance", ["regulat", "compliance", "customs", "trade", "nis2"]),
        ("IP & Licensing", ["licen", "intellectual", "copyright", "trademark"]),
        ("Tax", ["tax"]),
    ],
    "finance": [
        ("Family Office", ["family office", "family-office"]),
        ("Investor CRM", ["outreach", "cross-sell", "proposal", "pipeline", "crm"]),
        ("Private Equity", ["private equity", "pe ", "buyout", "sector"]),
        ("Venture Capital", ["venture", "cap table", "dilution", "round"]),
        ("Private Credit", ["credit", "lending", "loan", "underwrit"]),
        ("M&A", ["m&a", "buyer", "seller", "acquisition", "cim"]),
        ("IPO & ECM", ["ipo", "listing", "ecm", "public market"]),
        ("Tax & Compliance", ["tax", "fatca", "crs", "filing"]),
    ],
    "trading": [
        ("Backtesting", ["backtest"]),
        ("Paper Trading", ["paper"]),
        ("Options", ["option"]),
        ("Validation", ["validat"]),
        ("Reconciliation", ["reconcil"]),
        ("Reporting", ["report"]),
    ],
}

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _slug(stem):
    return re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")


def classify(category, stem, title, description):
    slug = _slug(stem)
    if slug in OVERRIDE:
        return OVERRIDE[slug]
    hay = f"{slug} {title} {description}".lower()
    for label, kws in KEYWORDS.get(category, []):
        if any(k in hay for k in kws):
            return label
    return DEFAULT.get(category, "")


def main(check=False):
    changed = 0
    for path in sorted(SEED.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = FRONT.match(text)
        if not m:
            continue
        block, body = m.group(1), m.group(2)
        meta = {}
        for line in block.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                meta[k.strip().lower()] = v.strip()
        category = path.parent.name  # finance / trading / legal / marketing
        sub = classify(category, path.stem, meta.get("title", ""), meta.get("description", ""))
        print(f"{category:9} {path.stem:42} -> {sub}")
        if check:
            continue
        # rewrite frontmatter with sublabel set (after the category line)
        lines, out, done = block.splitlines(), [], False
        for line in lines:
            if re.match(r"^sublabel:", line):
                out.append(f"sublabel: {sub}"); done = True
            else:
                out.append(line)
                if line.startswith("category:") and not done:
                    out.append(f"sublabel: {sub}"); done = True
        if not done:
            out.append(f"sublabel: {sub}")
        new = "---\n" + "\n".join(out) + "\n---\n\n" + body.lstrip("\n")
        if new != text:
            path.write_text(new, encoding="utf-8"); changed += 1
    print(f"\n{'would update' if check else 'updated'} {changed} file(s)")


if __name__ == "__main__":
    main(check="--check" in sys.argv)
