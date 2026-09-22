from __future__ import annotations
import html as _html
from datetime import datetime
from urllib.parse import quote
from fasthtml.common import *

from .version import RELEASE_DATE, VERSION
from .db import CATEGORIES
from . import account_auth
from .logos import ANTHROPIC_SVG, OPENAI_SVG, GROK_SVG

ACCENT = "#7c3aed"
TINT = "#f5f3ff"
REPO_URL = "https://github.com/predictivelabsai/FastSkills"
FAVICON = "data:image/svg+xml," + quote(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="16" fill="#7c3aed"/>'
    '<path fill="white" d="M40 22c-2-3-5-4.5-9-4.5-6 0-10 3.4-10 8.2 0 4.3 3 6.6 8.6 8 '
    '4.4 1.1 5.8 1.9 5.8 3.7 0 1.8-1.7 3-4.6 3-3.2 0-5.3-1.4-6.6-3.9l-5.2 3c1.9 3.9 5.9 6 '
    '11.7 6 6.6 0 10.9-3.3 10.9-8.5 0-4.6-3.1-6.8-9-8.2-4.2-1-5.4-1.7-5.4-3.4 0-1.6 1.4-2.7 '
    '3.9-2.7 2.7 0 4.4 1.1 5.5 3.1z"/></svg>', safe="")

PARTNERS = (
    ("SAASPASS", "https://saaspass.com/", "https://saaspass.com/_next/static/assets/0176aeff921f6359fee88e796be31ace.png", "Full-stack identity and access management spanning MFA, SSO, passwordless access and integration APIs."),
    ("Sixty Four", "https://sixtyfour.ee/", "https://sixtyfour.ee/favicon.ico", "A senior Tallinn technology studio delivering software, AI consultancy, service design and public-sector programmes."),
    ("EDI Labs", "https://edilabs.tech/", "https://edilabs.tech/static/favicon.svg", "AI and data engineering for document intelligence, forecasting, geospatial systems and agentic workflows."),
    ("Predictive Labs", "https://predictivelabs.ai/", "https://predictivelabs.ai/static/favicon.svg", "Auditable AI systems for health, defence, public management, mobility and financial services."),
    ("Consistente", "https://consistente.tech/", "https://consistente.tech/static/favicon.svg", "Enterprise AI delivery across financial services, healthcare, the public sector and technology."),
)

CAT_COLOR = {"Finance": "#0f766e", "Trading": "#b45309", "Legal": "#1d4ed8", "Marketing": "#be185d"}

# Suggested sub-labels per category (see prompts/skill-labeller.md). Editable free
# text — these only populate the editor's autocomplete.
SUBLABELS = {
    "Finance": ["Family Office", "Investor CRM", "Fund Management", "Private Equity",
                "Venture Capital", "Private Credit", "M&A", "IPO & ECM", "Tax & Compliance"],
    "Trading": ["Backtesting", "Paper Trading", "Options", "Portfolio Management",
                "Validation", "Reconciliation", "Reporting"],
    "Legal": ["Contracts", "Privacy & Data Protection", "Litigation", "Corporate & Governance",
              "Regulatory & Compliance", "IP & Licensing", "AI Governance", "Legal Research",
              "Document Review", "Tax"],
    "Marketing": ["SEO", "Paid Ads", "Content", "Email & SMS", "Social", "Product Marketing",
                  "Growth & CRO", "Sales & Outbound", "Analytics", "Brand & PR",
                  "Pricing & Offers", "Community & Influencer", "Research", "Strategy"],
}

BASE_CSS = r"""
:root{--accent:#7c3aed;--tint:#f5f3ff;--ink:#172033;--muted:#667085;--line:#e5e7eb;--panel:#f8fafc}
*{box-sizing:border-box}body{margin:0;color:var(--ink);background:#fff;font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif}a{color:inherit}
.nav{height:68px;display:flex;align-items:center;justify-content:space-between;max-width:1200px;margin:auto;padding:0 24px}.brand{display:flex;align-items:center;gap:10px;text-decoration:none;font-weight:800}.mark{width:34px;height:34px;background:var(--accent);color:#fff;border-radius:10px;display:grid;place-items:center;font-weight:800}.navlinks{display:flex;gap:18px;align-items:center}.navlinks a{text-decoration:none;font-weight:600;color:var(--ink)}.btn{display:inline-flex;align-items:center;justify-content:center;border:0;border-radius:10px;background:var(--accent);color:#fff;padding:11px 17px;font-weight:700;text-decoration:none;cursor:pointer}.btn.ghost{background:#fff;color:var(--ink);border:1px solid var(--line)}.btn.sm{padding:8px 13px;font-size:13px}
.hero{max-width:1000px;margin:auto;padding:66px 24px 24px;text-align:center}.eyebrow{color:var(--accent);font-weight:800;font-size:12px;letter-spacing:.17em;text-transform:uppercase}.hero h1{font-size:clamp(38px,5.4vw,60px);line-height:1.04;letter-spacing:-.05em;margin:16px 0}.hero p{font-size:19px;line-height:1.6;color:var(--muted);max-width:660px;margin:0 auto}
.searchwrap{max-width:640px;margin:30px auto 0}.searchbar{display:flex;gap:10px}.searchbar input{flex:1;border:1px solid var(--line);border-radius:12px;padding:14px 16px;font:inherit;font-size:15px}.searchbar input:focus{outline:2px solid color-mix(in srgb,var(--accent) 22%,white);border-color:var(--accent)}
.workswith{display:flex;align-items:center;justify-content:center;gap:14px 24px;flex-wrap:wrap;margin:30px auto 0}.ww-label{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}.ww-item{display:inline-flex;align-items:center;gap:8px;color:#3f4654;font-weight:650;font-size:14px;text-decoration:none;transition:color .15s}.ww-item:hover{color:var(--accent)}.ww-item svg{height:20px;width:auto;display:block}.ww-item svg path{fill:currentColor}
.tabs{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;max-width:900px;margin:26px auto 0;padding:0 24px}.tab{border:1px solid var(--line);background:#fff;border-radius:99px;padding:9px 16px;font-weight:650;font-size:14px;text-decoration:none;color:var(--ink);display:inline-flex;gap:7px;align-items:center}.tab .count{color:var(--muted);font-size:12px}.tab.active{background:var(--accent);border-color:var(--accent);color:#fff}.tab.active .count{color:#ffffffcc}
.catwrap{max-width:1200px;margin:34px auto 0;padding:0 24px 70px}.catmeta{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;color:var(--muted);font-size:14px;flex-wrap:wrap;gap:10px}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.card{position:relative;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:16px;padding:20px;text-decoration:none;color:inherit;background:#fff;transition:box-shadow .15s,transform .15s}.card:hover{box-shadow:0 14px 40px #312e8118;transform:translateY(-2px)}
.card .stretch{text-decoration:none;color:inherit}.card .stretch::after{content:"";position:absolute;inset:0;z-index:0}
.cardclone{position:relative;z-index:1;border:1px solid var(--line);background:#fff;border-radius:8px;padding:6px 11px;font-size:12px;font-weight:700;color:var(--accent);cursor:pointer}.cardclone:hover{background:var(--tint);border-color:var(--accent)}.cardclone-form{position:relative;z-index:1;margin:0}
.cardfav-wrap{position:absolute;top:9px;right:12px;z-index:1}.cardfav-wrap form{margin:0}.cardfav{border:0;background:transparent;font-size:20px;line-height:1;color:#c7ccd6;cursor:pointer;padding:2px}.cardfav:hover{color:#f59e0b}.cardfav.on{color:#f59e0b}
.cardtop{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px;padding-right:26px}.catbadge{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;padding:4px 9px;border-radius:99px;color:#fff}.sublabel{font-size:11px;font-weight:700;color:var(--accent);background:var(--tint);border-radius:99px;padding:4px 9px}
.sublabelrow{display:flex;gap:8px;flex-wrap:wrap;max-width:1200px;margin:14px auto 0;padding:0 24px}.subchip{border:1px solid var(--line);background:#fff;border-radius:99px;padding:6px 13px;font-size:13px;font-weight:600;text-decoration:none;color:var(--ink)}.subchip .count{color:var(--muted);font-size:11px;margin-left:5px}.subchip.active{background:var(--accent);border-color:var(--accent);color:#fff}.subchip.active .count{color:#ffffffcc}
.card h3{margin:0 0 8px;font-size:18px;line-height:1.25}.card .desc{color:var(--muted);font-size:14px;line-height:1.55;margin:0;flex:1}
.cardfoot{display:flex;align-items:center;justify-content:space-between;margin-top:16px;font-size:12px;color:var(--muted)}.author{display:flex;align-items:center;gap:7px;font-weight:650;color:var(--ink)}.avatar{width:22px;height:22px;border-radius:99px;background:var(--tint);color:var(--accent);display:grid;place-items:center;font-size:11px;font-weight:800}
.tagrow{display:flex;gap:6px;flex-wrap:wrap;margin-top:12px}.tag{font-size:11px;color:var(--muted);background:var(--panel);border:1px solid var(--line);border-radius:99px;padding:2px 9px}
.empty{padding:60px 24px;text-align:center;color:var(--muted)}
.footer{max-width:1200px;margin:auto;padding:30px 24px;color:var(--muted);display:flex;align-items:center;justify-content:space-between;gap:14px 24px;flex-wrap:wrap;border-top:1px solid var(--line);font-size:14px}.footer a{text-decoration:none;color:var(--muted)}.footer a:hover{color:var(--accent)}.foot-right{display:flex;gap:20px;flex-wrap:wrap}.foot-right a{font-weight:600}
.features{background:var(--panel);padding:70px 24px;margin-top:20px}.featuregrid{max-width:1200px;margin:auto;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.feature{background:#fff;border:1px solid var(--line);border-radius:18px;padding:26px}.feature b{color:var(--accent)}.feature h2{font-size:19px;margin:8px 0}.feature p{color:var(--muted);line-height:1.6;margin:0}
.pricing,.partners{max-width:1200px;margin:auto;padding:70px 24px}.pricing h2,.partners h2{font-size:32px;margin:10px 0}.pricing>p,.partners>p{max-width:720px;color:var(--muted);line-height:1.65}.pricinggrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin-top:26px}.pricingcard{border:1px solid var(--line);border-radius:17px;padding:22px}.pricingprice{font-size:34px;font-weight:800;margin:10px 0}.partnergrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;margin-top:26px}.partner{min-width:0;border:1px solid var(--line);border-radius:17px;padding:18px;text-decoration:none}.partner img{width:40px;height:40px;object-fit:contain}.partner small{display:block;margin-top:12px;color:var(--accent);font-weight:800;text-transform:uppercase;letter-spacing:.08em;font-size:11px}.partner h3{margin:6px 0;font-size:16px}.partner p{font-size:12px;line-height:1.5;color:var(--muted);margin:0}
/* detail */
.detail{max-width:840px;margin:0 auto;padding:40px 24px 80px}.detailhead{border-bottom:1px solid var(--line);padding-bottom:22px;margin-bottom:26px}.detailhead h1{font-size:38px;letter-spacing:-.03em;margin:14px 0 10px}.detailmeta{display:flex;gap:14px;align-items:center;flex-wrap:wrap;color:var(--muted);font-size:13px}.detailactions{display:flex;gap:10px;margin-top:18px;flex-wrap:wrap}.detailactions .inlineform{margin:0}.btn.fav-on{color:#b45309;border-color:#f4c77b}.prov{font-size:13px;color:var(--muted);margin:10px 0 0}.prov a{color:var(--accent);font-weight:600}
.vtable{width:100%;border-collapse:collapse;margin-top:10px}.vtable th,.vtable td{text-align:left;padding:11px 12px;border-bottom:1px solid var(--line);font-size:14px}.vtable th{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}.vrow-current{background:var(--tint)}.vbadge{font-size:11px;font-weight:800;color:var(--accent);background:#fff;border:1px solid var(--accent);border-radius:99px;padding:2px 8px}.vactions{display:flex;gap:8px}
.prose{font-size:16px;line-height:1.72}.prose h1,.prose h2,.prose h3{line-height:1.25;margin-top:1.6em}.prose h1{font-size:28px}.prose h2{font-size:23px}.prose h3{font-size:19px}.prose pre{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;overflow:auto}.prose code{background:var(--panel);border-radius:5px;padding:1px 5px;font-size:.9em}.prose pre code{background:none;padding:0}.prose table{border-collapse:collapse;width:100%}.prose td,.prose th{border:1px solid var(--line);padding:7px 10px}.prose blockquote{border-left:3px solid var(--accent);margin:1em 0;padding-left:14px;color:var(--muted)}.prose img{max-width:100%}
/* editor shell */
.shell{display:grid;grid-template-columns:250px minmax(0,1fr);min-height:100vh}.sidebar{background:#f8fafc;border-right:1px solid var(--line);padding:18px;overflow:auto}.sidehead{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.side-user{font-size:12px;color:var(--muted);padding:10px 0;border-bottom:1px solid var(--line);margin-bottom:12px}.sideitem{display:block;text-decoration:none;padding:8px 10px;border-radius:8px;font-size:14px;color:var(--ink)}.sideitem:hover,.sideitem.active{background:var(--tint);color:var(--accent)}.sidelabel{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:16px 0 4px;padding:0 10px}
.workspace{overflow:auto}.topbar{height:58px;border-bottom:1px solid var(--line);display:flex;align-items:center;gap:12px;padding:0 22px;position:sticky;top:0;background:#fffc;backdrop-filter:blur(10px);z-index:3}.status{font-size:12px;color:var(--muted)}.pageactions{display:flex;gap:8px;align-items:center;margin-left:auto}.inlineform{display:inline-flex;margin:0}
.editorwrap{max-width:880px;margin:auto;padding:40px 42px 70px}.titleinput{border:0;width:100%;font-size:38px;font-weight:800;letter-spacing:-.03em;outline:0;color:var(--ink)}
.metagrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:20px 0 8px}.metafield label{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-bottom:5px}.metafield input,.metafield select,.metafield textarea{width:100%;border:1px solid var(--line);border-radius:9px;padding:9px 11px;font:inherit}.metafield.full{grid-column:1/-1}.metafield textarea{min-height:56px;resize:vertical}
.toolbar{display:flex;gap:4px;flex-wrap:wrap;margin:18px 0 14px;padding:7px;border:1px solid var(--line);border-radius:11px;position:sticky;top:58px;background:#fff;z-index:2}.tool{border:0;background:#fff;border-radius:6px;padding:7px 9px;cursor:pointer}.tool:hover{background:var(--tint)}.tool.mode{border:1px solid var(--line);font-weight:700}.tool.mode.active{background:var(--accent);border-color:var(--accent);color:#fff}.toolbar-spacer{flex:1}
.editor{min-height:400px;outline:0;font-size:16px;line-height:1.72}.editor h1,.editor h2,.editor h3{line-height:1.2}.editor img{max-width:100%}.editor table{border-collapse:collapse}.editor td,.editor th{border:1px solid var(--line);padding:7px}.ProseMirror:focus{outline:0}
.markdown-editor{width:100%;min-height:400px;border:1px solid var(--line);border-radius:10px;padding:14px;font:14px/1.55 ui-monospace,SFMono-Regular,Menlo,monospace;resize:vertical;outline:0}
.block-editor{min-height:400px}.block-actions{margin-bottom:10px}.block-list{display:flex;flex-direction:column;gap:7px}.block-row{display:grid;grid-template-columns:auto 122px minmax(0,1fr) auto;gap:8px;align-items:start;padding:7px;border:1px solid transparent;border-radius:10px}.block-row:hover{border-color:var(--line);background:#f8fafc}.block-format{display:flex;gap:2px;padding-top:4px}.block-format button{width:25px;height:25px;border:1px solid var(--line);border-radius:5px;background:#fff;cursor:pointer;font-size:11px}.block-type{width:100%;border:1px solid var(--line);border-radius:7px;background:#fff;padding:7px;font:inherit;font-size:12px}.block-body{min-width:0}.block-edit,.block-raw{width:100%;min-height:42px;border:1px solid var(--line);border-radius:8px;background:#fff;padding:8px 10px;font:inherit;line-height:1.5;outline:0}.block-edit.heading1{font-size:26px;font-weight:800}.block-edit.heading2{font-size:21px;font-weight:750}.block-edit.heading3{font-size:18px;font-weight:700}.block-edit.quote{border-left:4px solid var(--accent);color:var(--muted);font-style:italic}.block-raw{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;resize:vertical}.block-controls{display:flex;gap:2px}.block-control{border:0;background:transparent;color:var(--muted);border-radius:5px;padding:5px;cursor:pointer}.block-control:hover{background:var(--tint);color:var(--accent)}.block-table{border-collapse:collapse;width:100%;font-size:13px}.block-table td,.block-table th{border:1px solid var(--line);padding:7px;min-width:75px}.block-table th{background:var(--tint)}.block-table-tools{display:flex;gap:5px;margin-top:5px}
.breadcrumbs{display:flex;gap:7px;align-items:center;flex-wrap:wrap;color:var(--muted);font-size:12px;margin-bottom:12px}.breadcrumbs a{text-decoration:none}.pagebadge{border-radius:99px;background:#fff7ed;color:#9a3412;font-size:10px;font-weight:800;padding:2px 7px;text-transform:uppercase}.pagebadge.published{background:#ecfdf3;color:#027a48}.pagebadge.public{background:#eef2ff;color:#3730a3}.pagebadge.private{background:#f3f4f6;color:#374151}
.release{display:block;padding:14px 10px 0;color:var(--muted);font-size:10px}
.docs{max-width:1180px;margin:0 auto;padding:36px 24px 90px;display:grid;grid-template-columns:236px minmax(0,1fr);gap:52px}
.toc{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 110px);overflow:auto}.toc h4{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted);margin:0 0 10px;padding:0 10px}.toc a{display:block;padding:6px 10px;border-radius:8px;text-decoration:none;color:var(--muted);font-size:13.5px;border-left:2px solid transparent;line-height:1.35}.toc a:hover{color:var(--ink);background:var(--panel)}.toc a.active{color:var(--accent);border-left-color:var(--accent);background:var(--tint);font-weight:650}
.doc-body{min-width:0}.doc-body h1{font-size:40px;letter-spacing:-.03em;margin:0 0 10px}.doc-lead{font-size:18px;color:var(--muted);line-height:1.6;margin:0 0 6px}
.doc-section{scroll-margin-top:88px;padding:30px 0;border-top:1px solid var(--line)}.doc-section h2{font-size:25px;letter-spacing:-.02em;margin:0 0 14px}.doc-section h3{font-size:17px;margin:24px 0 8px}.doc-section p,.doc-section li{line-height:1.72;color:var(--ink);font-size:15.5px}.doc-section p{margin:11px 0}.doc-section ul,.doc-section ol{padding-left:22px;margin:11px 0}.doc-section li{margin:5px 0}.doc-section a{color:var(--accent);font-weight:600;text-decoration:none}.doc-section a:hover{text-decoration:underline}
.doc-section code{background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-size:.88em}.doc-section pre{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:15px 16px;overflow:auto;margin:14px 0}.doc-section pre code{background:none;border:0;padding:0;font-size:13px;line-height:1.6}
.doc-section table{border-collapse:collapse;width:100%;margin:14px 0;display:block;overflow-x:auto}.doc-section th,.doc-section td{border:1px solid var(--line);padding:9px 11px;text-align:left;font-size:14px;vertical-align:top}.doc-section th{background:var(--panel);font-weight:700}
.callout{border:1px solid var(--line);border-left:3px solid var(--accent);background:var(--tint);border-radius:10px;padding:13px 16px;margin:16px 0;font-size:14.5px;line-height:1.6}
@media(max-width:860px){.docs{grid-template-columns:1fr;gap:0}.toc{display:none}}
@media(max-width:960px){.grid,.featuregrid,.partnergrid{grid-template-columns:1fr 1fr}}
@media(max-width:760px){.grid,.featuregrid,.partnergrid,.pricinggrid,.metagrid{grid-template-columns:1fr}.shell{grid-template-columns:1fr}.sidebar{display:none}.editorwrap{padding:28px 18px}}
"""


def head(title, description="An open, searchable catalog of reusable skills for Finance, Trading, Legal and Marketing."):
    return Head(
        Title(title), Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width,initial-scale=1"),
        Meta(name="description", content=description),
        Link(rel="icon", type="image/svg+xml", href=FAVICON),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap"),
        Style(BASE_CSS), Style(account_auth.AUTH_CSS))


def _initial(letter):
    return (letter or "?").strip()[:1].upper() or "?"


def public_nav(who):
    if who:
        right = Div(
            A("Browse", href="/"),
            A("Docs", href="/docs"),
            A("My Skills", href="/mine"),
            A("New Skill", href="/skills/new", cls="btn sm"),
            Span(_initial(who.get("name") or who["email"]), cls="avatar", title=who.get("name")),
            A("Sign out", href="/logout"),
            cls="navlinks")
    else:
        right = Div(
            A("Browse", href="/"),
            A("Docs", href="/docs"),
            Button("Sign in", cls="btn ghost sm", onclick="authOpen('login')", type="button"),
            Button("Add a skill", cls="btn sm", onclick="authOpen('register')", type="button"),
            cls="navlinks")
    return Nav(A(Span("S", cls="mark"), "FastSkills", href="/", cls="brand"), right, cls="nav")


LINKEDIN_URL = "https://www.linkedin.com/company/predictive-labs-ltd"
PREDICTIVELABS_URL = "https://predictivelabs.ai"


def site_footer():
    return Footer(
        Div("© ", str(datetime.now().year), " ",
            A("Predictive Labs Ltd", href=PREDICTIVELABS_URL, target="_blank", rel="noopener"),
            " · Part of the open-source ",
            A("FastSME", href="https://fastsme.com", target="_blank", rel="noopener"), " suite.",
            cls="foot-left"),
        Div(A("GitHub", href=REPO_URL, target="_blank", rel="noopener"),
            A("LinkedIn", href=LINKEDIN_URL, target="_blank", rel="noopener"),
            A("predictivelabs.ai", href=PREDICTIVELABS_URL, target="_blank", rel="noopener"),
            cls="foot-right"),
        cls="footer")


def skill_card(item, who=None, fav_ids=None):
    color = CAT_COLOR.get(item["category"], ACCENT)
    tags = [t.strip() for t in (item.get("tags") or "").split(",") if t.strip()][:3]
    author = item.get("author_label") or item.get("owner_name") or "Community"
    clone = (Form(Button("⑂ Clone", type="submit", cls="cardclone"), method="post",
                  action=f"/skills/{item['id']}/clone", cls="inlineform cardclone-form")
             if who else
             Button("⑂ Clone", type="button", cls="cardclone", title="Sign in to clone",
                    onclick="authOpen('login')"))
    faved = bool(fav_ids and item["id"] in fav_ids)
    fav_inner = (Form(Button("★" if faved else "☆", type="submit",
                             cls="cardfav" + (" on" if faved else ""),
                             title="Remove bookmark" if faved else "Bookmark"),
                      method="post", action=f"/skills/{item['id']}/favourite", cls="inlineform")
                 if who else
                 Button("☆", type="button", cls="cardfav", title="Sign in to bookmark",
                        onclick="authOpen('login')"))
    return Div(
        Div(fav_inner, cls="cardfav-wrap"),
        Div(Span(item["category"], cls="catbadge", style=f"background:{color}"),
            (Span(item["sub_label"], cls="sublabel") if item.get("sub_label") else None),
            (Span("Private", cls="pagebadge private") if item["visibility"] == "private" else None),
            cls="cardtop"),
        A(H3(item["title"]), href=f"/skills/{item['id']}", cls="stretch"),
        P((item.get("description") or (item.get("plain_text") or "")[:150]), cls="desc"),
        (Div(*[Span(t, cls="tag") for t in tags], cls="tagrow") if tags else None),
        Div(Div(Span(_initial(author), cls="avatar"), author, cls="author"), clone,
            cls="cardfoot"),
        cls="card")


def catalog_page(who, items, counts, active_category=None, q="", total=0,
                 sublabels=(), active_sub=None, fav_ids=None):
    tabs = [A("All", Span(str(total), cls="count"),
              href="/" + (f"?q={quote(q)}" if q else ""),
              cls="tab" + ("" if active_category else " active"))]
    for c in CATEGORIES:
        params = f"?category={quote(c)}" + (f"&q={quote(q)}" if q else "")
        tabs.append(A(c, Span(str(counts.get(c, 0)), cls="count"), href="/" + params,
                      cls="tab" + (" active" if active_category == c else "")))
    sub_row = None
    if active_category and sublabels:
        qs = f"&q={quote(q)}" if q else ""
        chips = [A("All", href=f"/?category={quote(active_category)}{qs}",
                   cls="subchip" + ("" if active_sub else " active"))]
        for s in sublabels:
            chips.append(A(s["sub_label"], Span(str(s["n"]), cls="count"),
                           href=f"/?category={quote(active_category)}&sub={quote(s['sub_label'])}{qs}",
                           cls="subchip" + (" active" if active_sub == s["sub_label"] else "")))
        sub_row = Div(*chips, cls="sublabelrow")
    grid = (Div(*[skill_card(i, who, fav_ids) for i in items], cls="grid") if items
            else Div("No skills match your search yet.", cls="empty"))
    heading = (f"{active_category} · {active_sub}" if active_sub else active_category) \
        or ("Results" if q else "All skills")
    return Html(
        head("FastSkills · The open skills library"),
        Body(
            public_nav(who),
            Section(
                Span("Open skills library", cls="eyebrow"),
                H1("Find the skill for the job."),
                P("A searchable catalog of reusable skills across Finance, Trading, Legal and Marketing — contribute your own, keep it private or share it public."),
                Form(Div(Input(name="q", value=q, placeholder="Search skills, tags, authors…", cls="search"),
                         Button("Search", cls="btn"), cls="searchbar"),
                     (Input(type="hidden", name="category", value=active_category) if active_category else None),
                     method="get", action="/", cls="searchwrap"),
                Div(Span("Works with", cls="ww-label"),
                    A(NotStr(ANTHROPIC_SVG), "Anthropic", href="https://www.anthropic.com",
                      target="_blank", rel="noopener noreferrer", cls="ww-item"),
                    A(NotStr(OPENAI_SVG), "ChatGPT", href="https://chatgpt.com",
                      target="_blank", rel="noopener noreferrer", cls="ww-item"),
                    A(NotStr(GROK_SVG), "xAI / Grok", href="https://x.ai",
                      target="_blank", rel="noopener noreferrer", cls="ww-item"),
                    cls="workswith"),
                cls="hero"),
            Div(*tabs, cls="tabs"),
            sub_row,
            Div(Div(Span(f"{len(items)} skill{'s' if len(items) != 1 else ''} · {heading}"),
                    (A("+ Add your skill", href="/skills/new", cls="btn ghost sm") if who
                     else Button("+ Add your skill", cls="btn ghost sm", onclick="authOpen('register')", type="button")),
                    cls="catmeta"),
                grid, cls="catwrap"),
            site_footer(),
            account_auth.auth_modal("FastSkills"),
            Script(account_auth.AUTH_JS)))


def detail_page(who, item, body_html, faved=False):
    color = CAT_COLOR.get(item["category"], ACCENT)
    tags = [t.strip() for t in (item.get("tags") or "").split(",") if t.strip()]
    author = item.get("author_label") or item.get("owner_name") or "Community"
    editable = who and (item["owner_id"] == who["sub"])
    clone_btn = (Form(Button("⑂ Clone", cls="btn"), method="post",
                      action=f"/skills/{item['id']}/clone", cls="inlineform")
                 if who else
                 Button("⑂ Clone", cls="btn", type="button", onclick="authOpen('login')"))
    fav_btn = (Form(Button(("★ Bookmarked" if faved else "☆ Bookmark"),
                           cls="btn ghost" + (" fav-on" if faved else "")),
                    method="post", action=f"/skills/{item['id']}/favourite", cls="inlineform")
               if who else
               Button("☆ Bookmark", type="button", cls="btn ghost",
                      onclick="authOpen('login')"))
    actions = [clone_btn, fav_btn,
               A(f"History · v{item['version']}", href=f"/skills/{item['id']}/versions", cls="btn ghost"),
               A("Download SKILL.md", href=f"/skills/{item['id']}/download", cls="btn ghost")]
    if item.get("source_url"):
        actions.append(A("View source", href=item["source_url"], target="_blank", rel="noopener", cls="btn ghost"))
    elif item.get("seeded"):
        actions.append(A("View in GitHub", href=f"{REPO_URL}/tree/main/seed/{item['category'].lower()}",
                         target="_blank", rel="noopener", cls="btn ghost"))
    if editable:
        actions.append(A("Edit", href=f"/skills/{item['id']}/edit", cls="btn ghost"))
    meta = [Span(_initial(author), cls="avatar"), B(author),
            Span("·"), Span(item["category"]),
            (Span("·") if item.get("license") else None),
            (Span(item["license"]) if item.get("license") else None)]
    return Html(
        head(f"{item['title']} · FastSkills", item.get("description") or ""),
        Body(
            public_nav(who),
            Div(
                Div(Div(*[A("Browse", href="/"), Span("/"), Span(item["category"])], cls="breadcrumbs"),
                    Span(Span(item["category"], cls="catbadge", style=f"background:{color}"),
                         (A(item["sub_label"], href=f"/?category={quote(item['category'])}&sub={quote(item['sub_label'])}",
                            cls="sublabel", style="text-decoration:none;margin-left:8px") if item.get("sub_label") else None),
                         style="display:inline-flex;align-items:center"),
                    H1(item["title"]),
                    (P(item["description"], style="color:var(--muted);font-size:17px;margin:0 0 6px") if item.get("description") else None),
                    Div(*[m for m in meta if m is not None], cls="detailmeta"),
                    (P("⑂ Forked from ", A(item["forked_from_title"] or "the original",
                                           href=f"/skills/{item['forked_from']}"), cls="prov")
                     if item.get("forked_from") else None),
                    (P("Library skill — the default version is maintained in GitHub; edits you make live in your own clone.",
                       cls="prov") if item.get("seeded") else None),
                    (Div(*[Span(t, cls="tag") for t in tags], cls="tagrow") if tags else None),
                    Div(*actions, cls="detailactions"),
                    cls="detailhead"),
                Div(NotStr(body_html), cls="prose"),
                cls="detail"),
            site_footer(),
            account_auth.auth_modal("FastSkills"),
            Script(account_auth.AUTH_JS)))


def _fmt(ts):
    if not ts:
        return ""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%d %b %Y, %H:%M UTC")
    except (ValueError, AttributeError):
        return ts


def versions_page(who, item, history, can_edit):
    rows_html = []
    for h in history:
        vlabel = Span(f"v{h['version']}",
                      cls="vbadge") if h["current"] else f"v{h['version']}"
        if h["current"]:
            actions = [A("Edit", href=f"/skills/{item['id']}/edit", cls="btn ghost sm")] if can_edit else []
        else:
            actions = [A("View", href=f"/skills/{item['id']}/versions/{h['version_id']}", cls="btn ghost sm")]
            if can_edit:
                actions.append(Form(Button("Restore", cls="btn ghost sm"), method="post",
                                    action=f"/skills/{item['id']}/versions/{h['version_id']}/restore",
                                    cls="inlineform"))
        rows_html.append(Tr(
            Td(vlabel, " ", Span("current", style="color:var(--muted);font-size:12px") if h["current"] else ""),
            Td(h["title"]),
            Td(_fmt(h["created_at"])),
            Td(Div(*actions, cls="vactions")),
            cls="vrow-current" if h["current"] else ""))
    note = (P("The default version of this library skill is maintained in GitHub. "
              "Versions below are database edits; clone it to keep your own versioned copy.",
              cls="prov") if item.get("seeded") else
            P("Every save creates a new version. You can view or restore any earlier one.",
              cls="prov"))
    return Html(
        head(f"History · {item['title']} · FastSkills"),
        Body(
            public_nav(who),
            Div(
                Div(*[A("Browse", href="/"), Span("/"),
                      A(item["title"], href=f"/skills/{item['id']}"), Span("/"), Span("History")],
                    cls="breadcrumbs"),
                H1("Version history"),
                note,
                Table(Thead(Tr(Th("Version"), Th("Title"), Th("When"), Th("Actions"))),
                      Tbody(*rows_html), cls="vtable"),
                cls="detail"),
            site_footer(),
            account_auth.auth_modal("FastSkills"), Script(account_auth.AUTH_JS)))


def snapshot_page(who, item, snap, body_html, can_edit):
    restore = (Form(Button("Restore this version", cls="btn"), method="post",
                    action=f"/skills/{item['id']}/versions/{snap['id']}/restore", cls="inlineform")
               if can_edit else None)
    return Html(
        head(f"v{snap['version']} · {item['title']} · FastSkills"),
        Body(
            public_nav(who),
            Div(
                Div(*[A("Browse", href="/"), Span("/"),
                      A(item["title"], href=f"/skills/{item['id']}"), Span("/"),
                      A("History", href=f"/skills/{item['id']}/versions"), Span("/"),
                      Span(f"v{snap['version']}")], cls="breadcrumbs"),
                Div(Span(f"Version {snap['version']}", cls="vbadge"),
                    Span(f"  saved {_fmt(snap['created_at'])}", cls="prov"),
                    style="display:flex;align-items:center;gap:10px;margin:10px 0"),
                H1(snap["title"]),
                Div(*[e for e in [restore,
                                  A("Back to history", href=f"/skills/{item['id']}/versions", cls="btn ghost")]
                      if e is not None], cls="detailactions"),
                Div(NotStr(body_html), cls="prose", style="margin-top:24px"),
                cls="detail"),
            site_footer(),
            account_auth.auth_modal("FastSkills"), Script(account_auth.AUTH_JS)))


DOCS_JS = r"""
const _tl=[...document.querySelectorAll('.toc a')];
const _tm=new Map(_tl.map(a=>[a.getAttribute('href').slice(1),a]));
const _io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){_tl.forEach(l=>l.classList.remove('active'));const a=_tm.get(e.target.id);if(a)a.classList.add('active')}})},{rootMargin:'-45% 0px -50% 0px'});
document.querySelectorAll('.doc-section').forEach(s=>_io.observe(s));
"""


def _skill_example():
    return ("---\n"
            "title: NDA Review\n"
            "description: Review a one-way NDA and produce a clause-by-clause issue log.\n"
            "category: Legal\n"
            "sublabel: Contracts\n"
            "author: Your Name\n"
            "tags: nda, contracts, review\n"
            "license: MIT\n"
            "---\n\n"
            "# NDA Review\n\n"
            "## When to use\n"
            "- Reviewing a one-way commercial NDA before signature.\n\n"
            "## Steps\n"
            "1. Identify the parties, term, and definition of Confidential Information.\n"
            "2. Flag one-sided or unusual clauses with a preferred redline.\n"
            "3. Output an issue log: clause, risk, recommendation.\n")


def docs_page(who):
    sections = [
        ("overview", "Overview", [
            P("FastSkills is an open, searchable catalog of reusable ", B("skills"),
              " for AI assistants — packaged instructions that teach a model how to perform "
              "a specific task well. Every skill is a plain Markdown file you can read, "
              "download, clone and version. The library is organised into four domains — ",
              B("Finance, Trading, Legal and Marketing"), " — each with a second level of "
              "sub-labels for quick navigation."),
            P("Skills follow the open ", B("SKILL.md"), " format, so a skill you find here "
              "works with any assistant that supports it — including Claude, ChatGPT and Grok."),
            Div("New here? Jump to ", A("Using a skill", href="#use"),
                " to put one to work in a couple of minutes, or ", A("Creating & editing", href="#editor"),
                " to publish your own.", cls="callout"),
        ]),
        ("what-is-a-skill", "What is a skill?", [
            P("A skill is a self-contained set of instructions that gives an assistant "
              "specialised, repeatable expertise for one job — a legal review checklist, a "
              "deal-screening procedure, an SEO audit, a backtesting workflow. Instead of "
              "re-explaining the same process every time, you hand the model a skill and it "
              "follows a consistent, auditable procedure."),
            P("Concretely, a skill is a folder whose entry point is a ", Code("SKILL.md"),
              " file. That file carries a little metadata plus the instructions themselves. "
              "A skill can also bundle supporting files:"),
            Pre(Code("my-skill/\n"
                     "├── SKILL.md        # required: metadata + instructions\n"
                     "├── references/     # optional: background material\n"
                     "├── scripts/        # optional: helper code\n"
                     "└── assets/         # optional: templates, examples")),
            P("On FastSkills, the ", Code("SKILL.md"), " body is the part you read on a "
              "skill's page and download; larger skills link out to their full source."),
        ]),
        ("skill-format", "The SKILL.md format", [
            P("A ", Code("SKILL.md"), " file starts with a YAML ", B("frontmatter"),
              " block (between ", Code("---"), " lines) and is followed by the instructions "
              "in Markdown. FastSkills reads these frontmatter fields:"),
            Table(
                Thead(Tr(Th("Field"), Th("Purpose"))),
                Tbody(
                    Tr(Td(Code("title")), Td("Display name of the skill.")),
                    Tr(Td(Code("description")), Td("One line shown on the catalog card and used for search.")),
                    Tr(Td(Code("category")), Td("One of Finance, Trading, Legal, Marketing.")),
                    Tr(Td(Code("sublabel")), Td("The second-level label within the category (e.g. Contracts).")),
                    Tr(Td(Code("author")), Td("Attribution shown on the card and detail page.")),
                    Tr(Td(Code("tags")), Td("Comma-separated keywords for search and filtering.")),
                    Tr(Td(Code("license")), Td("Licence the skill is shared under (e.g. MIT).")),
                    Tr(Td(Code("source")), Td("Optional link to the upstream repository or original.")),
                )),
            H3("A minimal example"),
            Pre(Code(_skill_example())),
            P("A good body answers three questions: ", B("when to use"), " the skill, the ",
              B("steps"), " to follow, and the ", B("output"), " it should produce. Keep it "
              "specific and action-oriented — the clearer the procedure, the more reliably a "
              "model follows it."),
        ]),
        ("how-it-works", "How skills load", [
            P("Skills are designed to stay out of the way until they're needed, through "
              "progressive disclosure:"),
            Ul(Li(B("Discovery"), " — an assistant first sees only each skill's name and "
                  "description, enough to know when it might be relevant."),
               Li(B("Activation"), " — when a task matches, it reads the full ", Code("SKILL.md"),
                  " instructions into context."),
               Li(B("Execution"), " — it follows the steps, loading any referenced files or "
                  "running bundled scripts only if the task calls for them.")),
            P("Because full instructions load only on demand, an assistant can keep many "
              "skills available while spending very little context on the ones it isn't using."),
        ]),
        ("categories", "Categories & sub-labels", [
            P("Every skill sits in one of four categories, each split into sub-labels so you "
              "can drill down quickly. Pick a category tab on the home page, then a sub-label "
              "chip to narrow further."),
            Table(
                Thead(Tr(Th("Category"), Th("Sub-labels"))),
                Tbody(*[Tr(Td(B(c)), Td(", ".join(SUBLABELS[c]))) for c in CATEGORIES])),
            P("Sub-labels are assigned with a documented taxonomy and labelling prompt kept in "
              "the repository, so classification stays consistent as the library grows. When "
              "you author a skill, the editor suggests the sub-labels for its category."),
        ]),
        ("browse", "Browsing & searching", [
            P("The home page is the catalog. You can:"),
            Ul(Li("Search titles, descriptions, tags and content from the search bar."),
               Li("Filter by category (the tabs) and then by sub-label (the chips)."),
               Li("Open any card to read the full skill, or use the clone button to fork it.")),
            P("Filters are just URL parameters, so links are shareable — for example ",
              Code("/?category=Finance&sub=Family%20Office"), " or ", Code("/?q=backtest"), "."),
        ]),
        ("use", "Using a skill", [
            P("Open a skill and choose ", B("Download SKILL.md"), " to get the file. From there "
              "it works with any assistant that reads the format:"),
            Ul(Li(B("Claude / Claude Code"), " — place the skill in your skills directory (or a "
                  "project), and Claude loads it when a task matches its description."),
               Li(B("ChatGPT"), " — add the instructions to a Project or a Custom GPT so they "
                  "apply to that workspace."),
               Li(B("Grok"), " — paste the instructions into your custom/system instructions.")),
            P("However you load it, the pattern is the same: the metadata tells the assistant "
              "when the skill is relevant, and the body tells it exactly what to do. Nothing on "
              "FastSkills is provider-specific — the same skill is portable across tools."),
            Div("Tip: keep skills small and focused. One clear job per skill beats a sprawling "
                "document — it activates more reliably and is easier to maintain.", cls="callout"),
        ]),
        ("clone", "Cloning a skill", [
            P("Every skill — on its detail page and on each catalog card — has a ", B("⑂ Clone"),
              " button, like a fork on a code host. Cloning:"),
            Ul(Li("Creates a private draft that ", B("you own"), ", pre-populated with the "
                  "original's title, content, category, sub-label and tags."),
               Li("Opens it straight in the editor so you can adapt it."),
               Li("Records where it came from — the clone shows a “forked from” link back to "
                  "the original, preserving attribution.")),
            P("If you're signed out, the clone button opens the sign-in dialog first; once "
              "you're in, clone again and your copy is created."),
        ]),
        ("versioning", "Versioning", [
            P("FastSkills keeps two kinds of version:"),
            Ul(Li(B("Default (library) versions"), " live in GitHub. The catalog's built-in "
                  "skills are seeded from the repository, so their canonical history is the "
                  "commit history — library skills carry a badge and a “View in GitHub” link."),
               Li(B("Your versions"), " live in the database. Every time you save a skill you "
                  "own, a new version is recorded.")),
            P("Open ", B("History"), " on any skill to see the full list of versions with "
              "timestamps. You can view any earlier version read-only, and — on skills you own "
              "— restore one, which brings it back as the current version while keeping the "
              "prior state in the history."),
        ]),
        ("editor", "Creating & editing", [
            P("Use ", B("New Skill"), " to start from scratch, or clone an existing one. The "
              "editor gives you three interchangeable writing surfaces for the body:"),
            Ul(Li(B("Rich"), " — a formatted editor for prose, lists, tables and code."),
               Li(B("Blocks"), " — a block-by-block view for restructuring."),
               Li(B("Markdown"), " — raw Markdown, if you prefer to write it directly."))
            ,
            P("Alongside the body you set the metadata — category, sub-label (with "
              "suggestions), author label, tags, a short description and visibility. Changes "
              "autosave as you type, and each save creates a version. When it's ready, ",
              B("Publish"), " it; you can always move it back to draft."),
        ]),
        ("visibility", "Public & private", [
            P("Every skill has an owner and a visibility setting:"),
            Ul(Li(B("Public"), " (the default) — listed in the catalog for everyone once "
                  "published."),
               Li(B("Private"), " — visible only to you; useful for drafts or internal skills.")),
            P("Your skills — public and private, drafts included — live under ", B("My Skills"),
              ". Author attribution (the name on the card) is separate from ownership, so you "
              "can credit an original author while owning your own copy."),
        ]),
        ("contribute", "Contributing", [
            P("There are two ways to add to FastSkills:"),
            Ul(Li("Create a skill in the app and publish it public — it appears in the catalog "
                  "immediately, owned by you."),
               Li("Contribute a library skill via the repository: add a ", Code("SKILL.md"),
                  " under the ", Code("seed/"), " tree and open a pull request. Library skills "
                  "are re-applied on deploy, so an approved change lands automatically.")),
            P("The catalog and the repository stay in sync: library skills are the default "
              "versions in GitHub; anyone can clone them into their own editable copy."),
        ]),
        ("api", "API reference", [
            P("A read-only JSON API is available for the public catalog:"),
            Table(
                Thead(Tr(Th("Endpoint"), Th("Returns"))),
                Tbody(
                    Tr(Td(Code("GET /api/skills")), Td("List public skills; filter with "
                        + "?category=, ?sub=, ?q=, ?author=.")),
                    Tr(Td(Code("GET /api/categories")), Td("The categories with skill counts.")),
                    Tr(Td(Code("GET /api/skills/{id}")), Td("One skill, including its markdown "
                        + "and content.")),
                )),
            P("Interactive docs live at ", A("/api/docs", href="/api/docs"), "."),
        ]),
        ("selfhost", "Self-hosting", [
            P("FastSkills is open source. It's a single FastHTML application backed by SQLite "
              "or PostgreSQL, packaged as a small Docker image. You can run your own private "
              "catalog for a team, seeded from your own ", Code("seed/"), " tree."),
            P("See the ", A("repository", href=REPO_URL, target="_blank", rel="noopener"),
              " for setup, configuration and deployment instructions."),
        ]),
        ("faq", "FAQ", [
            H3("Do I need an account to browse?"),
            P("No — browsing, searching and downloading are open. You need an account only to "
              "clone, create or edit skills."),
            H3("Which assistants does a skill work with?"),
            P("Any that support the SKILL.md format, including Claude, ChatGPT and Grok. The "
              "content is provider-neutral."),
            H3("Who can edit a library skill?"),
            P("Library (default) skills are maintained in GitHub. To make your own changes, "
              "clone one — your edits become a versioned copy you own in the database."),
            H3("How are sub-labels decided?"),
            P("From a fixed per-category taxonomy and a labelling prompt kept in the "
              "repository, so classification is consistent and reproducible."),
        ]),
    ]
    toc = Nav(H4("On this page"),
              *[A(title, href=f"#{sid}") for sid, title, _ in sections], cls="toc")
    body = Div(
        H1("Documentation"),
        P("Everything you need to find, use, create and share skills on FastSkills.",
          cls="doc-lead"),
        *[Section(H2(title), *content, id=sid, cls="doc-section")
          for sid, title, content in sections],
        cls="doc-body")
    return Html(
        head("Documentation · FastSkills",
             "How to find, use, create and share AI skills on FastSkills."),
        Body(
            public_nav(who),
            Div(toc, body, cls="docs"),
            site_footer(),
            account_auth.auth_modal("FastSkills"),
            Script(account_auth.AUTH_JS), Script(DOCS_JS)))


def _sidebar(who, active=""):
    def item(label, href, key):
        return A(label, href=href, cls="sideitem" + (" active" if key == active else ""))
    cat_links = [A(c, href=f"/?category={quote(c)}", cls="sideitem") for c in CATEGORIES]
    return Aside(
        Div(A(Span("S", cls="mark"), "FastSkills", href="/", cls="brand"),
            A("＋", href="/skills/new", title="New skill"), cls="sidehead"),
        Div(f"{who.get('name') or who['email']}", cls="side-user"),
        item("Browse all", "/", "browse"),
        item("★ Favourites", "/favourites", "favourites"),
        item("My Skills", "/mine", "mine"),
        item("New Skill", "/skills/new", "new"),
        Div("Categories", cls="sidelabel"), *cat_links,
        A("Sign out", href="/logout", cls="sideitem", style="margin-top:14px"),
        Span(f"v{VERSION} · {RELEASE_DATE}", cls="release"),
        cls="sidebar")


def favourites_page(who, items, counts, category=None):
    total = sum(counts.values())
    fav_ids = {i["id"] for i in items}
    tabs = [A("All", Span(str(total), cls="count"), href="/favourites",
              cls="tab" + ("" if category else " active"))]
    for c in CATEGORIES:
        n = counts.get(c, 0)
        if n or category == c:
            tabs.append(A(c, Span(str(n), cls="count"), href=f"/favourites?category={quote(c)}",
                          cls="tab" + (" active" if category == c else "")))
    cards = (Div(*[skill_card(i, who, fav_ids) for i in items], cls="grid") if items else
             Div(P("No bookmarks yet."),
                 P("Browse the catalog and tap the ☆ on any skill to save it here.", cls="prov"),
                 A("Browse skills", href="/", cls="btn", style="margin-top:12px"), cls="empty"))
    return Html(head("Favourites · FastSkills"),
                Body(_sidebar(who, "favourites"),
                     Main(Div(H1("Favourites", style="margin:6px 0 4px"),
                              P("Skills you've bookmarked.", cls="prov"),
                              Div(*tabs, cls="tabs", style="justify-content:flex-start;margin-top:16px"),
                              Div(cards, style="margin-top:20px"),
                              cls="catwrap", style="margin-top:26px"),
                          cls="workspace"),
                     cls="shell"))


def mine_page(who, items, fav_ids=None):
    cards = (Div(*[skill_card(i, who, fav_ids) for i in items], cls="grid") if items
             else Div(P("You haven't created any skills yet."),
                      A("Create your first skill", href="/skills/new", cls="btn"), cls="empty"))
    return Html(head("My Skills · FastSkills"),
                Body(_sidebar(who, "mine"),
                     Main(Div(Div(Span(f"{len(items)} skill{'s' if len(items) != 1 else ''}"),
                                  A("+ New Skill", href="/skills/new", cls="btn sm"), cls="catmeta"),
                              H1("My Skills", style="margin:6px 0 20px"), cards,
                              cls="catwrap", style="margin-top:26px"),
                          cls="workspace"),
                     cls="shell"))


EDITOR_JS = r"""
import { Editor } from 'https://esm.sh/@tiptap/core@3.6.6';
import StarterKit from 'https://esm.sh/@tiptap/starter-kit@3.6.6';
import Underline from 'https://esm.sh/@tiptap/extension-underline@3.6.6';
import Link from 'https://esm.sh/@tiptap/extension-link@3.6.6';
import Image from 'https://esm.sh/@tiptap/extension-image@3.6.6';
import { Table } from 'https://esm.sh/@tiptap/extension-table@3.6.6';
import { TableRow } from 'https://esm.sh/@tiptap/extension-table-row@3.6.6';
import { TableCell } from 'https://esm.sh/@tiptap/extension-table-cell@3.6.6';
import { TableHeader } from 'https://esm.sh/@tiptap/extension-table-header@3.6.6';
const el=document.querySelector('#editor');
const blockEditor=document.querySelector('#block-editor');
const blockList=document.querySelector('#block-list');
const markdown=document.querySelector('#markdown');
const status=document.querySelector('#save-status');
const content=JSON.parse(document.querySelector('#initial-content').textContent);
const saveUrl=document.body.dataset.saveUrl;
let switching=false;
const state={mode:'rich',doc:content};
const editor=new Editor({element:el,extensions:[StarterKit.configure({underline:false,link:false}),Underline,Link.configure({openOnClick:false}),Image,Table.configure({resizable:true}),TableRow,TableCell,TableHeader],content,onUpdate:()=>{if(!switching)queueSave()}});
window.editor=editor;
document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>{const c=editor.chain().focus(); const cmd=b.dataset.cmd;
 if(cmd==='bold')c.toggleBold().run(); if(cmd==='italic')c.toggleItalic().run(); if(cmd==='underline')c.toggleUnderline().run(); if(cmd==='h2')c.toggleHeading({level:2}).run(); if(cmd==='bullet')c.toggleBulletList().run(); if(cmd==='ordered')c.toggleOrderedList().run(); if(cmd==='quote')c.toggleBlockquote().run(); if(cmd==='code')c.toggleCodeBlock().run(); if(cmd==='table')c.insertTable({rows:3,cols:3,withHeaderRow:true}).run();});
let timer,version=Number(document.body.dataset.version);
const title=document.querySelector('#skill-title'); title.addEventListener('input',queueSave);
['#meta-description','#meta-category','#meta-sublabel','#meta-author','#meta-tags','#meta-visibility'].forEach(sel=>{const node=document.querySelector(sel);if(node)node.addEventListener('input',queueSave)});
function meta(sel){const node=document.querySelector(sel);return node?node.value:''}
function queueSave(){status.textContent='Unsaved changes';clearTimeout(timer);timer=setTimeout(save,700)}

const TYPES=[['paragraph','Paragraph'],['heading1','Heading 1'],['heading2','Heading 2'],['heading3','Heading 3'],['bullet','Bulleted list'],['numbered','Numbered list'],['quote','Quote'],['code','Code'],['table','Table'],['divider','Divider'],['raw','Raw JSON']];
function make(tag,cls,text){const node=document.createElement(tag);if(cls)node.className=cls;if(text!==undefined)node.textContent=text;return node}
function escapeHtml(value){return String(value||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function inlineHtml(nodes){return (nodes||[]).map(node=>{
 if(node.type==='hardBreak')return '<br>';
 if(node.type!=='text')return inlineHtml(node.content);
 let value=escapeHtml(node.text);
 (node.marks||[]).forEach(mark=>{if(mark.type==='bold')value='<strong>'+value+'</strong>';if(mark.type==='italic')value='<em>'+value+'</em>';if(mark.type==='underline')value='<u>'+value+'</u>';if(mark.type==='strike')value='<s>'+value+'</s>';if(mark.type==='code')value='<code>'+value+'</code>';if(mark.type==='link'){const href=escapeHtml((mark.attrs||{}).href||'');value='<a href="'+href+'">'+value+'</a>'}});
 return value;
}).join('')}
function domInline(root){
 const out=[];
 function visit(node,marks){
  if(node.nodeType===Node.TEXT_NODE){if(node.nodeValue)out.push({type:'text',text:node.nodeValue,...(marks.length?{marks}: {})});return}
  if(node.nodeType!==Node.ELEMENT_NODE)return;
  if(node.tagName==='BR'){out.push({type:'hardBreak'});return}
  const next=marks.slice(),tag=node.tagName;
  if(tag==='STRONG'||tag==='B')next.push({type:'bold'});if(tag==='EM'||tag==='I')next.push({type:'italic'});if(tag==='U')next.push({type:'underline'});if(tag==='S'||tag==='STRIKE')next.push({type:'strike'});if(tag==='CODE')next.push({type:'code'});if(tag==='A')next.push({type:'link',attrs:{href:node.getAttribute('href')||''}});
  node.childNodes.forEach(child=>visit(child,next));
 }
 root.childNodes.forEach(node=>visit(node,[]));
 return out.filter(node=>node.type!=='text'||node.text.length)
}
function textContent(node){if(node.type==='text')return node.text||'';if(node.type==='hardBreak')return '\n';return (node.content||[]).map(textContent).join('')}
function nodeBlock(node){
 if(node.type==='heading')return {type:'heading'+Math.min(3,Math.max(1,Number((node.attrs||{}).level||2))),node};
 if(node.type==='bulletList')return {type:'bullet',node};if(node.type==='orderedList')return {type:'numbered',node};if(node.type==='blockquote')return {type:'quote',node};if(node.type==='codeBlock')return {type:'code',node};if(node.type==='table')return {type:'table',node};if(node.type==='horizontalRule')return {type:'divider',node};if(node.type==='paragraph')return {type:'paragraph',node};
 return {type:'raw',node};
}
function blockControls(row){
 const controls=make('div','block-controls');
 [['↑','Move up',()=>{const previous=row.previousElementSibling;if(previous)blockList.insertBefore(row,previous)}],['↓','Move down',()=>{const next=row.nextElementSibling;if(next)blockList.insertBefore(next,row)}],['＋','Add block below',()=>{const added=renderBlock({type:'paragraph',node:{type:'paragraph'}});blockList.insertBefore(added,row.nextElementSibling);added.querySelector('.block-edit').focus()}],['✕','Delete block',()=>{if(blockList.children.length>1)row.remove()}]].forEach(([label,hint,action])=>{const button=make('button','block-control',label);button.type='button';button.title=hint;button.onclick=()=>{action();queueSave()};controls.appendChild(button)});
 return controls;
}
function blockFormat(row){
 const toolbar=make('div','block-format');
 [['B','bold','Bold'],['I','italic','Italic'],['U','underline','Underline'],['</>','code','Inline code']].forEach(([label,command,hint])=>{const button=make('button','',label);button.type='button';button.title=hint;button.onmousedown=event=>{const edit=row.querySelector('.block-edit'),selection=window.getSelection();button._range=selection?.rangeCount&&edit?.contains(selection.anchorNode)?selection.getRangeAt(0).cloneRange():null;event.preventDefault()};button.onclick=()=>{const edit=row.querySelector('.block-edit');if(!edit)return;const selection=window.getSelection();if(button._range){selection.removeAllRanges();selection.addRange(button._range)}else edit.focus();if(command==='code'){const selected=button._range?selection.toString():'code';document.execCommand('insertHTML',false,'<code>'+escapeHtml(selected||'code')+'</code>')}else document.execCommand(command,false,null);button._range=null;queueSave()};toolbar.appendChild(button)});
 return toolbar;
}
function tableEditor(node){
 const wrap=make('div');const table=make('table','block-table');
 const sourceRows=(node.content||[]).length?node.content:[{type:'tableRow',content:[{type:'tableHeader',content:[{type:'paragraph'}]}]},{type:'tableRow',content:[{type:'tableCell',content:[{type:'paragraph'}]}]}];
 sourceRows.forEach(sourceRow=>{const tr=make('tr');(sourceRow.content||[]).forEach(cell=>{const td=make(cell.type==='tableHeader'?'th':'td');td.contentEditable='true';td.dataset.cellType=cell.type||'tableCell';td.innerHTML=inlineHtml(((cell.content||[])[0]||{}).content)||'<br>';tr.appendChild(td)});table.appendChild(tr)});wrap.appendChild(table);
 const tools=make('div','block-table-tools');
 function button(label,action){const item=make('button','block-control',label);item.type='button';item.onclick=()=>{action();queueSave()};tools.appendChild(item)}
 button('＋ Row',()=>{const columns=table.rows[0]?.cells.length||1;const tr=make('tr');for(let i=0;i<columns;i++){const td=make('td');td.contentEditable='true';td.dataset.cellType='tableCell';td.innerHTML='<br>';tr.appendChild(td)}table.appendChild(tr)});
 button('＋ Column',()=>Array.from(table.rows).forEach((tr,index)=>{const cell=make(index===0?'th':'td');cell.contentEditable='true';cell.dataset.cellType=index===0?'tableHeader':'tableCell';cell.innerHTML='<br>';tr.appendChild(cell)}));
 button('－ Row',()=>{if(table.rows.length>1)table.deleteRow(-1)});wrap.appendChild(tools);return wrap;
}
function fillBlock(row,block){
 const body=row.querySelector('.block-body');body.replaceChildren();row.dataset.type=block.type;row.querySelector('.block-type').value=block.type;row.querySelector('.block-format').hidden=['code','raw','table','divider'].includes(block.type);
 if(block.type==='divider'){body.appendChild(document.createElement('hr'));return}
 if(block.type==='table'){body.appendChild(tableEditor(block.node||{}));return}
 if(block.type==='code'||block.type==='raw'){const raw=make('textarea','block-raw');raw.rows=block.type==='code'?5:8;raw.value=block.type==='raw'?JSON.stringify(block.node||{type:'paragraph'},null,2):textContent(block.node||{});body.appendChild(raw);return}
 const edit=make('div','block-edit '+block.type);edit.contentEditable='true';
 if(block.type==='bullet'||block.type==='numbered'){
  const items=(block.node?.content||[]);(items.length?items:[{content:[{type:'paragraph'}]}]).forEach(item=>{const line=make('div');const paragraph=(item.content||[]).find(child=>child.type==='paragraph')||{};line.innerHTML=inlineHtml(paragraph.content)||'<br>';edit.appendChild(line)});
 }else if(block.type==='quote'){
  const paragraph=(block.node?.content||[]).find(child=>child.type==='paragraph')||{};edit.innerHTML=inlineHtml(paragraph.content)||'<br>';
 }else edit.innerHTML=inlineHtml(block.node?.content)||'<br>';
 body.appendChild(edit);
}
function renderBlock(block){
 const row=make('div','block-row');const select=make('select','block-type');TYPES.forEach(([value,label])=>{const option=make('option','',label);option.value=value;select.appendChild(option)});const body=make('div','block-body');row.append(blockFormat(row),select,body,blockControls(row));fillBlock(row,block);
 select.onchange=()=>{const value=rowText(row);fillBlock(row,{type:select.value,node:valueNode(select.value,value)});queueSave()};return row;
}
function rowText(row){const edit=row.querySelector('.block-edit');const raw=row.querySelector('.block-raw');return raw?raw.value:(edit?edit.innerText:'')}
function valueNode(type,value){const inline=value?[{type:'text',text:value}]:undefined;if(type.startsWith('heading'))return {type:'heading',attrs:{level:Number(type.slice(-1))},...(inline?{content:inline}:{})};if(type==='quote')return {type:'blockquote',content:[{type:'paragraph',...(inline?{content:inline}:{})}]};if(type==='code')return {type:'codeBlock',...(inline?{content:inline}:{})};if(type==='divider')return {type:'horizontalRule'};if(type==='table')return {type:'table'};if(type==='raw'){try{return JSON.parse(value)}catch{return {type:'paragraph',...(inline?{content:inline}:{})}}}return {type:'paragraph',...(inline?{content:inline}:{})}}
function blockNode(row){
 const type=row.dataset.type;
 if(type==='divider')return {type:'horizontalRule'};
 if(type==='raw'){try{return JSON.parse(row.querySelector('.block-raw').value)}catch{return {type:'paragraph',content:[{type:'text',text:row.querySelector('.block-raw').value}]}}}
 if(type==='code'){const value=row.querySelector('.block-raw').value;return {type:'codeBlock',...(value?{content:[{type:'text',text:value}]}:{})}}
 if(type==='table'){const rows=Array.from(row.querySelectorAll('.block-table tr')).map(tr=>({type:'tableRow',content:Array.from(tr.cells).map(cell=>({type:cell.dataset.cellType||'tableCell',content:[{type:'paragraph',...(domInline(cell).length?{content:domInline(cell)}:{})}]}))}));return {type:'table',content:rows}}
 const edit=row.querySelector('.block-edit');
 if(type==='bullet'||type==='numbered'){const source=edit.children.length?Array.from(edit.children):[edit];return {type:type==='bullet'?'bulletList':'orderedList',content:source.map(item=>({type:'listItem',content:[{type:'paragraph',...(domInline(item).length?{content:domInline(item)}:{})}]}))}}
 const content=domInline(edit);if(type==='quote')return {type:'blockquote',content:[{type:'paragraph',...(content.length?{content}:{})}]};if(type.startsWith('heading'))return {type:'heading',attrs:{level:Number(type.slice(-1))},...(content.length?{content}:{})};return {type:'paragraph',...(content.length?{content}:{})};
}
function renderBlocks(doc){blockList.replaceChildren();(doc.content||[]).forEach(node=>blockList.appendChild(renderBlock(nodeBlock(node))));if(!blockList.children.length)blockList.appendChild(renderBlock({type:'paragraph',node:{type:'paragraph'}}))}
function blocksDoc(){return {type:'doc',content:Array.from(blockList.children).map(blockNode)}}
function inlineMarkdown(nodes){return (nodes||[]).map(node=>{if(node.type==='hardBreak')return '  \n';if(node.type!=='text')return inlineMarkdown(node.content);let value=node.text||'';(node.marks||[]).forEach(mark=>{if(mark.type==='bold')value='**'+value+'**';if(mark.type==='italic')value='*'+value+'*';if(mark.type==='strike')value='~~'+value+'~~';if(mark.type==='code')value='`'+value+'`';if(mark.type==='link')value='['+value+']('+((mark.attrs||{}).href||'')+')'});return value}).join('')}
function docMarkdown(doc){
 function nodeMd(node){if(node.type==='paragraph')return inlineMarkdown(node.content);if(node.type==='heading')return '#'.repeat(Number((node.attrs||{}).level||2))+' '+inlineMarkdown(node.content);if(node.type==='horizontalRule')return '---';if(node.type==='codeBlock')return '```\n'+textContent(node)+'\n```';if(node.type==='blockquote')return (node.content||[]).map(nodeMd).join('\n').split('\n').map(line=>'> '+line).join('\n');if(node.type==='bulletList'||node.type==='orderedList')return (node.content||[]).map((item,index)=>(node.type==='bulletList'?'- ':(index+1)+'. ')+(item.content||[]).map(nodeMd).join(' ')).join('\n');if(node.type==='table')return (node.content||[]).map((row,index)=>{const line='| '+(row.content||[]).map(cell=>textContent(cell).replace(/\|/g,'\\|')).join(' | ')+' |';return index===0?line+'\n| '+(row.content||[]).map(()=> '---').join(' | ')+' |':line}).join('\n');return textContent(node)}
 return (doc.content||[]).map(nodeMd).join('\n\n').replace(/\n{3,}/g,'\n\n').trim();
}
function inlineFromMarkdown(value){
 const nodes=[],pattern=/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))/g;let at=0,match;
 function text(value,marks){if(value)nodes.push({type:'text',text:value,...(marks?{marks}: {})})}
 while((match=pattern.exec(value))){text(value.slice(at,match.index));const token=match[0];if(token.startsWith('**'))text(token.slice(2,-2),[{type:'bold'}]);else if(token.startsWith('*'))text(token.slice(1,-1),[{type:'italic'}]);else if(token.startsWith('`'))text(token.slice(1,-1),[{type:'code'}]);else{const link=token.match(/^\[([^\]]+)\]\(([^)]+)\)$/);text(link[1],[{type:'link',attrs:{href:link[2]}}])}at=pattern.lastIndex}
 text(value.slice(at));return nodes;
}
function markdownDoc(value){
 const lines=String(value||'').replace(/\r\n/g,'\n').split('\n'),nodes=[];let i=0;
 while(i<lines.length){const line=lines[i];if(!line.trim()){i++;continue}if(/^```/.test(line)){const body=[];i++;while(i<lines.length&&!/^```/.test(lines[i]))body.push(lines[i++]);if(i<lines.length)i++;nodes.push({type:'codeBlock',...(body.length?{content:[{type:'text',text:body.join('\n')}]}:{})});continue}const heading=line.match(/^(#{1,3})\s+(.*)$/);if(heading){nodes.push({type:'heading',attrs:{level:heading[1].length},content:inlineFromMarkdown(heading[2])});i++;continue}if(/^\s*>\s?/.test(line)){const body=[];while(i<lines.length&&/^\s*>\s?/.test(lines[i]))body.push(lines[i++].replace(/^\s*>\s?/,''));nodes.push({type:'blockquote',content:[{type:'paragraph',content:inlineFromMarkdown(body.join(' '))}]});continue}if(/^\s*[-*+]\s+/.test(line)||/^\s*\d+[.)]\s+/.test(line)){const ordered=/^\s*\d/.test(line),items=[];const matcher=ordered?/^\s*\d+[.)]\s+/:/^\s*[-*+]\s+/;while(i<lines.length&&matcher.test(lines[i]))items.push({type:'listItem',content:[{type:'paragraph',content:inlineFromMarkdown(lines[i++].replace(matcher,''))}]});nodes.push({type:ordered?'orderedList':'bulletList',content:items});continue}if(/^\s*\|.*\|\s*$/.test(line)){const tableLines=[];while(i<lines.length&&/^\s*\|.*\|\s*$/.test(lines[i]))tableLines.push(lines[i++]);const rows=tableLines.filter((row,index)=>index!==1||!/^\s*\|?\s*:?-+/.test(row)).map((row,index)=>({type:'tableRow',content:row.trim().replace(/^\||\|$/g,'').split('|').map(value=>({type:index===0?'tableHeader':'tableCell',content:[{type:'paragraph',content:inlineFromMarkdown(value.trim())}]}))}));nodes.push({type:'table',content:rows});continue}if(/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)){nodes.push({type:'horizontalRule'});i++;continue}const paragraph=[];while(i<lines.length&&lines[i].trim()&&!/^(#{1,3}\s|```|\s*>\s?|\s*[-*+]\s+|\s*\d+[.)]\s+|\s*\|.*\|\s*$|\s*(-{3,}|\*{3,}|_{3,})\s*$)/.test(lines[i]))paragraph.push(lines[i++]);nodes.push({type:'paragraph',content:inlineFromMarkdown(paragraph.join(' '))})}
 return {type:'doc',content:nodes.length?nodes:[{type:'paragraph'}]};
}
function readMode(){if(state.mode==='rich')state.doc=editor.getJSON();else if(state.mode==='block')state.doc=blocksDoc();else state.doc=markdownDoc(markdown.value)}
function setMode(mode){
 if(mode!==state.mode)readMode();state.mode=mode;el.hidden=mode!=='rich';blockEditor.hidden=mode!=='block';markdown.hidden=mode!=='markdown';
 switching=true;if(mode==='rich')editor.commands.setContent(state.doc,{emitUpdate:false});if(mode==='block')renderBlocks(state.doc);if(mode==='markdown')markdown.value=docMarkdown(state.doc);switching=false;
 document.querySelectorAll('[data-mode]').forEach(button=>{button.classList.toggle('active',button.dataset.mode===mode);button.setAttribute('aria-pressed',button.dataset.mode===mode?'true':'false')});document.querySelectorAll('[data-rich-tool]').forEach(button=>button.hidden=mode!=='rich');
}
async function save(){clearTimeout(timer);readMode();status.textContent='Saving…';const markdownValue=state.mode==='markdown'?markdown.value:docMarkdown(state.doc);const res=await fetch(saveUrl,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:title.value,content_json:JSON.stringify(state.doc),markdown:markdownValue,version,description:meta('#meta-description'),category:meta('#meta-category'),sub_label:meta('#meta-sublabel'),author_label:meta('#meta-author'),tags:meta('#meta-tags'),visibility:meta('#meta-visibility')})});const out=await res.json();if(res.status===409){status.textContent='Newer version exists — reload';return false}if(res.ok){version=out.version;document.body.dataset.version=version;status.textContent='Saved';return true}status.textContent=out.error||'Save failed';return false}
document.querySelectorAll('[data-mode]').forEach(button=>button.onclick=()=>setMode(button.dataset.mode));
blockEditor.addEventListener('input',queueSave);markdown.addEventListener('input',queueSave);
document.querySelector('#add-block').onclick=()=>{const added=renderBlock({type:'paragraph',node:{type:'paragraph'}});blockList.appendChild(added);added.querySelector('.block-edit').focus();queueSave()};
setMode('rich');
"""


def editor_page(who, item):
    tools = [("B", "bold"), ("I", "italic"), ("U", "underline"), ("H2", "h2"),
             ("• List", "bullet"), ("1. List", "ordered"), ("❝", "quote"),
             ("</>", "code"), ("Table", "table")]
    next_status = "published" if item["status"] == "draft" else "draft"
    status_button = "Publish" if item["status"] == "draft" else "Unpublish"
    topbar = Div(
        Span(f"Editing · {item['category']}", cls="status"),
        Div(Span("Saved", id="save-status", cls="status"),
            A("View", href=f"/skills/{item['id']}", cls="btn ghost sm"),
            A(f"History · v{item['version']}", href=f"/skills/{item['id']}/versions", cls="btn ghost sm"),
            A("Download", href=f"/skills/{item['id']}/download", cls="btn ghost sm"),
            Form(Input(type="hidden", name="status", value=next_status),
                 Button(status_button, cls="btn sm"),
                 method="post", action=f"/skills/{item['id']}/status", cls="inlineform"),
            cls="pageactions"),
        cls="topbar")
    meta = Div(
        Div(Label("Category"),
            Select(*[Option(c, value=c, selected=(c == item["category"])) for c in CATEGORIES],
                   id="meta-category", name="category"), cls="metafield"),
        Div(Label("Sub-label"),
            Input(id="meta-sublabel", name="sub_label", value=item.get("sub_label") or "",
                  placeholder="e.g. Family Office", list="sublabel-options"),
            Datalist(*[Option(s) for s in SUBLABELS.get(item["category"], [])], id="sublabel-options"),
            cls="metafield"),
        Div(Label("Author label"),
            Input(id="meta-author", name="author_label", value=item.get("author_label") or "",
                  placeholder="e.g. Predictive Labs"), cls="metafield"),
        Div(Label("Tags (comma-separated)"),
            Input(id="meta-tags", name="tags", value=item.get("tags") or "",
                  placeholder="research, diligence"), cls="metafield"),
        Div(Label("Visibility"),
            Select(Option("Public", value="public", selected=(item["visibility"] == "public")),
                   Option("Private", value="private", selected=(item["visibility"] == "private")),
                   id="meta-visibility", name="visibility"), cls="metafield"),
        Div(Label("Short description (shown on the card)"),
            Textarea(item.get("description") or "", id="meta-description", name="description",
                     placeholder="One line describing what this skill does."),
            cls="metafield full"),
        cls="metagrid")
    body = Div(
        Div(*[value for pair in [(A("My Skills", href="/mine"), Span("/"))] for value in pair],
            Span(item["category"]),
            Span(item["status"].title(), cls="pagebadge " + item["status"]),
            Span(item["visibility"].title(), cls="pagebadge " + item["visibility"]),
            cls="breadcrumbs"),
        Input(value=item["title"], id="skill-title", cls="titleinput", aria_label="Skill title"),
        meta,
        Div(*[Button(label, type="button", data_cmd=cmd, data_rich_tool="true", cls="tool")
              for label, cmd in tools],
            Span(cls="toolbar-spacer"),
            Button("Rich", type="button", data_mode="rich", aria_pressed="true", cls="tool mode active"),
            Button("Blocks", type="button", data_mode="block", aria_pressed="false", cls="tool mode"),
            Button("Markdown", type="button", data_mode="markdown", aria_pressed="false", cls="tool mode"),
            cls="toolbar"),
        Div(id="editor", cls="editor"),
        Div(Button("＋ Add block", id="add-block", type="button", cls="btn ghost block-actions"),
            Div(id="block-list", cls="block-list"), id="block-editor", cls="block-editor", hidden=True),
        Textarea(item["markdown"], id="markdown", cls="markdown-editor", hidden=True, aria_label="Markdown editor"),
        Script(item["content_json"], type="application/json", id="initial-content"),
        Div(Form(Button("Delete skill", cls="btn ghost"),
                 method="post", action=f"/skills/{item['id']}/trash",
                 onsubmit="return confirm('Delete this skill?')"),
            style="margin-top:44px"),
        cls="editorwrap")
    return Html(
        head(item["title"] + " · FastSkills"),
        Body(_sidebar(who, "mine"),
             Main(topbar, body, cls="workspace"),
             Script(EDITOR_JS, type="module"),
             cls="shell",
             data_version=str(item["version"]),
             data_save_url=f"/skills/{item['id']}/save"))
