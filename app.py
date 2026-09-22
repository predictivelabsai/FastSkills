from __future__ import annotations
import os, re, secrets
from urllib.parse import quote

import markdown as _md
from dotenv import load_dotenv
from fasthtml.common import *
from starlette.responses import JSONResponse, RedirectResponse, Response

load_dotenv()
from fastskills import account_auth, db, seed, views
from fastskills.api import api
from fastskills.version import RELEASE_DATE, VERSION

app, rt = fast_app(secret_key=os.getenv("FASTSKILLS_SECRET", secrets.token_hex(32)))
app.mount("/api", api)

# Seed the catalog from the committed seed/ tree (idempotent).
try:
    seed.run()
except Exception as exc:  # never let seeding block startup
    print(f"[seed] skipped: {exc}")


def who(session):
    return session.get("identity")


def guard(session):
    return who(session) or RedirectResponse("/", status_code=303)


def establish_identity(session, email, name=""):
    email = (email or "").strip().lower()
    identity = {"sub": email, "email": email, "name": name or email.split("@")[0]}
    db.provision(identity)
    session["identity"] = identity


def render_markdown(text):
    return _md.markdown(text or "", extensions=["fenced_code", "tables", "sane_lists"])


# ── catalog ──────────────────────────────────────────────────────────────────
@rt("/")
def get(session, q: str = "", category: str = ""):
    identity = who(session)
    category = category if category in db.CATEGORIES else None
    items = db.catalog(category, q.strip() or None)
    counts = db.category_counts()
    total = sum(counts.values())
    return views.catalog_page(identity, items, counts, category, q.strip(), total)


@rt("/mine")
def get(session):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    return views.mine_page(identity, db.mine(identity))


@rt("/skills/new")
def get(session):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    sid = db.create_skill(identity)
    return RedirectResponse(f"/skills/{sid}/edit", status_code=303)


@rt("/skills/{sid:int}")
def get(session, sid: int):
    identity = who(session)
    item = db.visible_skill(identity, sid)
    if not item:
        return Response("Skill not found", status_code=404)
    return views.detail_page(identity, item, render_markdown(item["markdown"]))


@rt("/skills/{sid:int}/download")
def get(session, sid: int):
    identity = who(session)
    item = db.visible_skill(identity, sid)
    if not item:
        return Response("Skill not found", status_code=404)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", item["slug"]).strip("-.") or "skill"
    front = (f"---\ntitle: {item['title']}\ndescription: {item['description']}\n"
             f"category: {item['category']}\nauthor: {item['author_label']}\n"
             f"tags: {item['tags']}\n")
    if item["license"]:
        front += f"license: {item['license']}\n"
    if item["source_url"]:
        front += f"source: {item['source_url']}\n"
    front += "---\n\n"
    body = front + (item["markdown"] or "")
    return Response(body, media_type="text/markdown",
                    headers={"Content-Disposition": f'attachment; filename="{safe}.md"'})


@rt("/skills/{sid:int}/edit")
def get(session, sid: int):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    item = db.skill(sid)
    if not db.can_edit(identity, item):
        return Response("Not found", status_code=404)
    return views.editor_page(identity, item)


@rt("/skills/{sid:int}/save")
async def post(request, session, sid: int):
    identity = who(session)
    if not identity:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    body = await request.json()
    try:
        result = db.save_skill(
            identity, sid,
            title=body.get("title", "Untitled skill"),
            content_json=body.get("content_json", "{}"),
            markdown=body.get("markdown", ""),
            version=int(body.get("version", 0)),
            description=body.get("description"),
            category=body.get("category"),
            author_label=body.get("author_label"),
            tags=body.get("tags"),
            visibility=body.get("visibility"))
    except (ValueError, TypeError):
        return JSONResponse({"error": "invalid content"}, status_code=422)
    if not result:
        return JSONResponse({"error": "not found"}, status_code=404)
    if result.get("conflict"):
        return JSONResponse(result, status_code=409)
    return JSONResponse({"id": sid, "version": result["version"]})


@rt("/skills/{sid:int}/status")
def post(session, sid: int, status: str):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    try:
        db.set_status(identity, sid, status)
    except ValueError:
        return Response("Invalid status", status_code=422)
    return RedirectResponse(f"/skills/{sid}/edit", status_code=303)


@rt("/skills/{sid:int}/visibility")
def post(session, sid: int, visibility: str):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    try:
        db.set_visibility(identity, sid, visibility)
    except ValueError:
        return Response("Invalid visibility", status_code=422)
    return RedirectResponse(f"/skills/{sid}/edit", status_code=303)


@rt("/skills/{sid:int}/trash")
def post(session, sid: int):
    identity = guard(session)
    if isinstance(identity, RedirectResponse):
        return identity
    db.trash(identity, sid)
    return RedirectResponse("/mine", status_code=303)


# ── local accounts (email/password) ──────────────────────────────────────────
def _on_local_login(session, account):
    establish_identity(session, account["email"], account.get("name") or "")


account_auth.register_fasthtml_routes(rt, app_name="FastSkills", success_path="/mine",
                                      on_login=_on_local_login)


# ── Google OAuth (optional — enabled when client id + secret are set) ─────────
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_ALLOWED_DOMAINS = [d.strip().lower() for d in
                          os.environ.get("GOOGLE_ALLOWED_DOMAINS", "").split(",") if d.strip()]
OAUTH_ENABLED = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)
_oauth = None
if OAUTH_ENABLED:
    from authlib.integrations.starlette_client import OAuth as _AuthlibOAuth
    _oauth = _AuthlibOAuth()
    _oauth.register(
        name="google", client_id=GOOGLE_CLIENT_ID, client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"})


if OAUTH_ENABLED:
    def _redirect_uri(request):
        scheme = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("host", request.url.netloc)
        return f"{scheme}://{host}/auth/callback"

    @rt("/auth/google", methods=["GET"])
    async def google_login(request):
        return await _oauth.google.authorize_redirect(request, _redirect_uri(request))

    @rt("/auth/callback", methods=["GET"])
    async def google_callback(request, sess):
        try:
            token = await _oauth.google.authorize_access_token(request)
        except Exception:
            return RedirectResponse("/?auth=google-failed", status_code=303)
        info = token.get("userinfo") or {}
        email = (info.get("email") or "").strip().lower()
        if not email or not info.get("email_verified", True):
            return RedirectResponse("/?auth=unverified", status_code=303)
        if (GOOGLE_ALLOWED_DOMAINS and email.split("@")[-1] not in GOOGLE_ALLOWED_DOMAINS
                and not db.get_user(email)):
            return RedirectResponse("/?auth=not-permitted", status_code=303)
        account_auth.accounts.link_google(email, info.get("name") or email)
        establish_identity(sess, email, info.get("name") or "")
        return RedirectResponse("/mine", status_code=303)
else:
    @rt("/auth/google", methods=["GET"])
    def google_disabled():
        return RedirectResponse("/?auth=google-disabled", status_code=303)


@rt("/auth/dev")
def get(session, email: str = "kaljuvee@gmail.com"):
    if os.getenv("FASTSKILLS_ENV", "development") == "production":
        return RedirectResponse("/", status_code=303)
    establish_identity(session, email, "Julian Kaljuvee")
    return RedirectResponse("/mine", status_code=303)


@rt("/logout")
def get(session):
    session.clear()
    return RedirectResponse("/", status_code=303)


# ── infra ────────────────────────────────────────────────────────────────────
@rt("/health")
def get():
    return JSONResponse({"status": "ok", "product": "FastSkills", "version": VERSION,
                         "release_date": RELEASE_DATE})


@rt("/favicon.ico")
def get():
    return Response(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
        '<rect width="64" height="64" rx="16" fill="#7c3aed"/>'
        '<path fill="white" d="M40 22c-2-3-5-4.5-9-4.5-6 0-10 3.4-10 8.2 0 4.3 3 6.6 8.6 8 '
        '4.4 1.1 5.8 1.9 5.8 3.7 0 1.8-1.7 3-4.6 3-3.2 0-5.3-1.4-6.6-3.9l-5.2 3c1.9 3.9 5.9 6 '
        '11.7 6 6.6 0 10.9-3.3 10.9-8.5 0-4.6-3.1-6.8-9-8.2-4.2-1-5.4-1.7-5.4-3.4 0-1.6 1.4-2.7 '
        '3.9-2.7 2.7 0 4.4 1.1 5.5 3.1z"/></svg>', media_type="image/svg+xml")


@rt("/openapi.json")
def get():
    return JSONResponse(api.openapi())


@rt("/developers")
def get():
    return RedirectResponse("/api/docs", status_code=307)


if __name__ == "__main__":
    serve(port=int(os.getenv("FASTSKILLS_PORT", "5024")))
