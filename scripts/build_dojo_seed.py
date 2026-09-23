#!/usr/bin/env python3
"""Import the MIT-licensed skill packs listed on skillsdojo.com into seed/.

Each pack is a public GitHub repo of standalone SKILL.md files. We republish
only MIT-licensed packs, crediting the original creator (author), recording the
source repo and license. Slugs are source-scoped to avoid collisions with each
other and with the existing catalog. Unlicensed packs are intentionally skipped.

    python scripts/build_dojo_seed.py
"""
from __future__ import annotations
import re, shutil, subprocess, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "seed"

# repo, creator (credit), category, sublabel, slug-prefix
PACKS = [
    ("kepano/obsidian-skills",              "kepano (Steph Ango)", "Productivity", "Obsidian",          "obsidian"),
    ("emilkowalski/skills",                 "Emil Kowalski",        "Design",       "Design Engineering","emil"),
    ("AgriciDaniel/claude-seo",             "AgriciDaniel",         "Marketing",    "SEO",               "cseo"),
    ("ericosiu/ai-marketing-skills",        "Eric Siu",             "Marketing",    "Strategy",          "ericosiu"),
    ("AgriciDaniel/claude-blog",            "AgriciDaniel",         "Marketing",    "Content",           "cblog"),
    ("onvoyage-ai/gtm-engineer-skills",     "onvoyage-ai",          "Marketing",    "GTM",               "gtm"),
    ("OpenClaudia/openclaudia-skills",      "OpenClaudia",          "Marketing",    "SEO",               "oclaudia"),
    ("Affitor/affiliate-skills",            "Affitor",              "Marketing",    "Affiliate",         "affitor"),
    ("blacktwist/social-media-skills",      "blacktwist",           "Marketing",    "Social",            "social"),
    ("TheMattBerman/google-ads-copilot",    "Matt Berman",          "Marketing",    "Paid Ads",          "gads"),
    ("garrettjsmith/localseoskills",        "garrettjsmith",        "Marketing",    "Local SEO",         "lseo"),
    ("superamped/ai-marketing-skills",      "superamped",           "Marketing",    "Strategy",          "samp"),
    # UI skills directory (ui-skills.com); per-skill sub-labels applied via a
    # dedicated import — this entry documents the source/credit for reproducibility.
    ("ibelick/ui-skills",                   "Julien Thibeaut (ibelick)", "UI",       "Frontend",          "uiskills"),
]

FRONT = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def parse_front(text):
    m = FRONT.match(text)
    if not m:
        return {}, text
    meta, lines, i = {}, m.group(1).splitlines(), 0
    while i < len(lines):
        mm = re.match(r"^([A-Za-z][\w-]*):\s*(.*)$", lines[i])
        if mm:
            k, v = mm.group(1).lower(), mm.group(2).strip()
            if v in (">", "|", ">-", "|-", ">+", "|+"):
                g, i = [], i + 1
                while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                    g.append(lines[i].strip()); i += 1
                meta[k] = " ".join(x for x in g if x); continue
            meta[k] = v.strip().strip('"').strip("'")
        i += 1
    return meta, m.group(2)


def clean_desc(t):
    t = re.sub(r"\s+", " ", t or "").strip()
    if len(t) > 200:
        cut = t[:200]; dot = cut.rfind(". ")
        t = cut[:dot + 1] if dot > 80 else cut.rstrip() + "…"
    return t


ACRO = {"seo": "SEO", "ai": "AI", "ab": "A/B", "gtm": "GTM", "aeo": "AEO", "geo": "GEO",
        "cli": "CLI", "sms": "SMS", "faq": "FAQ", "cro": "CRO", "ppc": "PPC", "ugc": "UGC",
        "roi": "ROI", "b2b": "B2B", "api": "API", "json": "JSON", "css": "CSS"}


def titleize(stem):
    return " ".join(ACRO.get(w, w.capitalize()) for w in re.split(r"[-_]+", stem) if w)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "skill"


def find_skill_dirs(repo_dir):
    """Yield (skill_dir_name, SKILL.md path) for both root-level and skills/ layouts."""
    seen = set()
    for base in (repo_dir, repo_dir / "skills"):
        if not base.is_dir():
            continue
        for d in sorted(base.iterdir()):
            if d.is_dir() and d.name not in seen:
                for name in ("SKILL.md", "skill.md", "Skill.md"):
                    f = d / name
                    if f.is_file():
                        seen.add(d.name); yield d.name, f; break


def main():
    total = 0
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for repo, creator, category, sublabel, prefix in PACKS:
            dest = tmp / prefix
            print(f"cloning {repo} …")
            r = subprocess.run(["git", "clone", "--depth", "1", f"https://github.com/{repo}.git", str(dest)],
                               capture_output=True, text=True)
            if r.returncode != 0:
                print(f"  ! clone failed: {r.stderr.strip()[:100]}"); continue
            n = 0
            for dirname, f in find_skill_dirs(dest):
                meta, body = parse_front(f.read_text(encoding="utf-8", errors="replace"))
                title = titleize(meta.get("name") or dirname)
                desc = clean_desc(meta.get("description", "")) or f"{title} — a skill by {creator}."
                slug = slugify(f"{prefix}-{dirname}")
                out = SEED / category.lower().replace(" ", "-") / f"{slug}.md"
                out.parent.mkdir(parents=True, exist_ok=True)
                front = (f"---\ntitle: {title}\ndescription: {desc}\ncategory: {category}\n"
                         f"sublabel: {sublabel}\nauthor: {creator}\ntags: \nlicense: MIT\n"
                         f"source: https://github.com/{repo}\n---\n\n")
                out.write_text(front + body.strip() + "\n", encoding="utf-8")
                n += 1
            print(f"  imported {n} skills -> {category}/{sublabel}")
            total += n
    print(f"\nTotal imported: {total} skills from {len(PACKS)} MIT packs")


if __name__ == "__main__":
    main()
