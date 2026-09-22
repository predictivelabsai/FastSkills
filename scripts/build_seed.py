#!/usr/bin/env python3
"""Generate the committed ``seed/`` tree from external + internal skill sources.

Run once (or whenever refreshing sources):

    python scripts/build_seed.py

External repos are shallow-cloned into a temp dir; internal repos are read from
sibling checkouts under ../.. . Each source SKILL.md is normalized into
``seed/<category>/<slug>.md`` with clean YAML frontmatter that seed.py consumes.
Authored Finance skills placed directly under seed/finance/ are left untouched.
"""
from __future__ import annotations
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT.parent.parent          # /home/julian/dev
SEED = ROOT / "seed"

# (git url, category, author, license, source_url)
EXTERNAL = [
    ("https://github.com/coreyhaines31/marketingskills.git", "Marketing", "Corey Haines",
     "MIT", "https://github.com/coreyhaines31/marketingskills"),
    ("https://github.com/LegalQuants/lq-skills.git", "Legal", "LegalQuants",
     "Apache-2.0", "https://github.com/LegalQuants/lq-skills"),
]

# Internal SKILL.md, relative to DEV. (path, category, author, license, source_url)
INTERNAL = [
    ("plai/alpatrade/agents/backtester/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/index_options/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/paper_trader/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/portfolio_manager/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/reconciler/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/reporter/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/agents/validator/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/engine/backtest/skills/trading-api-backtest/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("plai/alpatrade/hermes/skills/alpatrade/SKILL.md", "Trading", "Predictive Labs", "", ""),
    ("fastsme/FastPE/.claude/skills/sector-taxonomy/SKILL.md", "Finance", "Predictive Labs", "", ""),
]

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def parse_front(text):
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta, block, body = {}, m.group(1), m.group(2)
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        m2 = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", line)
        if m2:
            key, val = m2.group(1).lower(), m2.group(2).strip()
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                gathered, i = [], i + 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                    gathered.append(lines[i].strip()); i += 1
                meta[key] = " ".join(g for g in gathered if g)
                continue
            meta[key] = val.strip().strip('"').strip("'")
        i += 1
    return meta, body


def clean_desc(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) > 200:
        cut = text[:200]
        dot = cut.rfind(". ")
        text = (cut[:dot + 1] if dot > 80 else cut.rstrip() + "…")
    return text


ACRONYMS = {
    "ai": "AI", "seo": "SEO", "aso": "ASO", "cro": "CRO", "sms": "SMS", "pr": "PR",
    "nda": "NDA", "dpa": "DPA", "msa": "MSA", "saas": "SaaS", "ccp": "CCP", "us": "US",
    "uk": "UK", "eu": "EU", "nis2": "NIS2", "nist": "NIST", "rmf": "RMF", "qc": "QC",
    "ma": "M&A", "revops": "RevOps", "gtm": "GTM", "api": "API", "bart": "BART",
    "sgcite": "SGCite", "ccpa": "CCPA", "act": "Act",
}
SPECIAL = {"ab-testing": "A/B Testing", "ai-seo": "AI SEO", "ai-act-quick": "AI Act Quick"}


def titleize(slug):
    if slug in SPECIAL:
        return SPECIAL[slug]
    return " ".join(ACRONYMS.get(w, w.capitalize()) for w in re.split(r"[-_]+", slug) if w)


def write_skill(category, slug, meta, body, author, license_, source_url):
    desc = clean_desc(meta.get("description", ""))
    title = titleize(meta.get("name") or slug)
    out = SEED / category.lower() / f"{slug}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    front = (f"---\ntitle: {title}\ndescription: {desc}\ncategory: {category}\n"
             f"author: {author}\ntags: \nlicense: {license_}\nsource: {source_url}\n---\n\n")
    out.write_text(front + body.strip() + "\n", encoding="utf-8")
    return out


def find_skill_files(skills_dir):
    for p in sorted(skills_dir.iterdir()):
        if p.is_dir():
            for name in ("SKILL.md", "skill.md", "Skill.md"):
                f = p / name
                if f.is_file():
                    yield p.name, f
                    break


def main():
    count = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for url, category, author, lic, source in EXTERNAL:
            dest = tmp / re.sub(r"\W+", "_", url)
            print(f"cloning {url} …")
            subprocess.run(["git", "clone", "--depth", "1", url, str(dest)],
                           check=True, capture_output=True)
            skills_dir = dest / "skills"
            if not skills_dir.is_dir():
                print(f"  ! no skills/ in {url}"); continue
            for slug, f in find_skill_files(skills_dir):
                meta, body = parse_front(f.read_text(encoding="utf-8", errors="replace"))
                write_skill(category, slug, meta, body, author,
                            meta.get("license") or lic, source); count += 1
            print(f"  imported {category} skills")

    for rel, category, author, lic, source in INTERNAL:
        f = DEV / rel
        if not f.is_file():
            print(f"  ! missing internal {rel}"); continue
        slug = f.parent.name
        meta, body = parse_front(f.read_text(encoding="utf-8", errors="replace"))
        write_skill(category, slug, meta, body, author, lic, source); count += 1
    print(f"wrote {count} imported skills into {SEED}")


if __name__ == "__main__":
    main()
