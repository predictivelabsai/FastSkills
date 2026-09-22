# FastSkills

An open, searchable catalog of Claude/agent **skills** — browse and filter by
category, contribute your own, and keep each skill public (default) or private.
Part of the open-source [FastSME](https://fastsme.com) suite.

Categories: **Finance · Trading · Legal · Marketing** (no leaderboard).

## Stack

- [FastHTML](https://fastht.ml) (Starlette/Uvicorn), server-rendered Python UI
- **PostgreSQL** (default) or **SQLite** via a `DB_TYPE` toggle
- FastWiki-style Tiptap editor (rich / block / Markdown, autosave, version history,
  optimistic-locking 409 conflicts)
- Google SSO (Authlib OIDC) + local email/password accounts
- FastAPI read-only sub-app mounted at `/api` (`/api/docs`)

## Run locally

```bash
uv pip install -r requirements.txt

# Option A — SQLite (no external DB)
DB_TYPE=sqlite FASTSKILLS_DB=data/fastskills.sqlite python app.py

# Option B — PostgreSQL (reads .env)
python app.py            # DB_TYPE=postgresql is the default
```

Open http://localhost:5024. In development, `/auth/dev` signs you in without SSO.

## Configuration (`.env`)

| Variable | Purpose |
|---|---|
| `DB_TYPE` | `postgresql` (default) or `sqlite` |
| `DATABASE_URL` / `DATABASE_URL_PROD` | Postgres DSN (`postgres://` accepted); the second is a fallback |
| `DB_SCHEMA` | Postgres schema, default `fast_skills` (auto-created) |
| `FASTSKILLS_DB` | SQLite path (when `DB_TYPE=sqlite`) |
| `FASTSKILLS_SECRET` | Session signing secret |
| `FASTSKILLS_PORT` | Port, default `5024` |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Enable the Google SSO button |
| `GOOGLE_ALLOWED_DOMAINS` | Optional comma-separated email-domain allow-list |
| `POSTMARK_API_TOKEN` / `FROM_EMAIL` | Enable local-account verify/reset emails |

See `.env.coolify.sample`. Never commit real secrets — `.env` is gitignored.

## Skill catalog seeding

The catalog is seeded from the committed `seed/` tree at startup (idempotent; a skill
a user has taken over is never overwritten). Each seed file is Markdown with normalized
frontmatter (`title`, `description`, `category`, `author`, `tags`, `license`, `source`).

Regenerate the imported skills from their upstream sources:

```bash
python scripts/build_seed.py     # clones external repos, copies internal SKILL.md
```

Sources & attribution:

- **Marketing** — [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) (MIT), author *Corey Haines*
- **Legal** — [LegalQuants/lq-skills](https://github.com/LegalQuants/lq-skills) (Apache-2.0), author *LegalQuants*
- **Trading** — AlpaTrade domain skills, author *Predictive Labs*
- **Finance** — FastPE `sector-taxonomy` plus skills authored from FastFund / LiquidRound /
  FastPE / FastVC capabilities, author *Predictive Labs*

## Deploy (Coolify)

Single-service Docker with a persistent `fastskills-data` volume; deploys from `main` to
`fastskills.org`.

```bash
python scripts/coolify.py status
python scripts/coolify.py env --sync --yes
python scripts/coolify.py deploy --yes
```

Add a `/health` check (already provided). Set the env vars above in Coolify.

## Google SSO — final step

Register the OAuth client in Google Cloud Console → **APIs & Services → Credentials**:

- Authorized redirect URI: `https://fastskills.org/auth/callback`
- Scopes: `openid email profile`

Put the client id/secret into the deployment env (`GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`).
The Google button appears automatically once both are set.
